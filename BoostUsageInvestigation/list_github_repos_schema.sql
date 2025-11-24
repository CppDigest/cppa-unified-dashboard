-- List all tables and their columns in the github_repos dataset
-- This uses INFORMATION_SCHEMA (metadata only - no cost)

SELECT 
  table_name,
  column_name,
  data_type,
  is_nullable,
  ordinal_position
FROM `bigquery-public-data.github_repos.INFORMATION_SCHEMA.COLUMNS`
WHERE table_schema = 'github_repos'
ORDER BY table_name, ordinal_position;

