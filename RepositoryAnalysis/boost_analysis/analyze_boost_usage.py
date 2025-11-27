from __future__ import annotations

import csv
import os
import sqlite3
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STATS_CSV = BASE_DIR / "boost_usage_statistics.csv"
REPORT_MD = BASE_DIR / "boost_analysis" / "Booost_Usage_Report.md"
DB_PATH = Path(__file__).resolve().parent / "boost_usage.db"

# Path to Boost source code (can be set via BOOST_SOURCE_PATH environment variable)
# Should point to the directory containing the boost/ folder (e.g., /path/to/boost_1_89_0/boost)
BOOST_SOURCE_PATH_STR = os.getenv("BOOST_SOURCE_PATH", "D:/boost_1_89_0/boost")
BOOST_SOURCE_PATH = Path(BOOST_SOURCE_PATH_STR) if BOOST_SOURCE_PATH_STR else None

BOOST_INCLUDE_RE = re.compile(r'#include\s*[<"]\s*(boost/[^>"]+)[>"]')

csv.field_size_limit(2**31 - 1)


def parse_timestamp(raw: str) -> Optional[int]:
    raw = (raw or "").strip()
    if not raw:
        return None
    if raw.endswith(" UTC"):
        raw = raw[:-4]
    try:
        parsed = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return int(parsed.timestamp())


def parse_boolean(raw: str) -> bool:
    raw = (raw or "").strip().upper()
    return raw in ("TRUE", "1", "YES", "T")


def isoformat(epoch_seconds: Optional[int], empty: bool = False) -> Optional[str]:
    if epoch_seconds is None:
        return "" if empty else None
    return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def iter_data_files() -> Iterable[Path]:
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Missing data directory: {DATA_DIR}")
    return sorted(DATA_DIR.rglob("bq-results-*"))


def extract_boost_includes(content: str) -> List[str]:
    if not content:
        return []
    headers = []
    for match in BOOST_INCLUDE_RE.finditer(content):
        header = match.group(1).strip()
        if not header:
            continue
        headers.append(header)
    return headers


def extract_version_from_path(path: str) -> Optional[str]:
    """Extract Boost version from path if it contains patterns like /boost_1_57_0/ or /boost-1.57.0/."""
    if not path:
        return None
    
    # Pattern 1: /boost_1_57_0/ or /boost_1_70_0/
    match = re.search(r'/boost[_-](\d+)[_-](\d+)[_-](\d+)', path)
    if match:
        return f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
    
    # Pattern 2: /boost-1.57.0/ or /boost-1.70.0/
    match = re.search(r'/boost[_-](\d+\.\d+\.\d+)', path)
    if match:
        return match.group(1)
    
    # Pattern 3: /boost1.57.0/ or /boost1.70.0/
    match = re.search(r'/boost(\d+\.\d+\.\d+)', path)
    if match:
        return match.group(1)
    
    return None


def should_exclude_usage(path: str, contains_vendored_boost: bool) -> bool:
    """Exclude rows where path contains '/boost' AND contains_vendored_boost is true."""
    return "/boost" in path and contains_vendored_boost


