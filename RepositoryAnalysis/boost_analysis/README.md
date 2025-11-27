## Boost Usage Analysis

This workspace aggregates Boost header usage from the exported BigQuery result set located in `../data`. The analysis pursues three deliverables:

- A curated `boost_usage_statistics.csv` report enumerating header-level adoption metrics.
- A relational SQLite database describing libraries, repositories, and their observed relationships.
- A summary Markdown report (`Booost_Usage_Report.md`) with key statistics and insights.

### Prerequisites

Before running the analysis script, you must first generate the BigQuery data:

1. Execute `query.sql` in Google BigQuery against the `bigquery-public-data.github_repos` dataset
2. Export the results to CSV files (`bq-results-*`) in the `../data` directory (including subdirectories)

The BigQuery query:

- Detects repositories containing Boost includes in C/C++ source files
- Identifies repositories with vendored Boost (containing `boost/` folder)
- Extracts Boost version information from multiple sources:
  - `boost/version.hpp` files (BOOST_VERSION macro)
  - CMake `find_package(Boost ...)` declarations
  - Conan `conanfile.txt` or `conanfile.py` references
  - vcpkg `vcpkg.json` manifest files
- Retrieves latest commit metadata for each repository

### Running the analysis

```
python analyze_boost_usage.py
```

The script performs a streaming pass over every `bq-results-*` file (including subdirectories), extracts `#include <boost/...>` and `#include "boost/..."` directives, and records:

- Referencing repository counts and per-header include frequency.
- Latest observed commit timestamp (UTC) for each header.
- Boost version information (from CSV field or extracted from file paths).
- Repository impact assessment (affected by system Boost updates vs. using vendored Boost).

**Processing steps:**

1. **Collect data** from all CSV files in the data directory (currently commented out in main - uncomment to rebuild database)
2. **Build database** with collected usage data (currently commented out in main - uncomment to rebuild database)
3. **Generate statistics** based on data in the database
4. **Write statistics CSV** (`boost_usage_statistics.csv`)
5. **Write summary report** (`Booost_Usage_Report.md`)

**Note**: Steps 1 and 2 are commented out in the main function by default. Uncomment them if you need to rebuild the database from scratch.

### Data filtering

Usage records are excluded if:

- The file path contains `/boost` AND the repository has `contains_vendored_boost = true`

This ensures that vendored Boost headers within repository directories are not counted as external Boost usage.

### Version detection

Boost version is determined in the following priority order:

1. **From the `boost_version` field in the CSV** (populated by `query.sql` from version detection sources):
   - `boost/version.hpp` files (BOOST_VERSION macro)
   - CMake `find_package(Boost ...)` declarations
   - Conan `conanfile.txt` or `conanfile.py` references
   - vcpkg `vcpkg.json` manifest files
2. **Extracted from file paths** (if CSV field is empty) containing patterns like:
   - `/boost_1_57_0/` → `1.57.0`
   - `/boost-1.70.0/` → `1.70.0`
   - `/boost1.76.0/` → `1.76.0`

**Note on Missing Version Information**: Some repositories may not have Boost version information available because:

- The repository uses system Boost installed via package managers (apt, yum, brew, etc.) without explicit version declarations in build files
- Version information is specified in documentation or README files rather than in machine-readable build configuration files
- The repository uses Boost headers directly without any dependency management system (CMake, Conan, vcpkg)
- The repository's build system doesn't explicitly declare Boost as a dependency
- Version information exists in files that are not scanned by the query (e.g., CI configuration files, Dockerfiles, or other non-standard locations)

### Output schema

#### `boost_usage_statistics.csv`

| Column             | Description                                                           |
| ------------------ | --------------------------------------------------------------------- |
| `library_name`     | First path segment following `boost/` within the include directive.   |
| `header_name`      | Canonical include target, beginning with `boost/`.                    |
| `repository_count` | Number of distinct repositories that include the header.              |
| `usage_count`      | Total number of times the header is included across all files.        |
| `last_commit_time` | Most recent commit (ISO-8601, UTC) referencing the header.            |
| `boost_version`    | Most common Boost version used by repositories including this header. |

#### `boost_usage.db`

**`boost_library`** — unique Boost libraries

- `id` (PRIMARY KEY)
- `name` (UNIQUE)

**`boost_header`** — headers mapped to their parent library

- `id` (PRIMARY KEY)
- `library_id` (FOREIGN KEY → `boost_library.id`)
- `header_name` (UNIQUE)
- `max_commit_ts` (TEXT, ISO-8601 UTC)

**`repository`** — GitHub repositories from the dataset

- `id` (PRIMARY KEY)
- `repo_name` (UNIQUE)
- `affect_from_boost` (INTEGER: 1 if affected by system Boost updates, 0 if using vendored Boost)
- `boost_version` (TEXT, nullable: detected or extracted Boost version)

**`boost_usage`** — occurrences of a header within a repository

- `id` (PRIMARY KEY)
- `repository_id` (FOREIGN KEY → `repository.id`)
- `file_path` (TEXT: path to the file containing the include)
- `header_id` (FOREIGN KEY → `boost_header.id`)
- `last_commit_ts` (TEXT, ISO-8601 UTC, nullable)
- `excepted_ts` (TEXT, nullable: placeholder for future use)

#### `Booost_Usage_Report.md`

A summary report containing:

- Overall statistics (total repositories, affected repositories, usage counts)
- Top 20 Boost libraries by repository count
- Top 20 Boost headers by repository count
- Top 10 Boost version distribution
- Detailed data processing procedure documentation (including BigQuery query details, data collection, version detection, filtering, and database construction)

### Database relationships

The database structure enables queries such as:

- Which repositories are affected by Boost updates (use system Boost)?
- What Boost versions are most commonly used?
- Which Boost libraries and headers are most popular?
- Which files in which repositories use specific Boost headers?

This structure enables downstream SQL analysis and can be extended with additional metadata, such as star counts retrieved from the GitHub API, should the C++ Alliance require deeper insights.
