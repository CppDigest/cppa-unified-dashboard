# Boost Usage Analysis Report

Generated: 2025-12-09 20:00:13 UTC

## Data Source and Date Range

**Data Source Reference**: The BigQuery public dataset can be accessed at: https://console.cloud.google.com/bigquery?ws=!1m5!1m4!4m3!1sbigquery-public-data!2sgithub_repos!3sfiles

**Important**: This report is generated from BigQuery data covering the period **2002-2022**. The BigQuery dataset (`bigquery-public-data.github_repos`) was last updated on **2022-11-27**, which means:
- All commit timestamps in this report are from commits made on or before 2022-11-27
- Repository activity after 2022-11-27 is not included in this analysis
- The "latest commit" dates shown in the statistics reflect the most recent commit in the dataset, not necessarily the current state of repositories

## Overview

- **Total Repositories**: 37,693
- **Repositories Using System Boost**: 34,158
- **Total Boost Libraries**: 151
- **Total Boost Headers**: 17,310
- **Total Usage Records**: 3,083,707

**Note on Repository Counts**: "Repositories Using Boost" counts distinct repositories that depend on external/system Boost. This may be less than "Total Repositories" because repositories with vendored Boost bundle their own copy of Boost rather than using external Boost, so their Boost includes are filtered out during processing.

## Top Boost Libraries by Repository Count

| Library | Repository Count | Usage Count | Earliest Commit | Latest Commit |
|---------|------------------|-------------|-----------------|---------------|
| smart_ptr | 15,469 | 176,577 | 2002-06-10T16:45:41Z | 2022-11-26T00:18:53Z |
| thread | 14,682 | 146,934 | 2003-03-10T08:58:24Z | 2022-11-24T13:06:24Z |
| algorithm | 14,109 | 159,208 | 2004-03-04T22:12:19Z | 2022-11-26T01:01:28Z |
| filesystem | 13,362 | 165,356 | 2004-07-12T19:03:46Z | 2022-11-25T23:32:19Z |
| bind | 12,635 | 79,991 | 2005-01-07T16:39:44Z | 2022-11-24T08:12:33Z |
| lexical_cast | 12,128 | 50,802 | 2002-02-11T01:28:42Z | 2022-11-26T00:18:53Z |
| program_options | 11,469 | 45,198 | 2006-04-09T18:49:48Z | 2022-11-24T15:03:42Z |
| asio | 11,059 | 87,193 | 2007-07-03T17:12:16Z | 2022-11-26T00:18:53Z |
| config | 10,996 | 111,619 | 2002-06-10T16:45:41Z | 2022-11-25T15:47:21Z |
| date_time | 10,610 | 52,943 | 2006-03-26T20:54:29Z | 2022-11-25T21:46:13Z |
| function | 9,716 | 33,915 | 2003-03-20T17:54:09Z | 2022-11-24T08:36:02Z |
| test | 9,476 | 270,574 | 2006-10-17T20:36:13Z | 2022-11-25T18:39:16Z |
| foreach | 9,462 | 141,624 | 2007-08-17T09:04:43Z | 2022-11-24T17:16:14Z |
| variant | 8,138 | 26,127 | 2006-08-10T16:05:45Z | 2022-11-22T22:39:48Z |
| type_traits | 7,796 | 67,064 | 2002-06-10T16:45:41Z | 2022-11-25T15:47:21Z |
| tuple | 7,755 | 37,258 | 2006-02-23T08:03:51Z | 2022-11-16T11:51:01Z |
| iostreams | 7,481 | 39,905 | 2006-02-25T15:57:24Z | 2022-11-22T16:16:04Z |
| array | 7,438 | 16,188 | 2007-05-11T15:35:15Z | 2022-11-01T09:00:22Z |
| assign | 6,973 | 71,514 | 2007-05-11T15:35:15Z | 2022-11-24T16:53:10Z |
| interprocess | 6,792 | 38,805 | 2009-12-16T00:18:21Z | 2022-11-23T13:49:55Z |

## Bottom Boost Libraries by Repository Count

