from __future__ import annotations

import csv
import os
import sqlite3
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data/file_time"
STATS_CSV = BASE_DIR / "boost_usage_statistics.csv"
REPORT_MD = BASE_DIR / "boost_analysis" / "Boost_Usage_Report.md"
DB_PATH = Path(__file__).resolve().parent / "boost_usage.db"
BOOST_RELEASE_DATE_CSV = BASE_DIR / "data" / "boost_release_date.csv"

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
    if parsed.year > 2025:
        parsed.year = parsed.year - 26
    return int(parsed.timestamp())


def parse_boolean(raw: str) -> bool:
    raw = (raw or "").strip().upper()
    return raw in ("TRUE", "1", "YES", "T")


def isoformat(epoch_seconds: Optional[int], empty: bool = False) -> Optional[str]:
    if epoch_seconds is None:
        return "" if empty else None
    return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def iter_data_files() -> Iterable[Path]:
    """
    Iterate over all data files in the data directory.
    Includes both BigQuery exports (bq-results-*) and GitHub API results (github-api-results-*).
    """
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Missing data directory: {DATA_DIR}")

    # Find both BigQuery exports and GitHub API results
    bq_files = sorted(DATA_DIR.rglob("bq-results-*"))
    github_files = sorted(DATA_DIR.rglob("github-api-results-*"))

    # Combine and return all files
    all_files = sorted(set(bq_files) | set(github_files))
    return all_files


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


