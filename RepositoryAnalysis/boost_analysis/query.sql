-- 1) Detect repos that contain boost/ folder (vendored Boost)
WITH
    vendored_boost AS (
        SELECT DISTINCT
            repo_name
        FROM
            `bigquery-public-data.github_repos.files`
        WHERE
            REGEXP_CONTAINS (path, r '(^|/)boost/')
    ),

-- 2) get files containing Boost includes
boost_files AS (
    SELECT *
    FROM (
            SELECT
                f.repo_name, f.ref, f.path, f.mode, f.id, f.symlink_target, c.size AS file_size_bytes, COALESCE(
                    SAFE_CONVERT_BYTES_TO_STRING (SAFE.FROM_BASE64 (c.content)), c.content
                ) AS content_text
            FROM
                `bigquery-public-data.github_repos.contents` c
                JOIN `bigquery-public-data.github_repos.files` f ON c.id = f.id
            WHERE
                c.binary = FALSE
                AND c.content IS NOT NULL
                AND LENGTH(c.content) > 0
                AND (
                    ENDS_WITH (f.path, '.cpp')
                    OR ENDS_WITH (f.path, '.cxx')
                    OR ENDS_WITH (f.path, '.cc')
                    OR ENDS_WITH (f.path, '.hpp')
                    OR ENDS_WITH (f.path, '.hxx')
                    OR ENDS_WITH (f.path, '.hh')
                    OR ENDS_WITH (f.path, '.c')
                    OR ENDS_WITH (f.path, '.h')
                )
        )
    WHERE
        REGEXP_CONTAINS (
            content_text,
            r '(?i)#\s*include\s*["<]\s*boost/'
        )
),

-- 3) Latest commit metadata per repo
latest_commits AS (
    SELECT
        repo AS repo_name,
        MAX(
            TIMESTAMP_SECONDS (c.committer.time_sec)
        ) AS last_commit_ts,
        ANY_VALUE (c.commit) AS commit_sha,
        ANY_VALUE (c.tree) AS tree_sha,
        ANY_VALUE (c.parent) AS parent_commits,
        ANY_VALUE (c.author) AS author_info,
        ANY_VALUE (c.committer) AS committer_info,
        ANY_VALUE (c.subject) AS subject,
        ANY_VALUE (c.message) AS message
    FROM (
            SELECT c.*
            EXCEPT
            (
                trailer, difference, difference_truncated, encoding
            ), c.repo_name AS repo_list
            FROM
                `bigquery-public-data.github_repos.commits` c
        ) c
        CROSS JOIN UNNEST (c.repo_list) AS repo
    GROUP BY
        repo
),

/* -------------------------------------------------------------
BOOST VERSION DETECTION
--------------------------------------------------------------*/

-- 4A) Version from vendored boost/version.hpp
boost_versions_vendored AS (
    SELECT
        f.repo_name,
        REGEXP_EXTRACT (
            COALESCE(
                SAFE_CONVERT_BYTES_TO_STRING (SAFE.FROM_BASE64 (c.content)),
                c.content
            ),
            r '#define\s+BOOST_VERSION\s+(\d{6})'
        ) AS boost_version_num
    FROM
        `bigquery-public-data.github_repos.files` f
        JOIN `bigquery-public-data.github_repos.contents` c ON f.id = c.id
    WHERE
        f.path = 'boost/version.hpp'
),

-- Convert numeric version into semantic version
boost_versions_vendored_clean AS (
    SELECT
        repo_name,
        SAFE_CAST (boost_version_num AS INT64) AS version_num,
        CONCAT (
            CAST(
                CAST(
                    SAFE_CAST (boost_version_num AS INT64) / 100000 AS INT64
                ) AS STRING
            ),
            '.',
            CAST(
                MOD(
                    CAST(
                        SAFE_CAST (boost_version_num AS INT64) / 100 AS INT64
                    ),
                    1000
                ) AS STRING
            ),
            '.',
            CAST(
                MOD(
                    SAFE_CAST (boost_version_num AS INT64),
                    100
                ) AS STRING
            )
        ) AS semantic_version
    FROM boost_versions_vendored
    WHERE
        boost_version_num IS NOT NULL
),