| Library | Repository Count | Usage Count | Earliest Commit | Latest Commit |
|---------|------------------|-------------|-----------------|---------------|
| hof | 1 | 2 | 2022-10-05T05:08:30Z | 2022-11-09T16:12:16Z |
| leaf | 2 | 2 | 2021-01-19T01:29:09Z | 2022-02-11T05:25:12Z |
| outcome | 3 | 11 | 2022-03-16T16:56:02Z | 2022-10-27T13:51:42Z |
| poly_collection | 3 | 32 | 2017-07-20T17:36:36Z | 2022-11-13T22:14:46Z |
| safe_numerics | 3 | 3 | 2021-06-03T08:04:34Z | 2022-09-22T06:12:02Z |
| stl_interfaces | 3 | 11 | 2020-11-13T13:39:58Z | 2021-10-23T12:16:17Z |
| static_string | 4 | 10 | 2013-10-09T13:51:41Z | 2020-11-23T02:26:26Z |
| variant2 | 4 | 4 | 2019-11-13T19:30:27Z | 2022-01-28T10:13:36Z |
| metaparse | 6 | 2,342 | 2016-04-25T19:46:29Z | 2021-02-12T11:15:42Z |
| pfr | 7 | 7 | 2017-08-20T23:58:09Z | 2022-09-30T10:16:00Z |
| vmd | 9 | 2,337 | 2016-01-05T08:08:40Z | 2022-10-12T16:02:07Z |
| mp11 | 10 | 42 | 2018-02-12T15:50:47Z | 2022-11-19T09:17:05Z |
| histogram | 11 | 168 | 2019-07-20T04:26:26Z | 2022-11-04T13:45:54Z |
| qvm | 12 | 1,374 | 2011-08-23T13:35:37Z | 2022-06-27T08:38:14Z |
| contract | 15 | 15 | 2018-04-16T15:02:22Z | 2019-05-11T19:54:38Z |
| convert | 15 | 309 | 2016-01-05T08:08:40Z | 2021-05-20T04:18:44Z |
| parameter_python | 18 | 21 | 2011-11-02T23:50:20Z | 2018-01-09T13:26:11Z |
| json | 19 | 68 | 2011-07-20T06:21:52Z | 2022-11-25T23:32:19Z |
| callable_traits | 20 | 52 | 2017-11-18T21:34:51Z | 2022-11-08T10:48:50Z |
| type_erasure | 20 | 3,325 | 2013-10-09T13:51:41Z | 2018-01-09T13:26:11Z |

## Top Boost Headers by Repository Count

| Header | Repository Count | Usage Count |
|--------|------------------|-------------|
| boost/shared_ptr.hpp | 12,922 | 94,079 |
| boost/bind.hpp | 12,518 | 75,975 |
| boost/algorithm/string.hpp | 12,482 | 52,930 |
| boost/filesystem.hpp | 12,437 | 90,094 |
| boost/lexical_cast.hpp | 12,123 | 50,582 |
| boost/thread.hpp | 10,986 | 49,006 |
| boost/asio.hpp | 9,891 | 27,879 |
| boost/function.hpp | 9,701 | 31,242 |
| boost/foreach.hpp | 9,460 | 141,563 |
| boost/thread/mutex.hpp | 9,404 | 28,677 |
| boost/test/unit_test.hpp | 8,962 | 231,622 |
| boost/version.hpp | 8,811 | 26,710 |
| boost/variant.hpp | 7,903 | 17,602 |
| boost/tuple/tuple.hpp | 7,703 | 26,313 |
| boost/date_time/posix_time/posix_time.hpp | 7,614 | 18,696 |
| boost/array.hpp | 7,437 | 16,170 |
| boost/filesystem/path.hpp | 7,314 | 19,900 |
| boost/config.hpp | 7,277 | 45,177 |
| boost/algorithm/string/predicate.hpp | 7,212 | 27,745 |
| boost/algorithm/string/replace.hpp | 7,099 | 23,281 |

## Repository Counts by Year

This table shows the number of repositories using Boost, grouped by the year of their latest commit.

