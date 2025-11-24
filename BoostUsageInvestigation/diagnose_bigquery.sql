-- Simple diagnostic queries - minimal data scanning
-- Run these one at a time to identify the problem

-- 1. Check table schemas (metadata only - no cost)
SELECT 
  table_name,
  column_name,
  data_type
FROM `bigquery-public-data.github_repos.INFORMATION_SCHEMA.COLUMNS`
WHERE table_schema = 'github_repos'
  AND table_name IN ('sample_contents', 'sample_files', 'contents', 'files')
ORDER BY table_name, ordinal_position;

-- 2. Quick test: Check if sample_contents has any data (LIMIT 1 - very cheap)
SELECT 
  'sample_contents' AS table_name,
  COUNT(*) AS row_count
FROM `bigquery-public-data.github_repos.sample_contents`
LIMIT 1;

-- 3. Quick test: Check if sample_files has any data (LIMIT 1 - very cheap)
SELECT 
  'sample_files' AS table_name,
  COUNT(*) AS row_count
FROM `bigquery-public-data.github_repos.sample_files`
LIMIT 1;

-- 4. Test base64 decoding on ONE row only (very cheap)
SELECT 
  c.id,
  LENGTH(c.content) AS content_length,
  SAFE_CONVERT_BYTES_TO_STRING(SAFE.FROM_BASE64(CAST(c.content AS STRING))) AS decoded_sample
FROM `bigquery-public-data.github_repos.sample_contents` c
WHERE LENGTH(c.content) > 0
LIMIT 1;

-- 5. Test join on ONE row only (very cheap)
SELECT 
  c.id AS content_id,
  f.id AS file_id,
  f.repo_name,
  f.path
FROM `bigquery-public-data.github_repos.sample_contents` c
INNER JOIN `bigquery-public-data.github_repos.sample_files` f
  ON c.id = f.id
LIMIT 1;

-- 6. Simple test: Find ONE file with "boost" (LIMIT 1 - very cheap)
SELECT 
  f.repo_name,
  f.path
FROM `bigquery-public-data.github_repos.sample_contents` c
INNER JOIN `bigquery-public-data.github_repos.sample_files` f
  ON c.id = f.id
WHERE LENGTH(c.content) > 0
  AND SAFE_CONVERT_BYTES_TO_STRING(SAFE.FROM_BASE64(CAST(c.content AS STRING))) IS NOT NULL
  AND REGEXP_CONTAINS(
    SAFE_CONVERT_BYTES_TO_STRING(SAFE.FROM_BASE64(CAST(c.content AS STRING))),
    r'boost'
  )
LIMIT 1;
