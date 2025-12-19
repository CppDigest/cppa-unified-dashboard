"""
Create dashboard HTML files for Boost library usage analysis.

This script generates:
1. index.html - Main dashboard with overview statistics
2. {library_name}.html - Individual library pages with detailed information

The script is organized into two main modules:
1. collect_dashboard_data() - Collects all data from database and saves to dashboard_data.json
2. generate_dashboard_html() - Reads dashboard_data.json and generates HTML files
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any

from dateutil import parser as date_parser

from config import DB_PATH, DB_PATH_1, DASHBOARD_DIR


# Create libraries subdirectory
LIBRARIES_DIR = DASHBOARD_DIR / "libraries"
LIBRARIES_DIR.mkdir(exist_ok=True, parents=True)

# Dashboard data JSON file
DASHBOARD_DATA_FILE = DASHBOARD_DIR / "dashboard_data.json"


def version_sort_key(version: str) -> tuple:
    """Convert version string to tuple for sorting."""
    if not version:
        return (0, 0, 0)
    parts = version.split('.')
    return tuple(int(p) if p.isdigit() else 0 for p in parts[:3])


def _parse_any_datetime(raw: str) -> Optional[datetime]:
    """Parse various datetime formats used in DB (ISO, RFC, human text). Returns naive UTC-ish datetime."""
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        dt = date_parser.parse(raw)
        # normalize tz-aware to naive for comparisons
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except (ValueError, TypeError, OverflowError):
        return None


def create_index_html_from_data(data: Dict[str, Any]) -> None:
    """Create index.html from pre-collected data."""
    # Extract data
    repos_by_year = data.get("repos_by_year", [])
    repos_by_version = data.get("repos_by_version", [])
    top20_libs = data.get("top20_libs", [])
    bottom20_libs = data.get("bottom20_libs", [])
    activity_metrics = data.get("activity_metrics", {})
    top20_active = activity_metrics.get("top_20", [])
    bottom20_active = activity_metrics.get("bottom_20", [])
    all_libraries = data.get("all_libraries", [])
    top20_by_stars = data.get("top20_by_stars", [])
    top20_by_usage = data.get("top20_by_usage", [])
    top20_by_created = data.get("top20_by_created", [])

    # Process data for charts
    year_labels = [row["year"] for row in repos_by_year]
    year_counts = [row["count"] for row in repos_by_year]
    version_labels = [row["version"] for row in repos_by_version]
    version_counts = [row["count"] for row in repos_by_version]

    # Build HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Boost Library Usage Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>{_get_index_css()}</style>
</head>
<body>
    <h1>📊 Boost Library Usage Dashboard</h1>
    <p style="text-align: center; color: #666;">Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>

    <!-- Panel 1: Counts of created repositories used boost library by year -->
    <div class="panel">
        <h2>Counts of Created Repositories Used Boost Library by Year</h2>
        <div class="chart-container">
            <canvas id="reposByYearChart"></canvas>
        </div>
    </div>

    <!-- Panel 2: Counts of Created Repositories Used Boost by Version -->
    <div class="panel">
        <h2>Counts of Created Repositories Used Boost by Version</h2>
        <div class="chart-container">
            <canvas id="reposByVersionChart"></canvas>
        </div>
    </div>

    <!-- Panel 3: Top 20 and Bottom 20 repositories -->
    <div class="panel">
        <h2>Top 20 and Bottom 20 Libraries by Usage Count</h2>
        <div class="tables-container-2">
            <div>
                <h3>Top 20 Libraries</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Library</th>
                            <th>Usage Count</th>
                        </tr>
                    </thead>
{_build_library_table_html(top20_libs)}
                </table>
            </div>
            <div>
                <h3>Bottom 20 Libraries</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Library</th>
                            <th>Usage Count</th>
                        </tr>
                    </thead>
{_build_library_table_html(bottom20_libs)}
                </table>
            </div>
        </div>
    </div>

    <!-- Panel 4: Top 20 repositories by star, by boost usage count, and by last created -->
    <div class="panel">
        <h2>Top 20 Repositories by Different Metrics</h2>
        <div class="tables-container-3-wrapper">
            <div class="tables-container-3">
                <div>
                    <h3>By Stars</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Repository</th>
                                <th>Stars</th>
                                <th>Usage Count</th>
                                <th>Created</th>
                            </tr>
                        </thead>
{_build_repo_table_html(top20_by_stars)}
                    </table>
                </div>
                <div>
                    <h3>By Boost Usage Count</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Repository</th>
                                <th>Stars</th>
                                <th>Usage Count</th>
                                <th>Created</th>
                            </tr>
                        </thead>
{_build_repo_table_html(top20_by_usage)}
                    </table>
                </div>
                <div>
                    <h3>By Last Created</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Repository</th>
                                <th>Stars</th>
                                <th>Usage Count</th>
                                <th>Created</th>
                            </tr>
                        </thead>
{_build_repo_table_html(top20_by_created)}
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Panel 5: Most Active Libraries (Recent vs Past Activity) -->
    <div class="panel">
        <h2>Most Active Libraries (Recent vs Past Activity)</h2>
        <p style="color: #666; margin-top: 0;">
            Comparing library activity in the last <strong>5 years</strong> versus earlier years.
            Libraries with higher recent activity relative to past activity indicate growing adoption.
        </p>
        <div class="tables-container-2">
            <div>
                <h3>Top 20 Most Active Libraries</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Library</th>
                            <th>Recent Usage</th>
                            <th>Past Usage</th>
                            <th>Total Usage</th>
                            <th>Activity Ratio</th>
                            <th>Activity %</th>
                            <th>Activity Score</th>
                        </tr>
                    </thead>
{_build_activity_table_html(top20_active)}
                </table>
            </div>
            <div>
                <h3>Bottom 20 Least Active Libraries</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Library</th>
                            <th>Recent Usage</th>
                            <th>Past Usage</th>
                            <th>Total Usage</th>
                            <th>Activity Ratio</th>
                            <th>Activity %</th>
                            <th>Activity Score</th>
                        </tr>
                    </thead>
{_build_activity_table_html(bottom20_active)}
                </table>
            </div>
        </div>
    </div>

    <!-- Panel 6: All Libraries -->
    <div class="panel">
        <h2>All Libraries</h2>
        <p style="color: #666; margin-top: 0;">Click on any library to view detailed statistics.</p>
        <div class="library-grid">
"""
    for lib_name in all_libraries:
        html_content += f'            <div class="library-item"><a href="libraries/{lib_name}.html">{lib_name}</a></div>\n'

    html_content += f"""        </div>
    </div>

    <script>
        {_build_chart_js("reposByYearChart", year_labels, year_counts, "Repository Count", "rgba(54, 162, 235, 0.6)")}
        {_build_chart_js_with_rotation("reposByVersionChart", version_labels, version_counts, "Repository Count", "rgba(75, 192, 192, 0.6)")}
    </script>
</body>
</html>
"""

    index_file = DASHBOARD_DIR / "index.html"
    index_file.write_text(html_content, encoding="utf-8")
    print(f"Created {index_file}")


