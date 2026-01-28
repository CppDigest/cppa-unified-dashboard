-- Boost Usage Analysis Query
-- Extracts files using Boost libraries from GitHub repositories

WITH
    -- 1) Detect repos with vendored Boost
    vendored_boost AS (
        SELECT DISTINCT
            repo_name
        FROM
            `bigquery-public-data.github_repos.files`
        WHERE
            REGEXP_CONTAINS (path, r '(^|/)boost/')
    ),

-- 2) Files containing Boost includes
boost_files AS (
    SELECT
        f.repo_name,
        f.ref,
        f.path,
        f.mode,
        f.id,
        f.symlink_target,
        c.size AS file_size_bytes,
        COALESCE(
            SAFE_CONVERT_BYTES_TO_STRING (SAFE.FROM_BASE64 (c.content)),
            c.content
        ) AS content_text
    FROM
        `bigquery-public-data.github_repos.contents` c
        JOIN `bigquery-public-data.github_repos.files` f ON c.id = f.id
    WHERE
        c.binary = FALSE
        AND c.content IS NOT NULL
        AND LENGTH(c.content) > 0
        AND REGEXP_CONTAINS (
            f.path,
            r '\.(cpp|cxx|cc|hpp|hxx|hh|c|h)$'
        )
        AND REGEXP_CONTAINS (
            COALESCE(
                SAFE_CONVERT_BYTES_TO_STRING (SAFE.FROM_BASE64 (c.content)),
                c.content
            ),
            r '(?i)#\s*include\s*["<]\s*boost/'
        )
),

-- 3) Latest commit metadata per file
latest_file_commits AS (
    SELECT
        bf.repo_name,
        bf.path,
        MAX(
            TIMESTAMP_SECONDS (c.committer.time_sec)
        ) AS last_commit_ts,
        ARRAY_AGG (
            c.commit
            ORDER BY TIMESTAMP_SECONDS (c.committer.time_sec) DESC
            LIMIT 1
        ) [OFFSET(0)] AS commit_sha
    FROM
        boost_files bf
        JOIN `bigquery-public-data.github_repos.commits` c ON bf.repo_name IN UNNEST (c.repo_name)
        JOIN `bigquery-public-data.github_repos.files` tree_f ON c.tree = tree_f.id
        AND bf.path = tree_f.path
        AND bf.repo_name = tree_f.repo_name
    WHERE
        c.committer.time_sec IS NOT NULL
    GROUP BY
        bf.repo_name,
        bf.path
),

-- 4) Boost version detection
-- 4A) From vendored boost/version.hpp
boost_versions_vendored AS (
    SELECT f.repo_name, REGEXP_EXTRACT (
            COALESCE(
                SAFE_CONVERT_BYTES_TO_STRING (SAFE.FROM_BASE64 (c.content)), c.content
            ), r '#define\s+BOOST_VERSION\s+(\d{6})'
        ) AS version_num
    FROM
        `bigquery-public-data.github_repos.files` f
        JOIN `bigquery-public-data.github_repos.contents` c ON f.id = c.id
    WHERE
        f.path = 'boost/version.hpp'
),
boost_versions_vendored_clean AS (
    SELECT repo_name, CONCAT (
            CAST(
                CAST(
                    SAFE_CAST (version_num AS INT64) / 100000 AS INT64
                ) AS STRING
            ), '.', CAST(
                MOD(
                    CAST(
                        SAFE_CAST (version_num AS INT64) / 100 AS INT64
                    ), 1000
                ) AS STRING
            ), '.', CAST(
                MOD(
                    SAFE_CAST (version_num AS INT64), 100
                ) AS STRING
            )
        ) AS version
    FROM boost_versions_vendored
    WHERE
        version_num IS NOT NULL
),

-- 4B) From CMake find_package(Boost)
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

-- 4C) From Conan (boost/1.76.0)
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

-- 4D) From vcpkg.json
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
    SELECT repo_name, version
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
boost_version_final AS (
    SELECT
        repo_name,
        ANY_VALUE (version) AS boost_version
    FROM all_boost_versions
    GROUP BY
        repo_name
)

-- Final output
SELECT
    b.repo_name,
    bv.boost_version,
    b.ref,
    b.path,
    b.mode,
    b.id,
    b.file_size_bytes,
    b.content_text AS file_content,
    lfc.last_commit_ts,
    lfc.commit_sha AS file_commit_sha,
    v.repo_name IS NOT NULL AS contains_vendored_boost,
    CASE
        WHEN v.repo_name IS NOT NULL THEN 'NOT AFFECTED (vendored boost)'
        ELSE 'AFFECTED (uses system boost)'
    END AS boost_update_impact
FROM
    boost_files b
    LEFT JOIN latest_file_commits lfc ON b.repo_name = lfc.repo_name
    AND b.path = lfc.path
    LEFT JOIN vendored_boost v ON b.repo_name = v.repo_name
    LEFT JOIN boost_version_final bv ON b.repo_name = bv.repo_name
ORDER BY b.repo_name, b.path;