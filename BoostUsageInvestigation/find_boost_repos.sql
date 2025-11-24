-- Find all GitHub repos using C++ Boost library
-- This query searches the BigQuery GitHub public dataset for C++ files containing Boost includes

WITH boost_files AS (
  SELECT *
  FROM (
    SELECT
      f.repo_name,
      f.ref,
      f.path,
      f.mode,
      f.id,
      f.symlink_target,
      c.size AS file_size_bytes,
      COALESCE(
        SAFE_CONVERT_BYTES_TO_STRING(SAFE.FROM_BASE64(c.content)),
        c.content
      ) AS content_text
    FROM `bigquery-public-data.github_repos.contents` c
    JOIN `bigquery-public-data.github_repos.files` f
      ON c.id = f.id
    WHERE c.binary = FALSE
      AND c.content IS NOT NULL
      AND LENGTH(c.content) > 0
      AND (
        ENDS_WITH(f.path, '.cpp') OR
        ENDS_WITH(f.path, '.cxx') OR
        ENDS_WITH(f.path, '.cc') OR
        ENDS_WITH(f.path, '.hpp') OR
        ENDS_WITH(f.path, '.hxx') OR
        ENDS_WITH(f.path, '.hh') OR
        ENDS_WITH(f.path, '.c') OR
        ENDS_WITH(f.path, '.h')
      )
  )
  WHERE REGEXP_CONTAINS(content_text, r'(?i)#include\s*<boost/')
),
latest_commits AS (
  SELECT
    repo AS repo_name,
    MAX(TIMESTAMP_SECONDS(c.committer.time_sec)) AS last_commit_ts,
    ANY_VALUE(c.commit) AS commit_sha,
    ANY_VALUE(c.tree) AS tree_sha,
    ANY_VALUE(c.parent) AS parent_commits,
    ANY_VALUE(c.author) AS author_info,
    ANY_VALUE(c.committer) AS committer_info,
    ANY_VALUE(c.subject) AS subject,
    ANY_VALUE(c.message) AS message
  FROM (
    SELECT
      c.* EXCEPT(trailer, difference, difference_truncated, encoding),
      c.repo_name AS repo_list
    FROM `bigquery-public-data.github_repos.commits` c
  ) c
  CROSS JOIN UNNEST(c.repo_list) AS repo
  GROUP BY repo
)
SELECT
  b.repo_name,
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
  lc.message
FROM boost_files b
LEFT JOIN latest_commits lc
  ON b.repo_name = lc.repo_name
ORDER BY b.repo_name, b.path