| Year | Repository Count |
|------|------------------|
| 2022 | 1,041 |
| 2021 | 645 |
| 2020 | 812 |
| 2019 | 928 |
| 2018 | 1,568 |
| 2017 | 4,616 |
| 2016 | 4,858 |
| 2015 | 9,411 |
| 2014 | 7,155 |
| 2013 | 2,819 |
| 2012 | 1,259 |
| 2011 | 789 |
| 2010 | 468 |
| 2009 | 267 |
| 2008 | 99 |
| 2007 | 31 |
| 2006 | 3 |
| 2005 | 2 |
| 2003 | 3 |
| 2002 | 2 |
## Version Coverage Statistics

- **Repositories with Detected Boost Version**: 3,792
- **Repositories without Detected Version**: 33,901
- **Version Coverage**: 10.1%

**Note**: Version detection relies on explicit version declarations in build files (CMake, Conan, vcpkg) or `boost/version.hpp` files. Repositories using system Boost installed via package managers may not have explicit version declarations.


## Boost Version Distribution

| Version | Usage Count |
|---------|-------------|
| 1.80.0 | 1 |
| 1.79.0 | 11 |
| 1.78.0 | 6 |
| 1.77.0 | 4 |
| 1.76.0 | 2 |
| 1.75.0 | 16 |
| 1.74.0 | 9 |
| 1.73.0 | 10 |
| 1.72.0 | 16 |
| 1.71.0 | 18 |
| 1.70.0 | 27 |
| 1.69.0 | 26 |
| 1.68.0 | 19 |
| 1.67.0 | 26 |
| 1.66.0 | 56 |
| 1.65.1 | 26 |
| 1.65.0 | 28 |
| 1.64.0 | 35 |
| 1.63.0 | 45 |
| 1.62.0 | 36 |
| 1.61.0 | 39 |
| 1.60.0 | 64 |
| 1.59.0 | 103 |
| 1.58.0 | 172 |
| 1.57.0 | 113 |
| 1.56.0 | 138 |
| 1.55.0 | 383 |
| 1.54.0 | 332 |
| 1.53.0 | 296 |
| 1.52.0 | 36 |
| 1.51.0 | 21 |
| 1.50.0 | 162 |

## Repository Counts by Year and Version

This table shows the number of repositories using Boost, grouped by both the Boost version and the year of their latest commit.

**Note**: This section only includes Boost versions for which version information was successfully detected in the repository data. Versions are shown starting from Boost 1.53.0 and later, as earlier versions may not have explicit version declarations in build files or may use different version detection methods. The absence of earlier versions in this table does not indicate they were not used, but rather that version information was not reliably detected for those repositories.

| Year | 1.80.0 | 1.79.0 | 1.78.0 | 1.77.0 | 1.76.0 | 1.75.0 | 1.74.0 | 1.73.0 | 1.72.0 | 1.71.0 | 1.70.0 | 1.69.0 | 1.68.0 | 1.67.0 | 1.66.0 | 1.65.1 | 1.65.0 | 1.64.0 | 1.63.0 | 1.62.0 | 1.61.0 | 1.60.0 | 1.59.0 | 1.58.0 | 1.57.0 | 1.56.0 | 1.55.0 | 1.54.0 | 1.53.0 |
|------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|
| 2022 | 1 | 11 | 6 | 3 | 2 | 9 | 1 | 4 | 8 | 9 | 16 | 12 | 1 | 7 | 8 | 3 | 6 | 1 | | 2 | 6 | 1 | 3 | 7 | 3 | 14 | 15 | 12 | 12 |
| 2021 | | | | 1 | | 6 | 7 | 1 | 2 | 2 | 3 | 5 | 5 | 7 | 4 | 2 | 3 | 1 | 1 | 2 | 5 | 1 | 4 | 7 | 2 | 9 | 6 | 9 | 5 |
| 2020 | | | | | | 1 | 1 | 5 | 5 | 5 | 5 | 2 | 1 | 3 | 7 | 6 | 5 | 5 | 1 | 3 | 5 | 1 | 6 | 6 | 2 | 1 | 6 | 8 | 15 |
| 2019 | | | | | | | | | 1 | 2 | 3 | 7 | 4 | 6 | 14 | | 10 | 3 | 1 | 3 | 2 | 2 | 5 | 16 | 3 | 3 | 13 | 15 | 7 |
| 2018 | | | | | | | | | | | | | 8 | 3 | 20 | 5 | 2 | 7 | 9 | 7 | 5 | 4 | 9 | 17 | 4 | 6 | 22 | 32 | 21 |
| 2017 | | | | | | | | | | | | | | | 3 | 8 | 1 | 17 | 32 | 11 | 6 | 28 | 32 | 48 | 11 | 20 | 89 | 65 | 34 |
| 2016 | | | | | | | | | | | | | | | | | | | 1 | 8 | 9 | 27 | 27 | 27 | 31 | 23 | 91 | 60 | 48 |
| 2015 | | | | | | | | | | | | | | | | | | | | | | | 15 | 42 | 54 | 30 | 91 | 93 | 119 |
| 2014 | | | | | | | | | | | | | | | | | | | | | | | | | 2 | 19 | 46 | 29 | 20 |