def collect_usage_data():
    """Collect all usage data from CSV files."""
    usage_records = []  # List of (repo_name, file_path, header, last_commit_ts)
    repo_info: Dict[str, Dict[str, any]] = {}  # repo_name -> {contains_vendored_boost, boost_version}
    header_meta: Dict[str, Dict[str, any]] = {}  # header_name -> {library_name, max_commit}
    
    total_rows = 0
    total_includes = 0
    excluded_count = 0

    for csv_path in iter_data_files():
        print(f"Scanning {csv_path.name} ...")
        with csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                total_rows += 1
                repo = (row.get("repo_name") or "").strip()
                if not repo:
                    continue
                
                file_path = (row.get("path") or "").strip()
                contains_vendored = parse_boolean(row.get("contains_vendored_boost", ""))
                boost_version = (row.get("boost_version") or "").strip() or None
                last_commit = parse_timestamp(row.get("last_commit_ts", ""))
                
                # Extract version from path if CSV field is empty
                if not boost_version:
                    boost_version = extract_version_from_path(file_path)
                
                # Store repo info
                if repo not in repo_info:
                    repo_info[repo] = {
                        "contains_vendored_boost": contains_vendored,
                        "boost_version": boost_version,
                    }
                else:
                    # Update version if we find a non-null one
                    if boost_version and not repo_info[repo]["boost_version"]:
                        repo_info[repo]["boost_version"] = boost_version
                
                includes = extract_boost_includes(row.get("file_content", ""))
                if not includes:
                    continue
                
                for header in includes:
                    total_includes += 1
                    
                    # Check if we should exclude this usage
                    if should_exclude_usage(file_path, contains_vendored):
                        excluded_count += 1
                        continue
                    # Store usage record (without boost_version - it's in repository table)
                    usage_records.append({
                        "repo_name": repo,
                        "file_path": file_path,
                        "header": header,
                        "last_commit_ts": last_commit,
                    })

    print(
        f"Completed scan: {len(header_meta)} headers, {len(repo_info)} repositories, "
        f"{total_rows} files, {total_includes} Boost includes, {excluded_count} excluded."
    )

    return {
        "usage_records": usage_records,
        "repo_info": repo_info,
        "header_meta": header_meta,
    }


