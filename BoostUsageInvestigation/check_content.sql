-- Check what's actually in the content field
-- Run these one at a time

-- 1. Check if content is already plain text (not base64)
SELECT 
  c.sample_repo_name,
  c.sample_path,
  SUBSTR(c.content, 1, 100) AS content_preview,
  LENGTH(c.content) AS content_length
FROM `bigquery-public-data.github_repos.sample_contents` c
WHERE c.binary = FALSE
  AND ENDS_WITH(c.sample_path, '.cpp')
LIMIT 3;

-- 2. Test if content contains "include" directly (without decoding)
SELECT 
  c.sample_repo_name,
  c.sample_path
FROM `bigquery-public-data.github_repos.sample_contents` c
WHERE c.binary = FALSE
  AND ENDS_WITH(c.sample_path, '.cpp')
  AND REGEXP_CONTAINS(c.content, r'include')
LIMIT 3;

-- 3. Test base64 decoding result
SELECT 
  c.sample_repo_name,
  c.sample_path,
  SAFE_CONVERT_BYTES_TO_STRING(SAFE.FROM_BASE64(c.content)) AS decoded,
  SUBSTR(c.content, 1, 50) AS raw_content_preview
FROM `bigquery-public-data.github_repos.sample_contents` c
WHERE c.binary = FALSE
  AND ENDS_WITH(c.sample_path, '.cpp')
LIMIT 3;

-- 4. Search for "boost" in raw content (without decoding)
SELECT 
  c.sample_repo_name,
  c.sample_path
FROM `bigquery-public-data.github_repos.sample_contents` c
WHERE c.binary = FALSE
  AND ENDS_WITH(c.sample_path, '.cpp')
  AND REGEXP_CONTAINS(c.content, r'(?i)boost')
LIMIT 3;