# Legacy functions removed - use create_index_html_from_data() and create_library_html_from_data() instead


def create_library_html_from_data(data: Dict[str, Any], library_name: str) -> None:
    """Create HTML file for a specific library from pre-collected data."""
    libraries_data = data.get("libraries", {})
    lib_data = libraries_data.get(library_name, {})

    if not lib_data:
        print(f"Warning: No data found for library {library_name}")
        return

    # Extract data
    dependents_table_data = lib_data.get("dependents_table_data", [])
    dependents_by_version = lib_data.get("dependents_by_version", {})
    top_repos = lib_data.get("top_repos", [])
    usage_by_year = lib_data.get("usage_by_year", {})
    contributors = lib_data.get("contributors", [])
    commits_by_version = lib_data.get("commits_by_version", {})

    latest_version_str = data.get("latest_version_str", "N/A")

    # Process data for charts
    dep_versions = sorted(dependents_by_version.keys(), key=version_sort_key)
    dep_counts = [dependents_by_version[v] for v in dep_versions]
    usage_years = sorted(usage_by_year.keys())
    usage_counts = [usage_by_year[y] for y in usage_years]
    commit_versions = sorted(commits_by_version.keys())
    commit_counts = [commits_by_version[y] for y in commit_versions]

    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{library_name} - Boost Library Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>{_get_library_css()}</style>