def build_database(data):
    """
    Build the boost_usage table by referencing existing boost_library and boost_header tables.
    
    This function does NOT modify boost_library or boost_header tables. It only:
    1. Creates repository and boost_usage tables if they don't exist
    2. Inserts repository records
    3. Inserts boost_usage records by matching headers via full_header_name
    """
    usage_records = data["usage_records"]
    repo_info = data["repo_info"]

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    
    # Create tables if they don't exist (but don't populate boost_library/boost_header)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS boost_library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS boost_header (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            library_id INTEGER NOT NULL,
            header_name TEXT NOT NULL UNIQUE,
            full_header_name TEXT,
            max_commit_ts TEXT,
            FOREIGN KEY (library_id) REFERENCES boost_library(id)
        );

        CREATE TABLE IF NOT EXISTS repository (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_name TEXT NOT NULL UNIQUE,
            affect_from_boost INTEGER NOT NULL,
            boost_version TEXT
        );

        CREATE TABLE IF NOT EXISTS boost_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repository_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            header_id INTEGER NOT NULL,
            last_commit_ts TEXT,
            excepted_ts TEXT,
            FOREIGN KEY (repository_id) REFERENCES repository(id),
            FOREIGN KEY (header_id) REFERENCES boost_header(id)
        );
        """
    )

    repo_ids: Dict[str, int] = {}
    header_id_cache: Dict[str, Optional[int]] = {}  # Cache for full_header_name -> header_id lookups

    with conn:
        # Check if boost_header table has data
        header_count = conn.execute("SELECT COUNT(*) FROM boost_header").fetchone()[0]
        if header_count == 0:
            print("Warning: boost_header table is empty. Please run populate_boost_headers.py first.")
            conn.close()
            return 0

        # Insert or get repositories
        for repo_name, info in sorted(repo_info.items()):
            # Check if repository already exists
            existing = conn.execute(
                "SELECT id FROM repository WHERE repo_name = ?",
                (repo_name,),
            ).fetchone()
            
            if existing:
                repo_ids[repo_name] = existing[0]
            else:
                affect_from_boost = 1 if not info["contains_vendored_boost"] else 0
                boost_version = info.get("boost_version")
                cur = conn.execute(
                    "INSERT INTO repository (repo_name, affect_from_boost, boost_version) VALUES (?, ?, ?)",
                    (repo_name, affect_from_boost, boost_version),
                )
                repo_ids[repo_name] = cur.lastrowid

        # Build header_id lookup cache by full_header_name
        for row in conn.execute("SELECT id, full_header_name FROM boost_header WHERE full_header_name IS NOT NULL"):
            header_id, full_header_name = row
            if full_header_name:
                header_id_cache[full_header_name] = header_id
        
        # Also cache by header_name for cases where full_header_name is NULL or same as header_name
        for row in conn.execute("SELECT id, header_name, full_header_name FROM boost_header"):
            header_id, header_name, full_header_name = row
            # If full_header_name is NULL or same as header_name, use header_name as key
            if not full_header_name or full_header_name == header_name:
                if header_name not in header_id_cache:
                    header_id_cache[header_name] = header_id

        # Insert usage records
        usage_rows = []
        unmatched_headers = set()
        
        for record in usage_records:
            repo_id = repo_ids.get(record["repo_name"])
            if repo_id is None:
                continue
            
            # Look up header_id by full_header_name (the real_header from derive_library_name)
            header = record["header"]
            header_id = header_id_cache.get(header)
            
            if header_id is None:
                unmatched_headers.add(header)
                continue
            
            usage_rows.append(
                (
                    repo_id,
                    record["file_path"],
                    header_id,
                    isoformat(record["last_commit_ts"]),
                    None,  # excepted_ts - placeholder for future use
                )
            )
        
        if unmatched_headers:
            print(f"Warning: {len(unmatched_headers)} unique headers not found in boost_header table:")
            for h in sorted(unmatched_headers)[:10]:  # Show first 10
                print(f"  - {h}")
            if len(unmatched_headers) > 10:
                print(f"  ... and {len(unmatched_headers) - 10} more")
        
        conn.executemany(
            "INSERT INTO boost_usage (repository_id, file_path, header_id, last_commit_ts, excepted_ts) "
            "VALUES (?, ?, ?, ?, ?)",
            usage_rows,
        )

    conn.close()
    print(f"Inserted {len(usage_rows):,} usage records into database.")
    return len(usage_rows)


def generate_statistics():
    """Generate statistics from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    stats = {}
    
    # Overall statistics
    stats["total_repositories"] = conn.execute("SELECT COUNT(*) FROM repository").fetchone()[0]
    stats["affected_repositories"] = conn.execute(
        "SELECT COUNT(*) FROM repository WHERE affect_from_boost = 1"
    ).fetchone()[0]
    stats["total_headers"] = conn.execute("SELECT COUNT(*) FROM boost_header").fetchone()[0]
    stats["total_libraries"] = conn.execute("SELECT COUNT(*) FROM boost_library").fetchone()[0]
    stats["total_usage_records"] = conn.execute("SELECT COUNT(*) FROM boost_usage").fetchone()[0]
    
    # Unique repositories using Boost
    stats["repos_using_boost"] = conn.execute(
        "SELECT COUNT(DISTINCT repository_id) FROM boost_usage"
    ).fetchone()[0]
    
    # Version statistics (from repository table)
    version_stats = conn.execute(
        "SELECT boost_version, COUNT(*) as cnt FROM repository "
        "WHERE boost_version IS NOT NULL AND boost_version != '' "
        "GROUP BY boost_version ORDER BY cnt DESC LIMIT 10"
    ).fetchall()
    stats["version_distribution"] = [(row["boost_version"], row["cnt"]) for row in version_stats]
    
    # Top libraries by repository count
    top_libraries = conn.execute(
        """
        SELECT bl.name, COUNT(bu.id) as usage_count, COUNT(DISTINCT bu.repository_id) as repo_count
        FROM boost_library bl
        JOIN boost_header bh ON bl.id = bh.library_id
        JOIN boost_usage bu ON bh.id = bu.header_id
        GROUP BY bl.id, bl.name
        ORDER BY repo_count DESC
        LIMIT 20
        """
    ).fetchall()
    stats["top_libraries"] = [
        {"name": row["name"], "usage_count": row["usage_count"], "repo_count": row["repo_count"]}
        for row in top_libraries
    ]
    
    # Top headers by repository count
    top_headers = conn.execute(
        """
        SELECT bh.header_name, COUNT(bu.id) as usage_count, COUNT(DISTINCT bu.repository_id) as repo_count
        FROM boost_header bh
        JOIN boost_usage bu ON bh.id = bu.header_id
        GROUP BY bh.id, bh.header_name
        ORDER BY repo_count DESC
        LIMIT 20
        """
    ).fetchall()
    stats["top_headers"] = [
        {"header": row["header_name"], "usage_count": row["usage_count"], "repo_count": row["repo_count"]}
        for row in top_headers
    ]
    
    conn.close()
    return stats