def load_boost_release_dates() -> List[tuple]:
    """
    Load Boost release dates from CSV file.
    Returns list of (version_string, release_timestamp) tuples, sorted by release date descending.
    Example: [("1.89.0", 1754438400), ("1.88.0", 1743638400), ...]
    """
    if not BOOST_RELEASE_DATE_CSV.exists():
        print(f"Warning: Boost release date file not found: {BOOST_RELEASE_DATE_CSV}")
        return []

    releases = []
    with BOOST_RELEASE_DATE_CSV.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            name = (row.get("name") or "").strip()
            release_date_str = (row.get("release_date") or "").strip()

            if not name or not release_date_str:
                continue

            # Extract version from name (e.g., "boost-1.89.0" -> "1.89.0")
            match = re.search(r'boost-(\d+\.\d+(?:\.\d+)?)', name)
            if not match:
                continue

            version = match.group(1)

            # Parse release date (format: "8/6/2025" or "4/3/2025")
            try:
                # Try different date formats
                for fmt in ["%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d"]:
                    try:
                        release_date = datetime.strptime(release_date_str, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    # If all formats fail, skip this row
                    continue

                # Convert to timestamp
                release_timestamp = int(release_date.replace(tzinfo=timezone.utc).timestamp())
                releases.append((version, release_timestamp))
            except Exception as e:
                print(f"Warning: Could not parse release date '{release_date_str}' for {name}: {e}")
                continue

    # Sort by release date descending (newest first)
    releases.sort(key=lambda x: x[1], reverse=True)
    return releases


def find_candidate_version(last_commit_ts: Optional[int], release_dates: List[tuple]) -> Optional[str]:
    """
    Find the candidate Boost version based on last_commit_ts.
    Returns the latest Boost version that was released on or before the commit timestamp.
    """
    if last_commit_ts is None or not release_dates:
        return None

    # Find the latest version released on or before the commit timestamp
    for version, release_ts in release_dates:
        if release_ts <= last_commit_ts:
            return version

    # If commit is older than all releases, return the oldest version
    if release_dates:
        return release_dates[-1][0]

    return None

def normalize_version(version:str) -> str:
    """_summary_

    Args:
        version (str): _description_

    Returns:
        str: _description_
    """
    # Normalize version string (handle variations like "1.80.0" vs "1.80")
    version_normalized = version.strip()

    # Normalize to have exactly 3 parts (major.minor.patch)
    # e.g., "1.80" -> "1.80.0", "1.80.0" -> "1.80.0"
    version_parts = version_normalized.split(".")
    if len(version_parts) == 2:
        version_normalized = f"{version_parts[0]}.{version_parts[1]}.0"

    if len(version_parts) >= 2:
        if int(version_parts[1]) < 10:
            if len(version_parts) == 3:
                version_normalized = f"{version_parts[0]}.{version_parts[1]}{version_parts[2]}.0"
            else:
                version_normalized = f"{version_parts[0]}.{version_parts[1]}0.0"

    elif len(version_parts) == 1:
        version_normalized = f"{version_parts[0]}.0.0"
    return version_normalized

def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings.

    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """
    def version_tuple(v: str) -> tuple:
        """Convert version string to tuple of integers for comparison."""
        if not v:
            return (0, 0, 0)

        # Split by dot and extract numeric parts
        parts = v.split('.')
        result = []

        for part in parts[:3]:  # Only take first 3 parts (major.minor.patch)
            # Extract numeric part (handle cases like "1.53" or "1.53.0")
            numeric_part = ''.join(c for c in part if c.isdigit())
            if numeric_part:
                result.append(int(numeric_part))
            else:
                result.append(0)

        # Pad with zeros to ensure same length (major.minor.patch)
        while len(result) < 3:
            result.append(0)

        return tuple(result[:3])

    try:
        v1_tuple = version_tuple(version1)
        v2_tuple = version_tuple(version2)
        if v1_tuple < v2_tuple:
            return -1
        elif v1_tuple > v2_tuple:
            return 1
        else:
            return 0
    except (ValueError, AttributeError, TypeError):
        # If parsing fails, treat as equal (conservative approach)
        return 0


def get_release_year_for_version(version: str, release_dates: List[tuple]) -> Optional[int]:
    """
    Get the release year for a given Boost version.
    Returns the year when the version was released, or None if not found.
    """
    if not version or not release_dates:
        return None

    # Find exact match first
    for ver, release_ts in release_dates:
        if ver == version:
            release_date = datetime.fromtimestamp(release_ts, tz=timezone.utc)
            return release_date.year

    # Try matching without patch version (e.g., "1.80" should match "1.80.0")
    version_major_minor = ".".join(version.split(".")[:2])
    for ver, release_ts in release_dates:
        ver_major_minor = ".".join(ver.split(".")[:2])
        if ver_major_minor == version_major_minor:
            release_date = datetime.fromtimestamp(release_ts, tz=timezone.utc)
            return release_date.year

    return None


def load_csv_data_and_build_boost_usage():
    """
    Step 1: Load CSV data and construct boost_usage table.

    This function:
    1. Reads CSV files and extracts Boost includes
    2. Creates temporary repository entries (minimal info)
    3. Inserts boost_usage records directly into the database

    Returns: Statistics about the loading process
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    # Create tables if they don't exist
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
            affect_from_boost INTEGER NOT NULL DEFAULT 0,
            boost_version TEXT,
            candidate_version TEXT
        );

        CREATE TABLE IF NOT EXISTS boost_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repository_id INTEGER NOT NULL,
            file_path TEXT NOT NULL,
            header_id INTEGER NOT NULL,
            last_commit_ts TEXT,
            boost_version TEXT,
            affect_from_boost INTEGER NOT NULL DEFAULT 0,
            excepted_ts TEXT,
            FOREIGN KEY (repository_id) REFERENCES repository(id),
            FOREIGN KEY (header_id) REFERENCES boost_header(id)
        );
        """
    )

    # Check if boost_header table has data
    header_count = conn.execute("SELECT COUNT(*) FROM boost_header").fetchone()[0]
    if header_count == 0:
        print("Warning: boost_header table is empty. Please run populate_boost_headers.py first.")
        conn.close()
        return {"error": "boost_header table is empty"}

    # Build header_id lookup cache
    header_id_cache: Dict[str, Optional[int]] = {}
    for row in conn.execute("SELECT id, full_header_name FROM boost_header WHERE full_header_name IS NOT NULL"):
        header_id, full_header_name = row
        if full_header_name:
            header_id_cache[full_header_name] = header_id

    for row in conn.execute("SELECT id, header_name, full_header_name FROM boost_header"):
        header_id, header_name, full_header_name = row
        if not full_header_name or full_header_name == header_name:
            if header_name not in header_id_cache:
                header_id_cache[header_name] = header_id

    # Statistics
    total_rows = 0
    total_includes = 0
    excluded_count = 0
    usage_rows = []
    unmatched_headers = set()
    repo_name_to_id: Dict[str, int] = {}  # Temporary mapping for CSV processing

    # Load CSV data and build boost_usage records
    print("Step 1: Loading CSV data and constructing boost_usage table...")
    for csv_path in iter_data_files():
        print(f"  Scanning {csv_path.name} ...")
        with csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                total_rows += 1
                repo_name = (row.get("repo_name") or "").strip()
                if not repo_name:
                    continue

                file_path = (row.get("path") or "").strip()
                contains_vendored = parse_boolean(row.get("contains_vendored_boost", ""))
                boost_version = (row.get("boost_version") or "").strip() or None
                last_commit = parse_timestamp(row.get("last_commit_ts", ""))

                # Extract version from path if CSV field is empty
                if not boost_version:
                    boost_version = extract_version_from_path(file_path)

                # Get or create repository entry (minimal - will be updated later)
                if repo_name not in repo_name_to_id:
                    # Check if repository already exists
                    existing = conn.execute(
                        "SELECT id FROM repository WHERE repo_name = ?",
                        (repo_name,),
                    ).fetchone()

                    if existing:
                        repo_id = existing[0]
                    else:
                        # Create minimal repository entry
                        affect_from_boost = 1 if not contains_vendored else 0
                        cur = conn.execute(
                            "INSERT INTO repository (repo_name, affect_from_boost) VALUES (?, ?)",
                            (repo_name, affect_from_boost),
                        )
                        repo_id = cur.lastrowid
                    repo_name_to_id[repo_name] = repo_id
                else:
                    repo_id = repo_name_to_id[repo_name]

                # Extract Boost includes
                includes = extract_boost_includes(row.get("file_content", ""))
                if not includes:
                    continue

                for header in includes:
                    total_includes += 1

                    # Check if we should exclude this usage
                    if should_exclude_usage(file_path, contains_vendored):
                        excluded_count += 1
                        continue

                    # Look up header_id
                    header_id = header_id_cache.get(header)
                    if header_id is None:
                        unmatched_headers.add(header)
                        continue

                    # Calculate affect_from_boost (1 if using system Boost, 0 if vendored)
                    affect_from_boost = 1 if not contains_vendored else 0

                    # Prepare usage record (now includes boost_version and affect_from_boost)
                    usage_rows.append((
                        repo_id,
                        file_path,
                        header_id,
                        isoformat(last_commit),
                        boost_version,  # Store version in boost_usage table
                        affect_from_boost,  # Store affect_from_boost in boost_usage table
                        None,  # excepted_ts
                    ))

    # Insert all usage records
    if usage_rows:
        print(f"  Inserting {len(usage_rows):,} usage records...")
        conn.executemany(
            "INSERT INTO boost_usage (repository_id, file_path, header_id, last_commit_ts, boost_version, affect_from_boost, excepted_ts) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            usage_rows,
        )
        conn.commit()

    if unmatched_headers:
        print(f"  Warning: {len(unmatched_headers)} unique headers not found in boost_header table:")
        for h in sorted(unmatched_headers)[:10]:
            print(f"    - {h}")
        if len(unmatched_headers) > 10:
            print(f"    ... and {len(unmatched_headers) - 10} more")

    conn.close()

    conn.close()

    stats = {
        "total_rows": total_rows,
        "total_includes": total_includes,
        "excluded_count": excluded_count,
        "usage_records_inserted": len(usage_rows),
        "unmatched_headers": len(unmatched_headers),
    }

    print(f"  Completed: {stats['usage_records_inserted']:,} usage records inserted.")
    return stats


def load_boost_usage_from_table():
    """
    Step 2: Load boost_usage data from the database table.

    Aggregates data from boost_usage to determine repository-level information:
    - Latest commit timestamp per repository
    - Boost versions (from boost_usage.boost_version field)
    - File paths (for fallback version extraction if needed)
    - Repository IDs

    Returns: Dictionary with repository-level aggregated data
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    print("Step 2: Loading boost_usage data from table...")

    # Aggregate usage data per repository
    repo_data = {}

    # Get all usage records with repository, file path, version, affect_from_boost, and commit info
    query = """
        SELECT
            r.id as repo_id,
            r.repo_name,
            bu.file_path,
            bu.last_commit_ts,
            bu.boost_version,
            bu.affect_from_boost
        FROM boost_usage bu
        JOIN repository r ON bu.repository_id = r.id
        WHERE bu.excepted_ts IS NULL
    """

    for row in conn.execute(query):
        repo_id = row["repo_id"]
        repo_name = row["repo_name"]
        file_path = row["file_path"]
        commit_ts = row["last_commit_ts"]
        boost_version = row["boost_version"]
        affect_from_boost = row["affect_from_boost"]
        if commit_ts:
            try:
                # Parse ISO format timestamp (e.g., "2022-11-26T00:18:53Z")
                commit_dt = datetime.fromisoformat(commit_ts.replace("Z", "+00:00"))
                if commit_dt < datetime(2013, 1, 1, tzinfo=timezone.utc):
                    continue
            except (ValueError, AttributeError):
                # If parsing fails, skip this record
                continue

        if repo_id not in repo_data:
            repo_data[repo_id] = {
                "repo_name": repo_name,
                "file_paths": [],
                "commit_timestamps": [],
                "boost_versions": [],  # Collect all versions from usage records
                "affect_from_boost_values": [],  # Collect all affect_from_boost values
            }

        repo_data[repo_id]["file_paths"].append(file_path)
        if commit_ts:
            repo_data[repo_id]["commit_timestamps"].append(commit_ts)
        if boost_version:
            repo_data[repo_id]["boost_versions"].append(boost_version)
        repo_data[repo_id]["affect_from_boost_values"].append(affect_from_boost)

    conn.close()

    print(f"  Loaded data for {len(repo_data)} repositories")
    return repo_data


