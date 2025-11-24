-- Find all GitHub repos using C++ Boost library
-- This query searches the BigQuery GitHub public dataset for C++ files containing Boost includes

WITH boost_files AS (
  SELECT
    f.repo_name,
    f.ref,
    f.path,
    f.mode,
    f.id,
    f.symlink_target,
    c.content
  FROM `bigquery-public-data.github_repos.sample_contents` c
  JOIN `bigquery-public-data.github_repos.sample_files` f
    ON c.id = f.id
  WHERE c.binary = FALSE
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
    AND REGEXP_CONTAINS(c.content, r'(?i)#include\s*<boost/')
),
latest_sample_commits AS (
  SELECT
    repo_name,
    MAX(committer.date) AS last_commit_ts
  FROM `bigquery-public-data.github_repos.sample_commits`
  GROUP BY repo_name
)
SELECT
  b.repo_name,
  b.ref,
  b.path,
  b.mode,
  b.id,
  b.symlink_target,
  LENGTH(b.content) AS file_size_bytes,
  b.content AS content_preview,
  lc.last_commit_ts
FROM boost_files b
LEFT JOIN latest_sample_commits lc
  ON b.repo_name = lc.repo_name
ORDER BY b.repo_name, b.path