-- 4B) Version from CMake find_package(Boost 1.70)
boost_versions_cmake AS (
    SELECT f.repo_name, REGEXP_EXTRACT (
            COALESCE(
                SAFE_CONVERT_BYTES_TO_STRING (SAFE.FROM_BASE64 (c.content)), c.content
            ), r 'Boost\s+(\d+\.\d+(?:\.\d+)?)'
        ) AS version
    FROM
        `bigquery-public-data.github_repos.files` f
        JOIN `bigquery-public-data.github_repos.contents` c ON f.id = c.id
    WHERE
        ENDS_WITH (f.path, 'CMakeLists.txt')
        AND REGEXP_CONTAINS (
            COALESCE(
                SAFE_CONVERT_BYTES_TO_STRING (SAFE.FROM_BASE64 (c.content)),
                c.content
            ),
            r 'find_package\s*\(\s*Boost'
        )
),

-- 4C) Conan reference: boost/1.76.0
boost_versions_conan AS (
    SELECT f.repo_name, REGEXP_EXTRACT (
            COALESCE(
                SAFE_CONVERT_BYTES_TO_STRING (SAFE.FROM_BASE64 (c.content)), c.content
            ), r 'boost/(\d+\.\d+\.\d+)'
        ) AS version
    FROM
        `bigquery-public-data.github_repos.files` f
        JOIN `bigquery-public-data.github_repos.contents` c ON f.id = c.id
    WHERE
        f.path LIKE '%conanfile%'
),

-- 4D) vcpkg.json version
boost_versions_vcpkg AS (
    SELECT f.repo_name, REGEXP_EXTRACT (
            COALESCE(
                SAFE_CONVERT_BYTES_TO_STRING (SAFE.FROM_BASE64 (c.content)), c.content
            ), r '"boost[^"]*"\s*:\s*"([^"]+)"'
        ) AS version
    FROM
        `bigquery-public-data.github_repos.files` f
        JOIN `bigquery-public-data.github_repos.contents` c ON f.id = c.id
    WHERE
        f.path LIKE '%vcpkg.json%'
),

-- Merge all version sources
all_boost_versions AS (
    SELECT
        repo_name,
        semantic_version AS version
    FROM boost_versions_vendored_clean
    UNION ALL
    SELECT repo_name, version
    FROM boost_versions_cmake
    WHERE
        version IS NOT NULL
    UNION ALL
    SELECT repo_name, version
    FROM boost_versions_conan
    WHERE
        version IS NOT NULL
    UNION ALL
    SELECT repo_name, version
    FROM boost_versions_vcpkg
    WHERE
        version IS NOT NULL
),

-- Best available version per repo
boost_version_final AS (
    SELECT
        repo_name,
        ANY_VALUE (version) AS boost_version
    FROM all_boost_versions
    GROUP BY
        repo_name
)

---------------------------------------------------------------
-- FINAL OUTPUT JOIN
---------------------------------------------------------------

SELECT
    b.repo_name,
    CONCAT (
        'https://github.com/',
        b.repo_name
    ) AS repo_url,
    bv.boost_version,
    b.ref,
    b.path,
    b.mode,
    b.id,
    b.symlink_target,
    b.file_size_bytes,
    b.content_text AS file_content,
    lc.last_commit_ts,
    lc.commit_sha,
    lc.tree_sha,
    lc.parent_commits,
    lc.author_info,
    lc.committer_info,
    lc.subject,
    lc.message,
    CASE
        WHEN v.repo_name IS NOT NULL THEN TRUE
        ELSE FALSE
    END AS contains_vendored_boost,
    CASE
        WHEN v.repo_name IS NOT NULL THEN 'NOT AFFECTED (vendored boost)'
        ELSE 'AFFECTED (uses system boost)'
    END AS boost_update_impact
FROM
    boost_files b
    LEFT JOIN latest_commits lc ON b.repo_name = lc.repo_name
    LEFT JOIN vendored_boost v ON b.repo_name = v.repo_name
    LEFT JOIN boost_version_final bv ON b.repo_name = bv.repo_name
ORDER BY b.repo_name, b.path;