def update_repository_table(repo_data):
    """
    Step 3: Update repository table based on boost_usage data.

    This function uses ONLY data from the boost_usage table:
    1. Extracts Boost version from boost_usage.boost_version field (priority)
    2. Falls back to extracting version from file paths if not in boost_usage
    3. Calculates latest commit timestamp per repository
    4. Calculates candidate_version based on commit timestamps
    5. Updates repository table with this information

    Args:
        repo_data: Dictionary from load_boost_usage_from_table()
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    print("Step 3: Updating repository table...")

    # Load Boost release dates for candidate version calculation
    print("  Loading Boost release dates...")
    release_dates = load_boost_release_dates()
    print(f"  Loaded {len(release_dates)} Boost release dates")

    updates = []

    for repo_id, data in repo_data.items():
        file_paths = data["file_paths"]
        commit_timestamps = data["commit_timestamps"]
        boost_versions = data.get("boost_versions", [])
        affect_from_boost_values = data.get("affect_from_boost_values", [])

        # Priority 1: Get version from boost_usage.boost_version field
        boost_version = None
        if boost_versions:
            # Use the most common version, or first non-null if all unique
            version_counts = Counter(boost_versions)
            if version_counts:
                boost_version = version_counts.most_common(1)[0][0]

        # Priority 2: Extract version from file paths if not found in boost_usage
        if not boost_version:
            for file_path in file_paths:
                version = extract_version_from_path(file_path)
                if version:
                    boost_version = version
                    break

        # Determine affect_from_boost from boost_usage data
        # If any usage record has affect_from_boost=1, the repository is affected
        # (uses system Boost, not vendored)
        affect_from_boost = 0
        if affect_from_boost_values:
            # If any record indicates affect_from_boost=1, set to 1
            # This means at least some files use system Boost
            if any(val == 1 for val in affect_from_boost_values):
                affect_from_boost = 1

        # Find latest commit timestamp
        latest_commit_ts = None
        if commit_timestamps:
            # Parse timestamps and find the latest
            parsed_timestamps = []
            for ts_str in commit_timestamps:
                try:
                    # Parse ISO format timestamp
                    dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    parsed_timestamps.append(int(dt.timestamp()))
                except (ValueError, AttributeError):
                    continue

            if parsed_timestamps:
                latest_commit_ts = min(parsed_timestamps)

        # Calculate candidate_version based on latest commit
        candidate_version = find_candidate_version(latest_commit_ts, release_dates)

        updates.append({
            "repo_id": repo_id,
            "boost_version": boost_version,
            "candidate_version": candidate_version,
            "affect_from_boost": affect_from_boost,
        })

    # Update repository table
    updated_count = 0
    with conn:
        for update in updates:
            conn.execute(
                """UPDATE repository
                   SET boost_version = COALESCE(?, boost_version),
                       candidate_version = COALESCE(?, candidate_version),
                       affect_from_boost = ?
                   WHERE id = ?""",
                (update["boost_version"], update["candidate_version"], update["affect_from_boost"], update["repo_id"]),
            )
            updated_count += 1

    conn.close()
    print(f"  Updated {updated_count} repository records")
    return updated_count


def generate_statistics():
    """Generate statistics from the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Load release dates for version validation
    release_dates = load_boost_release_dates()

    stats = {}

    # Overall statistics
    stats["total_repositories"] = conn.execute("SELECT COUNT(*) FROM repository").fetchone()[0]
    stats["affected_repositories"] = conn.execute(
        "SELECT COUNT(*) FROM repository WHERE affect_from_boost = 1"
    ).fetchone()[0]
    stats["total_headers"] = conn.execute("SELECT COUNT(*) FROM boost_header").fetchone()[0]
    stats["total_libraries"] = conn.execute("SELECT COUNT(*) FROM boost_library").fetchone()[0]
    stats["total_usage_records"] = conn.execute("SELECT COUNT(*) FROM boost_usage").fetchone()[0]

    # Version statistics (from repository table)
    # Only use boost_version, not candidate_version
    # Get ALL versions (not just top 10) so dashboard can filter to 1.53.0-1.80.0 range
    version_stats = conn.execute(
        """
        SELECT
            boost_version as version,
            COUNT(*) as cnt
        FROM repository
        WHERE boost_version IS NOT NULL
            AND boost_version != ''
        GROUP BY boost_version
        ORDER BY cnt DESC
        """
    ).fetchall()
    version_distribution = {}
    for row in version_stats:
        version_name = normalize_version(row["version"])

        version_distribution[version_name] = version_distribution.get(version_name, 0) + row["cnt"]

    # Sort by version number, starting from 1.50.0
    # Filter versions >= 1.50.0 and sort them numerically
    min_version = "1.50.0"
    filtered_items = [
        (version, count) for version, count in version_distribution.items()
        if compare_versions(version, min_version) >= 0
    ]

    # Sort by version number (ascending) - convert version to tuple for proper numeric sorting
    def version_sort_key(item):
        version = item[0]
        parts = version.split('.')
        return tuple(int(p) if p.isdigit() else 0 for p in parts[:3])

    filtered_items.sort(key=version_sort_key, reverse=True)

    stats["version_distribution"] = filtered_items

    # Version coverage statistics
    repos_with_version = conn.execute(
        "SELECT COUNT(*) FROM repository WHERE boost_version IS NOT NULL AND boost_version != ''"
    ).fetchone()[0]
    stats["repos_with_version"] = repos_with_version
    stats["repos_without_version"] = stats["total_repositories"] - repos_with_version
    stats["version_coverage_percent"] = (
        (repos_with_version / stats["total_repositories"] * 100)
        if stats["total_repositories"] > 0 else 0
    )

    # Top libraries by repository count with time ranges
    top_libraries = conn.execute(
        """
        SELECT
            bl.name,
            COUNT(bu.id) as usage_count,
            COUNT(DISTINCT bu.repository_id) as repo_count,
            MIN(bu.last_commit_ts) as earliest_commit,
            MAX(bu.last_commit_ts) as latest_commit
        FROM boost_library bl
        JOIN boost_header bh ON bl.id = bh.library_id
        JOIN boost_usage bu ON bh.id = bu.header_id
        WHERE bu.excepted_ts IS NULL
        GROUP BY bl.id, bl.name
        ORDER BY repo_count DESC
        LIMIT 150
        """
    ).fetchall()
    stats["top_libraries"] = [
        {
            "name": row["name"],
            "usage_count": row["usage_count"],
            "repo_count": row["repo_count"],
            "earliest_commit": row["earliest_commit"] or "",
            "latest_commit": row["latest_commit"] or "",
        }
        for row in top_libraries
    ]

    # Bottom libraries by repository count with time ranges
    bottom_libraries = conn.execute(
        """
        SELECT
            bl.name,
            COUNT(bu.id) as usage_count,
            COUNT(DISTINCT bu.repository_id) as repo_count,
            MIN(bu.last_commit_ts) as earliest_commit,
            MAX(bu.last_commit_ts) as latest_commit
        FROM boost_library bl
        JOIN boost_header bh ON bl.id = bh.library_id
        JOIN boost_usage bu ON bh.id = bu.header_id
        WHERE bu.excepted_ts IS NULL
        GROUP BY bl.id, bl.name
        HAVING repo_count > 0
        ORDER BY repo_count ASC
        LIMIT 20
        """
    ).fetchall()
    stats["bottom_libraries"] = [
        {
            "name": row["name"],
            "usage_count": row["usage_count"],
            "repo_count": row["repo_count"],
            "earliest_commit": row["earliest_commit"] or "",
            "latest_commit": row["latest_commit"] or "",
        }
        for row in bottom_libraries
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

    # Repository counts by year (based on latest commit timestamp per repository)
    # Get latest commit per repository, then extract year
    repos_by_year_raw = conn.execute(
        """
        SELECT
            bu.repository_id,
            MAX(bu.last_commit_ts) as latest_commit
        FROM boost_usage bu
        WHERE bu.last_commit_ts IS NOT NULL
            AND bu.last_commit_ts != ''
            AND LENGTH(bu.last_commit_ts) >= 4
        GROUP BY bu.repository_id
        """
    ).fetchall()

    # Extract year from timestamps and count
    year_counts = {}
    for row in repos_by_year_raw:
        commit_ts = row[1]
        if commit_ts and len(commit_ts) >= 4:
            try:
                # Extract year from ISO format (YYYY-MM-DD...)
                year_str = commit_ts[:4]
                if year_str.isdigit():
                    year = int(year_str)
                    if 2000 <= year <= datetime.now().year:
                        year_counts[year] = year_counts.get(year, 0) + 1
            except (ValueError, TypeError):
                continue

    stats["repos_by_year"] = sorted(year_counts.items(), reverse=True)

    # Repository counts by year AND version
    # Get latest commit per repository with version info, then extract year
    # Only use boost_version, not candidate_version
    repos_by_year_version_raw = conn.execute(
        """
        SELECT
            bu.repository_id,
            MAX(bu.last_commit_ts) as latest_commit,
            r.boost_version as version
        FROM boost_usage bu
        JOIN repository r ON bu.repository_id = r.id
        WHERE bu.last_commit_ts IS NOT NULL
            AND bu.last_commit_ts != ''
            AND LENGTH(bu.last_commit_ts) >= 4
            AND r.boost_version IS NOT NULL
            AND r.boost_version != ''
        GROUP BY bu.repository_id, r.boost_version
        """
    ).fetchall()

    # Build nested dict: {version: {year: count}}
    version_year_counts = {}
    for row in repos_by_year_version_raw:
        commit_ts = row[1]
        version = row[2]

        if not version or not commit_ts or len(commit_ts) < 4:
            continue
        version = normalize_version(version)

        try:
            # Extract year from ISO format (YYYY-MM-DD...)
            year_str = commit_ts[:4]
            if year_str.isdigit():
                year = int(year_str)
                if 2014 <= year <= datetime.now().year:
                    # Get release year for this version
                    release_year = get_release_year_for_version(version, release_dates)

                    # Ensure year is at least as recent as release year
                    # If release_year is known, use the maximum of commit year and release year
                    if release_year is not None:
                        year = max(year, release_year)

                    if version not in version_year_counts:
                        version_year_counts[version] = {}
                    version_year_counts[version][year] = version_year_counts[version].get(year, 0) + 1
        except (ValueError, TypeError):
            continue

    # Convert to list of dicts for easier JSON serialization
    # Format: [{"version": "1.89.0", "year": 2024, "count": 123}, ...]
    stats["repos_by_year_version"] = []
    for version, year_data in sorted(version_year_counts.items()):
        for year, count in sorted(year_data.items()):
            stats["repos_by_year_version"].append({
                "version": version,
                "year": year,
                "count": count
            })

    # Also create a summary dict for easier access: {version: [(year, count), ...]}
    stats["repos_by_year_version_dict"] = {
        version: sorted(year_data.items())
        for version, year_data in version_year_counts.items()
    }

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
        # Get most common version if multiple (using COALESCE result)
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
        "## Data Source and Date Range",
        "",
        "**Data Source Reference**: The BigQuery public dataset can be accessed at: https://console.cloud.google.com/bigquery?ws=!1m5!1m4!4m3!1sbigquery-public-data!2sgithub_repos!3sfiles",
        "",
        "**Important**: This report is generated from BigQuery data covering the period **2002-2022**. The BigQuery dataset (`bigquery-public-data.github_repos`) was last updated on **2022-11-27**, which means:",
        "- All commit timestamps in this report are from commits made on or before 2022-11-27",
        "- Repository activity after 2022-11-27 is not included in this analysis",
        "- The \"latest commit\" dates shown in the statistics reflect the most recent commit in the dataset, not necessarily the current state of repositories",
        "",

        "## Overview",
        "",
        f"- **Total Repositories**: {stats['total_repositories']:,}",
        f"- **Repositories Using System Boost**: {stats['affected_repositories']:,}",
        f"- **Total Boost Libraries**: {stats['total_libraries']:,}",
        f"- **Total Boost Headers**: {stats['total_headers']:,}",
        f"- **Total Usage Records**: {stats['total_usage_records']:,}",
        "",
        "**Note on Repository Counts**: \"Repositories Using Boost\" counts distinct repositories that depend on external/system Boost. This may be less than \"Total Repositories\" because repositories with vendored Boost bundle their own copy of Boost rather than using external Boost, so their Boost includes are filtered out during processing.",
        "",
        "## Top Boost Libraries by Repository Count",
        "",
        "| Library | Repository Count | Usage Count | Earliest Commit | Latest Commit |",
        "|---------|------------------|-------------|-----------------|---------------|",
    ]

    for lib in stats["top_libraries"]:
        earliest = lib.get("earliest_commit", "") or "N/A"
        latest = lib.get("latest_commit", "") or "N/A"
        report_lines.append(
            f"| {lib['name']} | {lib['repo_count']:,} | {lib['usage_count']:,} | {earliest} | {latest} |"
        )

    if stats.get("bottom_libraries"):
        report_lines.extend([
            "",
            "## Bottom Boost Libraries by Repository Count",
            "",
            "| Library | Repository Count | Usage Count | Earliest Commit | Latest Commit |",
            "|---------|------------------|-------------|-----------------|---------------|",
        ])

        for lib in stats["bottom_libraries"]:
            earliest = lib.get("earliest_commit", "") or "N/A"
            latest = lib.get("latest_commit", "") or "N/A"
            report_lines.append(
                f"| {lib['name']} | {lib['repo_count']:,} | {lib['usage_count']:,} | {earliest} | {latest} |"
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

    if stats.get("repos_by_year"):
        report_lines.extend([
            "",
            "## Repository Counts by Year",
            "",
            "This table shows the number of repositories using Boost, grouped by the year of their latest commit.",
            "",
            "| Year | Repository Count |",
            "|------|------------------|",
        ])
        for year, count in stats["repos_by_year"]:
            report_lines.append(f"| {year} | {count:,} |")

    report_lines.extend([
        "## Version Coverage Statistics",
        "",
        f"- **Repositories with Detected Boost Version**: {stats.get('repos_with_version', 0):,}",
        f"- **Repositories without Detected Version**: {stats.get('repos_without_version', 0):,}",
        f"- **Version Coverage**: {stats.get('version_coverage_percent', 0):.1f}%",
        "",
        "**Note**: Version detection relies on explicit version declarations in build files (CMake, Conan, vcpkg) or `boost/version.hpp` files. Repositories using system Boost installed via package managers may not have explicit version declarations.",
        "",
    ])

    if stats["version_distribution"]:
        report_lines.extend([
            "",
            "## Boost Version Distribution",
            "",
            "| Version | Usage Count |",
            "|---------|-------------|",
        ])
        for version, count in stats["version_distribution"]:
            report_lines.append(f"| {version} | {count:,} |")

    if stats.get("repos_by_year_version_dict"):
        report_lines.extend([
            "",
            "## Repository Counts by Year and Version",
            "",
            "This table shows the number of repositories using Boost, grouped by both the Boost version and the year of their latest commit.",
            "",
            "**Note**: This section only includes Boost versions for which version information was successfully detected in the repository data. Versions are shown starting from Boost 1.53.0 and later, as earlier versions may not have explicit version declarations in build files or may use different version detection methods. The absence of earlier versions in this table does not indicate they were not used, but rather that version information was not reliably detected for those repositories.",
            "",
        ])

        # Filter out versions below 1.53.0
        min_version = "1.53.0"
        filtered_versions = [
            version for version in stats["repos_by_year_version_dict"].keys()
            if compare_versions(version, min_version) >= 0
        ]

        if filtered_versions:
            # Collect all unique years
            all_years = set()
            for version in filtered_versions:
                year_data = stats["repos_by_year_version_dict"][version]
                for year, _ in year_data:
                    all_years.add(year)

            # Sort years descending (newest first)
            sorted_years = sorted(all_years, reverse=True)

            # Sort versions descending (newest first)
            def version_sort_key(v):
                parts = v.split('.')
                return tuple(int(p) if p.isdigit() else 0 for p in parts[:3])

            sorted_versions = sorted(filtered_versions, key=version_sort_key, reverse=True)

            # Build the pivot table
            # Header row
            header = "| Year |"
            separator = "|------|"
            for version in sorted_versions:
                header += f" {version} |"
                separator += "--------|"
            report_lines.append(header)
            report_lines.append(separator)

            # Data rows
            for year in sorted_years:
                row = f"| {year} |"
                for version in sorted_versions:
                    year_data = stats["repos_by_year_version_dict"][version]
                    # Find count for this year
                    count = 0
                    for y, c in year_data:
                        if y == year:
                            count = c
                            break
                    row += f" {count:,} |" if count > 0 else " |"
                report_lines.append(row)

            report_lines.append("")

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
    # Step 1: Load CSV data and construct boost_usage table
    # stats = load_csv_data_and_build_boost_usage()
    # if stats.get("error"):
    #     print("Cannot proceed without boost_header data. Exiting.")
    #     return

    # Step 2: Load boost_usage data from table
    # repo_data = load_boost_usage_from_table()

    # # Step 3: Update repository table based on boost_usage data
    # update_repository_table(repo_data)

    print("\nStep 4: Generating statistics...")
    stats = generate_statistics()

    print("\nStep 5: Writing statistics CSV...")
    write_statistics_csv()

    print("\nStep 6: Writing summary report...")
    write_report(stats)

    print("\nStep 7: Generating interactive visualization...")
    try:
        from generate_visualization import generate_html_dashboard
        generate_html_dashboard(stats)
        print("Interactive dashboard generated successfully!")
    except ImportError:
        print("Warning: Could not import visualization module. Skipping dashboard generation.")

    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()