def write_statistics_csv():
    """Write statistics to CSV file."""
    headers = [
        "library_name",
        "header_name",
        "repository_count",
        "usage_count",
        "last_commit_time",
        "boost_version",
    ]
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    rows = []
    query = """
        SELECT 
            bl.name as library_name,
            bh.header_name,
            COUNT(DISTINCT bu.repository_id) as repository_count,
            COUNT(bu.id) as usage_count,
            MAX(bu.last_commit_ts) as last_commit_time,
            GROUP_CONCAT(DISTINCT r.boost_version) as boost_versions
        FROM boost_header bh
        JOIN boost_library bl ON bh.library_id = bl.id
        JOIN boost_usage bu ON bh.id = bu.header_id
        JOIN repository r ON bu.repository_id = r.id
        GROUP BY bh.id, bh.header_name, bl.name
        ORDER BY bl.name, repository_count DESC
    """
    
    for row in conn.execute(query):
        # Get most common version if multiple
        versions = [v.strip() for v in (row["boost_versions"] or "").split(",") if v.strip()]
        most_common_version = max(set(versions), key=versions.count) if versions else ""
        
        rows.append([
            row["library_name"],
            row["header_name"],
            row["repository_count"],
            row["usage_count"],
            row["last_commit_time"] or "",
            most_common_version,
        ])
    
    conn.close()
    
    with STATS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter=",")
        writer.writerow(headers)
        writer.writerows(rows)
    
    print(f"Wrote {len(rows)} statistics rows to {STATS_CSV.relative_to(BASE_DIR)}")


def write_report(stats):
    """Write summary report in Markdown format."""
    report_lines = [
        "# Boost Usage Analysis Report",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "",
        "## Overview",
        "",
        f"- **Total Repositories**: {stats['total_repositories']:,}",
        f"- **Repositories Using System Boost**: {stats['affected_repositories']:,}",
        f"- **Repositories Using Boost**: {stats['repos_using_boost']:,}",
        f"- **Total Boost Libraries**: {stats['total_libraries']:,}",
        f"- **Total Boost Headers**: {stats['total_headers']:,}",
        f"- **Total Usage Records**: {stats['total_usage_records']:,}",
        "",
        "**Note on Repository Counts**: \"Repositories Using Boost\" counts distinct repositories that depend on external/system Boost. This may be less than \"Total Repositories\" because repositories with vendored Boost bundle their own copy of Boost rather than using external Boost, so their Boost includes are filtered out during processing.",
        "",
        "## Top Boost Libraries by Repository Count",
        "",
        "| Library | Repository Count | Usage Count |",
        "|---------|------------------|-------------|",
    ]
    
    for lib in stats["top_libraries"]:
        report_lines.append(
            f"| {lib['name']} | {lib['repo_count']:,} | {lib['usage_count']:,} |"
        )
    
    report_lines.extend([
        "",
        "## Top Boost Headers by Repository Count",
        "",
        "| Header | Repository Count | Usage Count |",
        "|--------|------------------|-------------|",
    ])
    
    for header in stats["top_headers"]:
        report_lines.append(
            f"| {header['header']} | {header['repo_count']:,} | {header['usage_count']:,} |"
        )
    
    if stats["version_distribution"]:
        report_lines.extend([
            "",
            "## Boost Version Distribution (Top 10)",
            "",
            "| Version | Usage Count |",
            "|---------|-------------|",
        ])
        for version, count in stats["version_distribution"]:
            report_lines.append(f"| {version} | {count:,} |")
    
    report_lines.extend(appendics())
    
    REPORT_MD.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Report written to {REPORT_MD.relative_to(BASE_DIR)}")