## Data Processing Procedure

This report is generated from BigQuery exports containing Boost-related files from GitHub repositories. The processing procedure consists of the following steps:

### 1. BigQuery Data Production

**The most important step**: Data is produced by executing `query.sql` in Google BigQuery against the `bigquery-public-data.github_repos` dataset. This query:

- Detects repositories containing Boost includes in C/C++ source files
- Identifies repositories with vendored Boost (containing `boost/` folder)
- Extracts Boost version information from multiple sources:
  - `boost/version.hpp` files (BOOST_VERSION macro)
  - CMake `find_package(Boost ...)` declarations
  - Conan `conanfile.txt` or `conanfile.py` references
  - vcpkg `vcpkg.json` manifest files
- Retrieves latest commit metadata for each repository
- Outputs results to CSV files (`bq-results-*`) exported to the data directory

The query produces CSV files with the following key fields:

- `repo_name`: GitHub repository identifier
- `path`: File path within the repository
- `file_content`: Full file content (for include extraction)
- `boost_version`: Detected Boost version (if found)
- `contains_vendored_boost`: Boolean indicating if repository has vendored Boost
- `last_commit_ts`: Timestamp of the most recent commit

### 2. Data Collection

- Scan all `bq-results-*` CSV files in the data directory (including subdirectories)
- Extract `#include <boost/...>` and `#include "boost/..."` directives from file contents
- Parse repository metadata from CSV fields

### 3. Version Detection

Boost version is determined in priority order:

1. From the `boost_version` field in the CSV (populated by `query.sql` from version detection sources)
2. If CSV field is empty, extracted from file paths containing patterns like:
   - `/boost_1_57_0/` → `1.57.0`
   - `/boost-1.70.0/` → `1.70.0`
   - `/boost1.76.0/` → `1.76.0`

**Note on Missing Version Information**: Some repositories may not have Boost version information available because:

- The repository uses system Boost installed via package managers (apt, yum, brew, etc.) without explicit version declarations in build files
- Version information is specified in documentation or README files rather than in machine-readable build configuration files
- The repository uses Boost headers directly without any dependency management system (CMake, Conan, vcpkg)
- The repository's build system doesn't explicitly declare Boost as a dependency
- Version information exists in files that are not scanned by the query (e.g., CI configuration files, Dockerfiles, or other non-standard locations)

### 4. Data Filtering

Usage records are excluded if:

- The file path contains `/boost` AND the repository has `contains_vendored_boost = true`

This ensures that vendored Boost headers within repository directories are not counted as external Boost usage.

### 5. Database Construction

A relational SQLite database is built with the following tables:

- **`boost_library`**: Unique Boost libraries
- **`boost_header`**: Headers mapped to their parent library
- **`repository`**: GitHub repositories with `affect_from_boost` flag (1 if using system Boost, 0 if vendored) and detected `boost_version`
- **`boost_usage`**: Individual usage records linking repositories to headers with file paths and commit timestamps