</head>
<body>
    <div class="back-link">
        <a href="../index.html">← Back to Dashboard</a>
    </div>
    <h1>📚 {library_name}</h1>

    <!-- Panel 1: Internal dependents -->
    <div class="panel">
        <h2>Internal dependents</h2>
        <div class="panel-row">
            <div>
                <table>
                    <thead>
                        <tr>
                            <th colspan="4">dependents Libraries (Latest Version: {latest_version_str})</th>
                        </tr>
                    </thead>
                    <tbody>
{_build_dependents_table_html(dependents_table_data)}
                    </tbody>
                </table>
            </div>
            <div class="chart-container">
                <canvas id="dependentsChart"></canvas>
            </div>
        </div>
    </div>

    <!-- Panel 2: External dependents -->
    <div class="panel">
        <h2>External dependents</h2>
        <div class="panel-row">
            <div>
                <table>
                    <thead>
                        <tr>
                            <th>Repository</th>
                            <th>Stars</th>
                            <th>Usage Count</th>
                        </tr>
                    </thead>
{_build_top_repos_table_html(top_repos)}
                </table>
            </div>
            <div class="chart-container">
                <canvas id="usageChart"></canvas>
            </div>
        </div>
    </div>

    <!-- Panel 3: Contribution -->
    <div class="panel">
        <h2>Contribution</h2>
        <div class="panel-row">
            <div>
                <table>
                    <thead>
                        <tr>
                            <th>Contributor</th>
                            <th>Commit Count</th>
                        </tr>
                    </thead>
{_build_contributor_table_html(contributors)}
                </table>
            </div>
            <div class="chart-container">
                <canvas id="commitChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        {_build_chart_js_with_rotation("dependentsChart", dep_versions, dep_counts, "dependents Count", "rgba(75, 192, 192, 0.6)")}
        {_build_chart_js("usageChart", usage_years, usage_counts, "Usage Count", "rgba(54, 162, 235, 0.6)")}
        {_build_chart_js("commitChart", [str(v) for v in commit_versions], commit_counts, "Commit Count", "rgba(255, 99, 132, 0.6)")}
    </script>