def appendics() -> list(str):
    return [
        "",
        "## Data Processing Procedure",
        "",
        "This report is generated from BigQuery exports containing Boost-related files from GitHub repositories. The processing procedure consists of the following steps:",
        "",
        "### 1. BigQuery Data Production",
        "",
        "**The most important step**: Data is produced by executing `query.sql` in Google BigQuery against the `bigquery-public-data.github_repos` dataset. This query:",
        "",
        "- Detects repositories containing Boost includes in C/C++ source files",
        "- Identifies repositories with vendored Boost (containing `boost/` folder)",
        "- Extracts Boost version information from multiple sources:",
        "  - `boost/version.hpp` files (BOOST_VERSION macro)",
        "  - CMake `find_package(Boost ...)` declarations",
        "  - Conan `conanfile.txt` or `conanfile.py` references",
        "  - vcpkg `vcpkg.json` manifest files",
        "- Retrieves latest commit metadata for each repository",
        "- Outputs results to CSV files (`bq-results-*`) exported to the data directory",
        "",
        "The query produces CSV files with the following key fields:",
        "",
        "- `repo_name`: GitHub repository identifier",
        "- `path`: File path within the repository",
        "- `file_content`: Full file content (for include extraction)",
        "- `boost_version`: Detected Boost version (if found)",
        "- `contains_vendored_boost`: Boolean indicating if repository has vendored Boost",
        "- `last_commit_ts`: Timestamp of the most recent commit",
        "",
        "### 2. Data Collection",
        "",
        "- Scan all `bq-results-*` CSV files in the data directory (including subdirectories)",
        "- Extract `#include <boost/...>` and `#include \"boost/...\"` directives from file contents",
        "- Parse repository metadata from CSV fields",
        "",
        "### 3. Version Detection",
        "",
        "Boost version is determined in priority order:",
        "",
        "1. From the `boost_version` field in the CSV (populated by `query.sql` from version detection sources)",
        "2. If CSV field is empty, extracted from file paths containing patterns like:",
        "   - `/boost_1_57_0/` → `1.57.0`",
        "   - `/boost-1.70.0/` → `1.70.0`",
        "   - `/boost1.76.0/` → `1.76.0`",
        "",
        "**Note on Missing Version Information**: Some repositories may not have Boost version information available because:",
        "",
        "- The repository uses system Boost installed via package managers (apt, yum, brew, etc.) without explicit version declarations in build files",
        "- Version information is specified in documentation or README files rather than in machine-readable build configuration files",
        "- The repository uses Boost headers directly without any dependency management system (CMake, Conan, vcpkg)",
        "- The repository's build system doesn't explicitly declare Boost as a dependency",
        "- Version information exists in files that are not scanned by the query (e.g., CI configuration files, Dockerfiles, or other non-standard locations)",
        "",
        "### 4. Data Filtering",
        "",
        "Usage records are excluded if:",
        "",
        "- The file path contains `/boost` AND the repository has `contains_vendored_boost = true`",
        "",
        "This ensures that vendored Boost headers within repository directories are not counted as external Boost usage.",
        "",
        "### 5. Database Construction",
        "",
        "A relational SQLite database is built with the following tables:",
        "",
        "- **`boost_library`**: Unique Boost libraries",
        "- **`boost_header`**: Headers mapped to their parent library",
        "- **`repository`**: GitHub repositories with `affect_from_boost` flag (1 if using system Boost, 0 if vendored) and detected `boost_version`",
        "- **`boost_usage`**: Individual usage records linking repositories to headers with file paths and commit timestamps",
        "",
    ]
    
def main():
    print("Step 1: Collecting data from data directory...")
    data = collect_usage_data()
    
    print("\nStep 2: Building database...")
    usage_count = build_database(data)
    print(f"Inserted {usage_count:,} usage records into database.")
    
    print("\nStep 3: Generating statistics...")
    stats = generate_statistics()
    
    print("\nStep 4: Writing statistics CSV...")
    write_statistics_csv()
    
    print("\nStep 5: Writing summary report...")
    write_report(stats)
    
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