</body>
</html>
"""

    library_file = LIBRARIES_DIR / f"{library_name}.html"
    library_file.write_text(html_content, encoding="utf-8")
    print(f"Created {library_file}")


def _rows_to_list(rows: List[Any]) -> List[Dict[str, Any]]:
    """Convert list of Row objects to list of dictionaries."""
    return [dict(row) for row in rows]


# ===== HTML Template Functions =====

def _build_chart_js(chart_id: str, labels: List[str], data: List[int], label: str, color: str = "rgba(54, 162, 235, 0.6)") -> str:
    """Build Chart.js JavaScript code for a bar chart."""
    labels_json = json.dumps(labels)
    data_json = json.dumps(data)
    return f"""
        new Chart(document.getElementById('{chart_id}'), {{
            type: 'bar',
            data: {{
                labels: {labels_json},
                datasets: [{{
                    label: '{label}',
                    data: {data_json},
                    backgroundColor: '{color}',
                    borderColor: '{color.replace("0.6", "1")}',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        display: true
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    """


def _build_chart_js_with_rotation(chart_id: str, labels: List[str], data: List[int], label: str, color: str = "rgba(75, 192, 192, 0.6)") -> str:
    """Build Chart.js JavaScript code for a bar chart with rotated x-axis labels."""
    labels_json = json.dumps(labels)
    data_json = json.dumps(data)
    return f"""
        new Chart(document.getElementById('{chart_id}'), {{
            type: 'bar',
            data: {{
                labels: {labels_json},
                datasets: [{{
                    label: '{label}',
                    data: {data_json},
                    backgroundColor: '{color}',
                    borderColor: '{color.replace("0.6", "1")}',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        display: true
                    }}
                }},
                scales: {{
                    x: {{
                        ticks: {{
                            autoSkip: true,
                            maxRotation: 90,
                            minRotation: 45
                        }}
                    }},
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    """


def _build_library_table_html(libraries: List[Dict[str, Any]], link_prefix: str = "libraries/") -> str:
    """Build HTML table for library list."""
    html = """
                    <tbody>
"""
    for lib in libraries:
        lib_name = lib.get("library_name", lib.get("name", ""))
        usage_count = lib.get("usage_count", 0)
        html += f"""
                        <tr>
                            <td><a href="{link_prefix}{lib_name}.html">{lib_name}</a></td>
                            <td>{usage_count:,}</td>
                        </tr>
"""
    html += """
                    </tbody>
"""
    return html


def _build_repo_table_html(repos: List[Dict[str, Any]]) -> str:
    """Build HTML table for repository list."""
    html = """
                    <tbody>
"""
    for repo in repos:
        repo_name = repo.get("repo_name", "")
        stars = repo.get("stars", 0) or "N/A"
        usage_count = repo.get("usage_count", 0)
        created = repo.get("created_at", "")[:10] if repo.get("created_at") else "N/A"
        html += f"""
                        <tr>
                            <td><a href="https://github.com/{repo_name}" target="_blank">{repo_name}</a></td>
                            <td>{stars if isinstance(stars, str) else f'{stars:,}'}</td>
                            <td>{usage_count:,}</td>
                            <td>{created}</td>
                        </tr>
"""
    html += """
                    </tbody>
"""
    return html


def _build_activity_table_html(libs: List[Dict[str, Any]]) -> str:
    """Build HTML table for library activity metrics."""
    html = """
                    <tbody>
"""
    for lib in libs:
        html += f"""
                        <tr>
                            <td><a href="libraries/{lib['name']}.html">{lib['name']}</a></td>
                            <td>{lib['recent_usage']:,}</td>
                            <td>{lib['past_usage']:,}</td>
                            <td>{lib['total_usage']:,}</td>
                            <td>{lib['recent_activity_ratio']:.2f}</td>
                            <td>{lib['recent_activity_percentage']:.1f}%</td>
                            <td>{lib['activity_score']:.3f}</td>
                        </tr>
"""
    html += """
                    </tbody>
"""
    return html


def _build_dependents_table_html(dependents: List[str]) -> str:
    """Build HTML table for dependents (4 columns per row)."""
    if not dependents:
        return """
                <tr>
                    <td colspan="4">No dependencies found</td>
                </tr>
"""
    html = ""
    deps = list(dependents)
    for i in range(0, len(deps), 4):
        chunk = deps[i:i + 4]
        while len(chunk) < 4:
            chunk.append("")
        html += "<tr>"
        for dep in chunk:
            if dep:
                html += f'<td><a href="{dep}.html">{dep}</a></td>'
            else:
                html += "<td></td>"
        html += "</tr>\n"
    return html


def _build_contributor_table_html(contributors: List[Dict[str, Any]]) -> str:
    """Build HTML table for contributors."""
    html = """
                    <tbody>
"""
    if contributors:
        for contrib in contributors:
            name = contrib.get('identity_name', contrib.get('email_address', 'N/A'))
            count = contrib.get('commit_count', 0)
            html += f"""
                <tr>
                    <td>{name}</td>
                    <td>{count:,}</td>
                </tr>
"""
    else:
        html += """
                <tr>
                    <td colspan="2">No commit data available (boost_commit table not yet populated)</td>
                </tr>
"""
    html += """
                    </tbody>
"""
    return html


def _build_top_repos_table_html(repos: List[Dict[str, Any]]) -> str:
    """Build HTML table for top repositories."""
    html = """
                    <tbody>
"""
    if repos:
        for repo in repos:
            html += f"""
                <tr>
                    <td><a href="https://github.com/{repo['repo_name']}" target="_blank">{repo['repo_name']}</a></td>
                    <td>{repo['stars']:,}</td>
                    <td>{repo['usage_count']:,}</td>
                </tr>
"""
    else:
        html += """
                <tr>
                    <td colspan="3">No repositories found</td>
                </tr>
"""
    html += """
                    </tbody>
"""
    return html

def _get_index_css() -> str:
    """Return CSS styles for index.html."""
    return """
        body {
            font-family: Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        .panel {
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .panel h2 {
            margin-top: 0;
            color: #2d3748;
        }
        .chart-container {
            margin: 20px 0;
            height: 420px;
        }
        canvas {
            width: 100% !important;
            height: 100% !important;
            display: block;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f0f0f0;
            font-weight: 600;
        }
        tr:hover {
            background-color: #f9f9f9;
        }
        a {
            color: #0066cc;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .tables-container-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .tables-container-3 {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 20px;
            align-items: start;
        }
        .tables-container-3 > div {
            min-width: 0;
        }
        .tables-container-3 table {
            width: 100%;
            table-layout: fixed;
        }
        .tables-container-3 th, .tables-container-3 td {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .tables-container-3-wrapper {
            overflow-x: auto;
        }
        .library-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 8px 16px;
            margin-top: 12px;
        }
        .library-item {
            padding: 6px 10px;
            border: 1px solid #eee;
            border-radius: 6px;
            background: #fafafa;
            font-size: 14px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        @media (max-width: 1200px) {
            .tables-container-3 {
                grid-template-columns: 1fr;
            }
            .tables-container-2 {
                grid-template-columns: 1fr;
            }
        }
    """


def _get_library_css() -> str:
    """Return CSS styles for library HTML files."""
    return """
        body {
            font-family: Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        .panel {
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .panel h2 {
            margin-top: 0;
            color: #2d3748;
        }
        .chart-container {
            margin: 20px 0;
            height: 380px;
        }
        canvas {
            width: 100% !important;
            height: 100% !important;
            display: block;
        }
        .panel-row {
            display: grid;
            grid-template-columns: 1.2fr 1fr;
            gap: 20px;
            align-items: start;
        }
        .panel-row .chart-container {
            margin: 0;
        }
        .panel-row table {
            margin: 0;
        }
        @media (max-width: 1100px) {
            .panel-row {
                grid-template-columns: 1fr;
            }
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f0f0f0;
            font-weight: 600;
        }
        tr:hover {
            background-color: #f9f9f9;
        }
        a {
            color: #0066cc;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .back-link {
            margin-bottom: 20px;
        }
    """


# ===== Data Collection Functions =====

def _collect_index_data(db: Any, db1: Any) -> Dict[str, Any]:
    """Collect all data needed for index.html."""
    from analyze_boost_usage import calculate_library_activity_metrics
    data: Dict[str, Any] = {}

    # Repos by year
    repos_by_year = db.fetchall(
        """
        SELECT
            SUBSTR(r.created_at, 1, 4) AS year,
            COUNT(DISTINCT r.id) AS count
        FROM repository r
        JOIN boost_usage bu ON bu.repository_id = r.id
        WHERE r.created_at IS NOT NULL
          AND r.created_at != ''
          AND LENGTH(r.created_at) >= 4
          AND bu.excepted_ts IS NULL
          AND r.stars IS NOT NULL
          AND r.stars >= 10
        GROUP BY year
        HAVING year >= '2002' AND year <= ?
        ORDER BY year
        """,
        (str(datetime.now().year),),
    )
    data["repos_by_year"] = _rows_to_list(repos_by_year)

    # Repos by version
    repos_by_version = db.fetchall(
        """
        SELECT
            bv.version AS version,
            COUNT(DISTINCT r.id) AS count
        FROM repository r
        JOIN boost_version bv
          ON bv.id = COALESCE(r.boost_version_id, r.candidate_version_id)
        WHERE COALESCE(r.boost_version_id, r.candidate_version_id) IS NOT NULL
          AND r.stars IS NOT NULL
          AND r.stars >= 10
        GROUP BY bv.version
        ORDER BY bv.version
        """
    )
    data["repos_by_version"] = _rows_to_list(repos_by_version)

    # Top 20 and Bottom 20 libraries
    top20_libs = db.fetchall("""
        SELECT
            bl.name AS library_name,
            COUNT(bu.id) AS usage_count
        FROM boost_library bl
        JOIN boost_header bh ON bh.library_id = bl.id
        JOIN boost_usage bu ON bu.header_id = bh.id
        JOIN repository r ON r.id = bu.repository_id
        WHERE bu.excepted_ts IS NULL
          AND r.stars IS NOT NULL
          AND r.stars >= 10
        GROUP BY bl.id, bl.name
        ORDER BY usage_count DESC
        LIMIT 20
    """)
    data["top20_libs"] = _rows_to_list(top20_libs)

    bottom20_libs = db.fetchall("""
        SELECT
            bl.name AS library_name,
            COUNT(bu.id) AS usage_count
        FROM boost_library bl
        JOIN boost_header bh ON bh.library_id = bl.id
        JOIN boost_usage bu ON bu.header_id = bh.id
        JOIN repository r ON r.id = bu.repository_id
        WHERE bu.excepted_ts IS NULL
          AND r.stars IS NOT NULL
          AND r.stars >= 10
        GROUP BY bl.id, bl.name
        HAVING usage_count > 0
        ORDER BY usage_count ASC
        LIMIT 20
    """)
    data["bottom20_libs"] = _rows_to_list(bottom20_libs)

    # Library Activity Metrics
    activity_metrics = calculate_library_activity_metrics(recent_years=5)
    data["activity_metrics"] = {
        "top_20": activity_metrics.get("top_10", []),
        "bottom_20": activity_metrics.get("bottom_10", []),
    }

    # All libraries list
    all_libraries = db.fetchall("SELECT name FROM boost_library ORDER BY name")
    data["all_libraries"] = [row["name"] for row in all_libraries]

    # Top 20 repos by different metrics
    data["top20_by_stars"] = _rows_to_list(db.fetchall("""
        SELECT
            r.repo_name,
            r.stars,
            COUNT(bu.id) as usage_count,
            r.created_at
        FROM repository r
        LEFT JOIN boost_usage bu ON r.id = bu.repository_id AND bu.excepted_ts IS NULL
        WHERE r.stars IS NOT NULL AND r.stars >= 10
        GROUP BY r.id
        ORDER BY r.stars DESC
        LIMIT 20
    """))

    data["top20_by_usage"] = _rows_to_list(db.fetchall("""
        SELECT
            r.repo_name,
            r.stars,
            COUNT(bu.id) as usage_count,
            r.created_at
        FROM repository r
        JOIN boost_usage bu ON r.id = bu.repository_id
        WHERE bu.excepted_ts IS NULL
          AND r.stars IS NOT NULL
          AND r.stars >= 10
        GROUP BY r.id
        ORDER BY usage_count DESC
        LIMIT 20
    """))

    data["top20_by_created"] = _rows_to_list(db.fetchall("""
        SELECT
            r.repo_name,
            r.stars,
            COUNT(bu.id) as usage_count,
            r.created_at
        FROM repository r
        LEFT JOIN boost_usage bu ON r.id = bu.repository_id AND bu.excepted_ts IS NULL
        WHERE r.created_at IS NOT NULL AND r.created_at != ''
          AND r.stars IS NOT NULL
          AND r.stars >= 10
        GROUP BY r.id
        ORDER BY r.created_at DESC
        LIMIT 20
    """))

    return data


def _collect_library_data(
    db: Any, db1: Any,
    lib_id: int,
    library_name: str,
    latest_version_id: Optional[int],
    latest_version_str: Optional[str],
    table_exists: bool,
) -> Dict[str, Any]:
    """Collect data for a single library."""
    lib_data: Dict[str, Any] = {}

    # Panel 1: Internal dependents
    dependents_table_data = []
    dependents_by_version = {}

    if latest_version_id and table_exists:
        dependencies = db.fetchall("""
            SELECT
                bl.name as dep_library_name,
                ld.version_id
            FROM library_dependency ld
            JOIN boost_library bl ON ld.dependency_library_id = bl.id
            WHERE ld.main_library_id = ? AND ld.version_id = ?
            ORDER BY bl.name
        """, (lib_id, latest_version_id))

        dependents_table_data = [row["dep_library_name"] for row in dependencies]

        dep_by_version_rows = db.fetchall("""
            SELECT
                bv.version,
                COUNT(DISTINCT ld.dependency_library_id) as dep_count
            FROM library_dependency ld
            JOIN boost_version bv ON ld.version_id = bv.id
            WHERE ld.main_library_id = ?
            GROUP BY bv.version
            ORDER BY bv.major, bv.minor, bv.patch
        """, (lib_id,))

        for row in dep_by_version_rows:
            version = row["version"]
            dep_count = row["dep_count"]
            if version:
                dependents_by_version[version] = int(dep_count or 0)

    lib_data["dependents_table_data"] = dependents_table_data
    lib_data["dependents_by_version"] = dependents_by_version

    # Panel 2: External dependents
    lib_data["top_repos"] = _rows_to_list(db.fetchall("""
        SELECT
            r.repo_name,
            r.stars,
            COUNT(bu.id) as usage_count
        FROM repository r
        JOIN boost_usage bu ON r.id = bu.repository_id
        JOIN boost_header bh ON bu.header_id = bh.id
        WHERE bh.library_id = ?
            AND bu.excepted_ts IS NULL
            AND r.stars IS NOT NULL AND r.stars >= 10
        GROUP BY r.id
        ORDER BY r.stars DESC
        LIMIT 10
    """, (lib_id,)))

    usage_by_year_rows = db.fetchall("""
        SELECT
            SUBSTR(bu.last_commit_ts, 1, 4) as year,
            COUNT(bu.id) as usage_count
        FROM boost_usage bu
        JOIN boost_header bh ON bu.header_id = bh.id
        JOIN repository r ON r.id = bu.repository_id
        WHERE bh.library_id = ?
            AND bu.excepted_ts IS NULL
            AND bu.last_commit_ts IS NOT NULL
            AND LENGTH(bu.last_commit_ts) >= 4
            AND r.stars IS NOT NULL
            AND r.stars >= 10
        GROUP BY year
        HAVING year >= '2000' AND year <= ?
        ORDER BY year
    """, (lib_id, str(datetime.now().year)))
    lib_data["usage_by_year"] = {
        row["year"]: row["usage_count"]
        for row in usage_by_year_rows
    }

    # Panel 3: Contribution
    nick_name = "logic" if library_name == "tribool" else library_name
    version_for_query = latest_version_str.replace(".0", "") if latest_version_str else None
    contributors = []
    commits_by_version = {}

    if version_for_query:
        contributors = db1.fetchall("""
            SELECT
                email_address,
                identity_name,
                count(*) as commit_count
            FROM contributor_data
            WHERE repo = ?
            AND version = ?
            GROUP BY email_address
            ORDER BY commit_count DESC
        """, (nick_name, version_for_query))

        commits_by_version_rows = db1.fetchall("""
            SELECT
                version,
                count(*) as commit_count
            FROM contributor_data
            WHERE repo = ?
            AND version LIKE '%1.%'
            GROUP BY version
            ORDER BY version
        """, (nick_name,))
        commits_by_version = {
            row["version"]: row["commit_count"]
            for row in commits_by_version_rows
        }

    lib_data["contributors"] = _rows_to_list(contributors)
    lib_data["commits_by_version"] = commits_by_version

    return lib_data


def collect_dashboard_data() -> None:
    """
    Collect all data needed for dashboard generation from databases.
    Saves the data to dashboard_data.json.
    """
    print("Collecting dashboard data from databases...")
    from sqlite_connector import SQLiteConnector

    with SQLiteConnector(DB_PATH) as db, SQLiteConnector(DB_PATH_1) as db1:
        # Collect index data
        dashboard_data = _collect_index_data(db, db1)

        # Collect library data
        libraries = db.fetchall("SELECT id, name FROM boost_library ORDER BY name")

        latest_version_rows = db.fetchall("""
            SELECT id, version FROM boost_version
            ORDER BY major DESC, minor DESC, patch DESC
            LIMIT 2
        """)
        latest_version_id = latest_version_rows[0]["id"] if latest_version_rows else None
        latest_version_str = latest_version_rows[0]["version"] if latest_version_rows else None

        table_exists = db.table_exists("library_dependency")

        libraries_data: Dict[str, Dict[str, Any]] = {}
        for lib_row in libraries:
            lib_id = lib_row["id"]
            library_name = lib_row["name"]
            libraries_data[library_name] = _collect_library_data(
                db, db1, lib_id, library_name, latest_version_id, latest_version_str, table_exists
            )

        dashboard_data["libraries"] = libraries_data
        dashboard_data["latest_version_id"] = latest_version_id
        dashboard_data["latest_version_str"] = latest_version_str

        # Save to JSON
        with open(DASHBOARD_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)

        print(f"Dashboard data collected and saved to {DASHBOARD_DATA_FILE}")
        print(f"  - Index data: {len(dashboard_data.get('all_libraries', []))} libraries")
        print(f"  - Library data: {len(libraries_data)} libraries")


def generate_dashboard_html() -> None:
    """
    Read dashboard_data.json and generate all HTML files.
    """
    print("Generating HTML files from dashboard data...")

    # Load data from JSON
    with open(DASHBOARD_DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Generate index.html
    print("Creating index.html...")
    create_index_html_from_data(data)

    # Generate library HTML files
    libraries_data = data.get("libraries", {})
    print(f"Creating HTML files for {len(libraries_data)} libraries...")

    for library_name in libraries_data:
        create_library_html_from_data(data, library_name)

    print("Dashboard generation complete!")


def main():
    """Main entry point: collect data and generate HTML."""
    collect_dashboard_data()
    generate_dashboard_html()


if __name__ == "__main__":
    main()

