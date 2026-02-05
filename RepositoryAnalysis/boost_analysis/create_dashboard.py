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
    # Calculate cumulative counts for years
    year_cumulative = []
    cumulative_sum = 0
    for count in year_counts:
        cumulative_sum += count
        year_cumulative.append(cumulative_sum)

    version_labels = [row["version"] for row in repos_by_version]
    version_counts = [row["count"] for row in repos_by_version]
    # Calculate cumulative counts for versions
    version_cumulative = []
    cumulative_sum = 0
    for count in version_counts:
        cumulative_sum += count
        version_cumulative.append(cumulative_sum)

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
        {_build_dual_chart_js("reposByYearChart", year_labels, year_counts, year_cumulative, "Yearly Count", "Cumulative Total", "rgba(54, 162, 235, 0.6)", "rgba(255, 99, 132, 0.8)")}
        {_build_dual_chart_js_with_rotation("reposByVersionChart", version_labels, version_counts, version_cumulative, "Version Count", "Cumulative Total", "rgba(75, 192, 192, 0.6)", "rgba(255, 159, 64, 0.8)")}
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

    # Always use latest version from boost_version table for the table
    latest_version_id = lib_data.get("latest_version_id")
    # Get latest version string from data
    latest_version_str = data.get("latest_version_str", "N/A")
    if latest_version_id:
        versions = data.get("versions_info", {})
        if isinstance(versions, dict) and latest_version_id in versions:
            latest_version_str = versions[latest_version_id]

    # Process data for charts - handle new structure with first_level and all_deeper
    # Get all versions from 1.66.0 to 1.90.0 from data
    all_versions_list = data.get("all_versions_for_chart", [])
    if not all_versions_list:
        # Fallback: get from dependents_by_version if not in data
        dep_versions = sorted(dependents_by_version.keys(), key=version_sort_key)
    else:
        dep_versions = sorted(all_versions_list, key=version_sort_key)

    first_level_counts = []
    all_deeper_counts = []

    for version in dep_versions:
        version_data = dependents_by_version.get(version, {})
        if isinstance(version_data, dict):
            first_level_counts.append(version_data.get("first_level", 0))
            all_deeper_counts.append(version_data.get("all_deeper", 0))
        elif isinstance(version_data, int):
            # Fallback for old format
            first_level_counts.append(version_data)
            all_deeper_counts.append(0)
        else:
            # No data for this version, set to 0
            first_level_counts.append(0)
            all_deeper_counts.append(0)

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
        <p style="color: #666; margin-top: 0; margin-bottom: 15px;">
            Showing all dependencies (direct and transitive) for the latest version with dependents.
            Colors indicate depth: <span style="color: #3b82f6; font-weight: 600;">Blue (d1)</span> = Direct,
            <span style="color: #10b981; font-weight: 600;">Green (d2)</span> = Second level,
            <span style="color: #f59e0b; font-weight: 600;">Orange (d3+)</span> = Deeper levels.
        </p>
        <div class="panel-row">
            <div>
                <table>
                    <thead>
                        <tr>
                            <th colspan="4">Dependent Libraries (Latest Version: {latest_version_str})</th>
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
        {_build_dependents_chart_js("dependentsChart", dep_versions, first_level_counts, all_deeper_counts)}
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


def _build_dual_chart_js(
    chart_id: str,
    labels: List[str],
    bar_data: List[int],
    line_data: List[int],
    bar_label: str,
    line_label: str,
    bar_color: str = "rgba(54, 162, 235, 0.6)",
    line_color: str = "rgba(255, 99, 132, 0.8)"
) -> str:
    """Build Chart.js JavaScript code for a dual chart (bar + line for cumulative)."""
    labels_json = json.dumps(labels)
    bar_data_json = json.dumps(bar_data)
    line_data_json = json.dumps(line_data)
    return f"""
        new Chart(document.getElementById('{chart_id}'), {{
            type: 'bar',
            data: {{
                labels: {labels_json},
                datasets: [{{
                    label: '{bar_label}',
                    type: 'bar',
                    data: {bar_data_json},
                    backgroundColor: '{bar_color}',
                    borderColor: '{bar_color.replace("0.6", "1")}',
                    borderWidth: 2,
                    borderRadius: 4,
                    order: 2
                }}, {{
                    label: '{line_label}',
                    type: 'line',
                    data: {line_data_json},
                    borderColor: '{line_color}',
                    backgroundColor: 'transparent',
                    borderWidth: 3,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: '{line_color}',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    fill: false,
                    tension: 0.3,
                    yAxisID: 'y1',
                    order: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{
                    mode: 'index',
                    intersect: false
                }},
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top',
                        labels: {{
                            usePointStyle: true,
                            padding: 15,
                            font: {{
                                size: 13,
                                weight: '500'
                            }}
                        }}
                    }},
                    tooltip: {{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: {{
                            size: 14,
                            weight: 'bold'
                        }},
                        bodyFont: {{
                            size: 13
                        }},
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        displayColors: true,
                        callbacks: {{
                            label: function(context) {{
                                let label = context.dataset.label || '';
                                if (label) {{
                                    label += ': ';
                                }}
                                if (context.parsed.y !== null) {{
                                    label += context.parsed.y.toLocaleString();
                                }}
                                return label;
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        type: 'linear',
                        display: true,
                        position: 'left',
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: '{bar_label}',
                            font: {{
                                size: 12,
                                weight: '600'
                            }},
                            color: '{bar_color.replace("0.6", "1")}'
                        }},
                        ticks: {{
                            callback: function(value) {{
                                return value.toLocaleString();
                            }},
                            font: {{
                                size: 11
                            }}
                        }},
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.05)'
                        }}
                    }},
                    y1: {{
                        type: 'linear',
                        display: true,
                        position: 'right',
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: '{line_label}',
                            font: {{
                                size: 12,
                                weight: '600'
                            }},
                            color: '{line_color}'
                        }},
                        ticks: {{
                            callback: function(value) {{
                                return value.toLocaleString();
                            }},
                            font: {{
                                size: 11
                            }}
                        }},
                        grid: {{
                            drawOnChartArea: false
                        }}
                    }},
                    x: {{
                        ticks: {{
                            font: {{
                                size: 11
                            }}
                        }},
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.05)'
                        }}
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


def _build_dual_chart_js_with_rotation(
    chart_id: str,
    labels: List[str],
    bar_data: List[int],
    line_data: List[int],
    bar_label: str,
    line_label: str,
    bar_color: str = "rgba(75, 192, 192, 0.6)",
    line_color: str = "rgba(255, 159, 64, 0.8)"
) -> str:
    """Build Chart.js JavaScript code for a dual chart (bar + line for cumulative) with rotated x-axis labels."""
    labels_json = json.dumps(labels)
    bar_data_json = json.dumps(bar_data)
    line_data_json = json.dumps(line_data)
    return f"""
        new Chart(document.getElementById('{chart_id}'), {{
            type: 'bar',
            data: {{
                labels: {labels_json},
                datasets: [{{
                    label: '{bar_label}',
                    type: 'bar',
                    data: {bar_data_json},
                    backgroundColor: '{bar_color}',
                    borderColor: '{bar_color.replace("0.6", "1")}',
                    borderWidth: 2,
                    borderRadius: 4,
                    order: 2
                }}, {{
                    label: '{line_label}',
                    type: 'line',
                    data: {line_data_json},
                    borderColor: '{line_color}',
                    backgroundColor: 'transparent',
                    borderWidth: 3,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: '{line_color}',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    fill: false,
                    tension: 0.3,
                    yAxisID: 'y1',
                    order: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{
                    mode: 'index',
                    intersect: false
                }},
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top',
                        labels: {{
                            usePointStyle: true,
                            padding: 15,
                            font: {{
                                size: 13,
                                weight: '500'
                            }}
                        }}
                    }},
                    tooltip: {{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: {{
                            size: 14,
                            weight: 'bold'
                        }},
                        bodyFont: {{
                            size: 13
                        }},
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        displayColors: true,
                        callbacks: {{
                            label: function(context) {{
                                let label = context.dataset.label || '';
                                if (label) {{
                                    label += ': ';
                                }}
                                if (context.parsed.y !== null) {{
                                    label += context.parsed.y.toLocaleString();
                                }}
                                return label;
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        type: 'linear',
                        display: true,
                        position: 'left',
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: '{bar_label}',
                            font: {{
                                size: 12,
                                weight: '600'
                            }},
                            color: '{bar_color.replace("0.6", "1")}'
                        }},
                        ticks: {{
                            callback: function(value) {{
                                return value.toLocaleString();
                            }},
                            font: {{
                                size: 11
                            }}
                        }},
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.05)'
                        }}
                    }},
                    y1: {{
                        type: 'linear',
                        display: true,
                        position: 'right',
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: '{line_label}',
                            font: {{
                                size: 12,
                                weight: '600'
                            }},
                            color: '{line_color}'
                        }},
                        ticks: {{
                            callback: function(value) {{
                                return value.toLocaleString();
                            }},
                            font: {{
                                size: 11
                            }}
                        }},
                        grid: {{
                            drawOnChartArea: false
                        }}
                    }},
                    x: {{
                        ticks: {{
                            autoSkip: true,
                            maxRotation: 90,
                            minRotation: 45,
                            font: {{
                                size: 11
                            }}
                        }},
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.05)'
                        }}
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
                            <td>{lib['derivation_score']:.3f}</td>
                        </tr>
"""
    html += """
                    </tbody>
"""
    return html


def _build_dependents_table_html(dependents: List[Dict[str, Any]]) -> str:
    """
    Build HTML table for dependents with depth-based coloring (4 columns per row).

    Args:
        dependents: List of dicts with "name" and "depth" keys, or list of strings (for backward compatibility)
    """
    if not dependents:
        return """
                <tr>
                    <td colspan="4">No dependencies found</td>
                </tr>
"""
    # Handle backward compatibility: if list of strings, convert to dicts
    if dependents and isinstance(dependents[0], str):
        dependents = [{"name": dep, "depth": 1} for dep in dependents]

    # Depth color mapping: depth 1 = blue, depth 2 = green, depth 3+ = orange/red
    depth_colors = {
        1: "#3b82f6",  # Blue
        2: "#10b981",  # Green
        3: "#f59e0b",  # Orange
        4: "#ef4444",  # Red
    }

    html = ""
    for i in range(0, len(dependents), 4):
        chunk = dependents[i:i + 4]
        while len(chunk) < 4:
            chunk.append(None)
        html += "<tr>"
        for dep in chunk:
            if dep:
                depth = dep.get("depth", 1) if isinstance(dep, dict) else 1
                name = dep.get("name", dep) if isinstance(dep, dict) else str(dep)
                color = depth_colors.get(depth, depth_colors.get(4, "#6b7280"))
                html += f'<td style="background-color: {color}20; border-left: 3px solid {color};"><a href="{name}.html" style="color: {color}; font-weight: {"bold" if depth == 1 else "normal"};">{name}</a> <span style="color: {color}; font-size: 0.85em; opacity: 0.7;">(d{depth})</span></td>'
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


def _build_dependents_chart_js(
    chart_id: str,
    versions: List[str],
    first_level_data: List[int],
    all_deeper_data: List[int]
) -> str:
    """Build Chart.js JavaScript code for dependents chart with two datasets per version."""
    versions_json = json.dumps(versions)
    first_level_json = json.dumps(first_level_data)
    all_deeper_json = json.dumps(all_deeper_data)

    return f"""
        new Chart(document.getElementById('{chart_id}'), {{
            type: 'bar',
            data: {{
                labels: {versions_json},
                datasets: [{{
                    label: 'First-Level Dependencies',
                    data: {first_level_json},
                    backgroundColor: 'rgba(59, 130, 246, 0.7)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 2,
                    borderRadius: 4
                }}, {{
                    label: 'All Deeper Dependencies',
                    data: {all_deeper_json},
                    backgroundColor: 'rgba(16, 185, 129, 0.7)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 2,
                    borderRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{
                    mode: 'index',
                    intersect: false
                }},
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top',
                        labels: {{
                            usePointStyle: true,
                            padding: 15,
                            font: {{
                                size: 13,
                                weight: '500'
                            }}
                        }}
                    }},
                    tooltip: {{
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: {{
                            size: 14,
                            weight: 'bold'
                        }},
                        bodyFont: {{
                            size: 13
                        }},
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        displayColors: true,
                        callbacks: {{
                            label: function(context) {{
                                let label = context.dataset.label || '';
                                if (label) {{
                                    label += ': ';
                                }}
                                if (context.parsed.y !== null) {{
                                    label += context.parsed.y.toLocaleString();
                                }}
                                return label;
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        ticks: {{
                            autoSkip: true,
                            maxRotation: 90,
                            minRotation: 45,
                            font: {{
                                size: 11
                            }}
                        }},
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.05)'
                        }}
                    }},
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Dependency Count',
                            font: {{
                                size: 12,
                                weight: '600'
                            }}
                        }},
                        ticks: {{
                            callback: function(value) {{
                                return value.toLocaleString();
                            }},
                            font: {{
                                size: 11
                            }}
                        }},
                        grid: {{
                            color: 'rgba(0, 0, 0, 0.05)'
                        }}
                    }}
                }}
            }}
        }});
    """


def _get_index_css() -> str:
    """Return CSS styles for index.html."""
    return """
        * {
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            max-width: 1600px;
            margin: 0 auto;
            padding: 30px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        h1 {
            text-align: center;
            color: #fff;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            font-weight: 700;
        }
        body > p {
            text-align: center;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 30px;
            font-size: 0.95em;
        }
        .panel {
            background: #ffffff;
            padding: 30px;
            margin: 25px 0;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.08);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .panel:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 32px rgba(0,0,0,0.15), 0 4px 8px rgba(0,0,0,0.1);
        }
        .panel h2 {
            margin-top: 0;
            margin-bottom: 20px;
            color: #1a202c;
            font-size: 1.6em;
            font-weight: 600;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }
        .panel h3 {
            color: #2d3748;
            font-size: 1.2em;
            font-weight: 600;
            margin-top: 0;
            margin-bottom: 15px;
        }
        .chart-container {
            margin: 25px 0;
            height: 450px;
            position: relative;
            background: #fafafa;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #e2e8f0;
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
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 12px;
            margin-top: 20px;
        }
        .library-item {
            padding: 12px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            font-size: 14px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            transition: all 0.3s ease;
            text-align: center;
        }
        .library-item:hover {
            border-color: #667eea;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        .library-item:hover a {
            color: #fff;
            font-weight: 600;
        }
        .tables-container-2 > div,
        .tables-container-3 > div {
            background: #fafafa;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }
        .tables-container-2 > div:hover,
        .tables-container-3 > div:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-color: #cbd5e0;
        }
        @media (max-width: 1200px) {
            .tables-container-3 {
                grid-template-columns: 1fr;
            }
            .tables-container-2 {
                grid-template-columns: 1fr;
            }
            body {
                padding: 20px 15px;
            }
            .panel {
                padding: 20px;
            }
            h1 {
                font-size: 2em;
            }
        }
    """


def _get_library_css() -> str:
    """Return CSS styles for library HTML files."""
    return """
        * {
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            max-width: 1600px;
            margin: 0 auto;
            padding: 30px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        h1 {
            text-align: center;
            color: #fff;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            font-weight: 700;
        }
        .panel {
            background: #ffffff;
            padding: 30px;
            margin: 25px 0;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.08);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .panel:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 32px rgba(0,0,0,0.15), 0 4px 8px rgba(0,0,0,0.1);
        }
        .panel h2 {
            margin-top: 0;
            margin-bottom: 20px;
            color: #1a202c;
            font-size: 1.6em;
            font-weight: 600;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }
        .panel h3 {
            color: #2d3748;
            font-size: 1.2em;
            font-weight: 600;
            margin-top: 0;
            margin-bottom: 15px;
        }
        .chart-container {
            margin: 25px 0;
            height: 450px;
            position: relative;
            background: #fafafa;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #e2e8f0;
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
        .back-link a {
            color: rgba(255, 255, 255, 0.95);
            font-weight: 500;
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 6px;
            display: inline-block;
            transition: all 0.2s ease;
            backdrop-filter: blur(10px);
        }
        .back-link a:hover {
            background: rgba(255, 255, 255, 0.25);
            color: #fff;
            text-decoration: none;
            transform: translateX(-3px);
        }
        .depth-1 {
            background-color: #dbeafe;
        }
        .depth-2 {
            background-color: #d1fae5;
        }
        .depth-3, .depth-4, .depth-5 {
            background-color: #fef3c7;
        }
        @media (max-width: 1200px) {
            .panel-row {
                grid-template-columns: 1fr;
            }
            body {
                padding: 20px 15px;
            }
            .panel {
                padding: 20px;
            }
            h1 {
                font-size: 2em;
            }
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


def _collect_dependents_data(db: Any) -> Dict[int, Dict[str, Any]]:
    """
    Collect dependents data for all libraries with transitive dependencies and depth tracking.

    Returns:
        Dict mapping library_id to {
            "table_data": List[Dict with name, depth] for latest version with dependents,
            "chart_data": Dict mapping version to {
                "first_level": count,
                "all_deeper": count
            }
        }
    """
    # Fetch all dependencies
    dependencies = db.fetchall("""
        SELECT
            main_library_id, dependency_library_id, version_id
        FROM library_dependency
        ORDER BY version_id
    """)

    libraries = db.fetchall("SELECT id, name FROM boost_library ORDER BY name")
    library_id_to_name = {row["id"]: row["name"] for row in libraries}

    versions = db.fetchall("SELECT id, version, major, minor, patch FROM boost_version ORDER BY major DESC, minor DESC, patch DESC")
    version_id_to_version = {row["id"]: row["version"] for row in versions}
    version_id_to_info = {row["id"]: row for row in versions}

    # Build dependency graph: library_id -> version_id -> list of direct dependency library_ids
    dependency_graph = {}
    for row in dependencies:
        main_lib_id = row["main_library_id"]
        dep_lib_id = row["dependency_library_id"]
        version_id = row["version_id"]

        if main_lib_id not in dependency_graph:
            dependency_graph[main_lib_id] = {}
        if version_id not in dependency_graph[main_lib_id]:
            dependency_graph[main_lib_id][version_id] = []
        dependency_graph[main_lib_id][version_id].append(dep_lib_id)

    def find_all_transitive_deps(main_lib_id: int, version_id: int, graph: Dict) -> Dict[int, int]:
        """
        Find all transitive dependencies with depth tracking using BFS.
        Returns: Dict mapping dependency_library_id to depth (1 = direct, 2+ = transitive)
        Excludes the main library itself from dependencies.
        """
        if main_lib_id not in graph or version_id not in graph[main_lib_id]:
            return {}

        all_deps = {}  # dep_lib_id -> depth
        # Filter out self-dependencies from initial queue
        initial_deps = [dep_id for dep_id in graph[main_lib_id][version_id] if dep_id != main_lib_id]
        queue = [(dep_id, 1) for dep_id in initial_deps]  # (lib_id, depth)
        visited = set()
        visited.add(main_lib_id)  # Exclude main library from visited set

        while queue:
            current_lib_id, depth = queue.pop(0)

            if current_lib_id in visited or current_lib_id == main_lib_id:
                continue
            visited.add(current_lib_id)

            # Record this dependency with its depth
            if current_lib_id not in all_deps or all_deps[current_lib_id] > depth:
                all_deps[current_lib_id] = depth

            # Add transitive dependencies (if this library also has dependencies in this version)
            if current_lib_id in graph and version_id in graph[current_lib_id]:
                for next_dep_id in graph[current_lib_id][version_id]:
                    # Exclude self-dependencies and the main library
                    if next_dep_id not in visited and next_dep_id != main_lib_id and next_dep_id != current_lib_id:
                        queue.append((next_dep_id, depth + 1))

        return all_deps

    # Find the latest version from boost_version table
    latest_version_id = sorted(version_id_to_version.keys(),
                               key=lambda vid: (version_id_to_info[vid]["major"],
                                               version_id_to_info[vid]["minor"],
                                               version_id_to_info[vid]["patch"]),
                               reverse=True)[0]
    latest_version_str = version_id_to_version[latest_version_id]
    latest_version_info = version_id_to_info[latest_version_id]

    # Get all versions from 1.66.0 to latest version for chart x-axis
    all_versions_for_chart = []
    for vid in sorted(version_id_to_version.keys(),
                     key=lambda vid: (version_id_to_info[vid]["major"],
                                     version_id_to_info[vid]["minor"],
                                     version_id_to_info[vid]["patch"])):
        version_str = version_id_to_version[vid]
        major = version_id_to_info[vid]["major"]
        minor = version_id_to_info[vid]["minor"]
        patch = version_id_to_info[vid]["patch"]
        # Include versions from 1.66.0 to latest version (inclusive)
        if major == 1 and minor >= 66:
            # Compare with latest version
            if (major < latest_version_info["major"] or
                (major == latest_version_info["major"] and minor < latest_version_info["minor"]) or
                (major == latest_version_info["major"] and minor == latest_version_info["minor"] and patch <= latest_version_info["patch"])):
                all_versions_for_chart.append(version_str)

    total_dependents_by_library: Dict[int, Dict[str, Any]] = {}

    for library_id in library_id_to_name.keys():
        table_data = []
        chart_data = {}

        # Initialize chart_data with all versions from 1.66.0 to latest version, set to 0
        for version_str in all_versions_for_chart:
            chart_data[version_str] = {
                "first_level": 0,
                "all_deeper": 0
            }

        # Process each version for chart data
        for version_id in sorted(version_id_to_version.keys(),
                                 key=lambda vid: (version_id_to_info[vid]["major"],
                                                 version_id_to_info[vid]["minor"],
                                                 version_id_to_info[vid]["patch"])):
            version_str = version_id_to_version[version_id]
            # Only process versions in the range 1.66.0 to latest version
            if version_str not in all_versions_for_chart:
                continue

            all_deps = find_all_transitive_deps(library_id, version_id, dependency_graph)

            # Separate first-level and deeper dependencies (exclude self)
            first_level = [lib_id for lib_id, depth in all_deps.items() if depth == 1 and lib_id != library_id]
            # all_deeper should include first-level dependencies (cumulative)
            all_deps_count = len([lib_id for lib_id in all_deps.keys() if lib_id != library_id])

            chart_data[version_str] = {
                "first_level": len(first_level),
                "all_deeper": all_deps_count  # Includes first-level + deeper (cumulative)
            }

        # Build table data for latest version (always use latest version for all libraries)
        all_deps = find_all_transitive_deps(library_id, latest_version_id, dependency_graph)
        # Filter out self-dependencies and sort by depth, then name
        for dep_lib_id, depth in sorted(all_deps.items(), key=lambda x: (x[1], library_id_to_name.get(x[0], ""))):
            # Double-check: exclude self-dependencies
            if dep_lib_id != library_id:
                dep_name = library_id_to_name.get(dep_lib_id, f"Unknown({dep_lib_id})")
                table_data.append({
                    "name": dep_name,
                    "depth": depth
                })

        total_dependents_by_library[library_id] = {
            "table_data": table_data,
            "chart_data": chart_data,
            "latest_version_id": latest_version_id  # Always use latest version from boost_version table
        }

    return total_dependents_by_library


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

        # Create table data with depth 1 (direct dependencies only in fallback)
        dependents_table_data = [{"name": row["dep_library_name"], "depth": 1} for row in dependencies]

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
                # Use new format: first_level and all_deeper (fallback: all are first-level)
                dependents_by_version[version] = {
                    "first_level": int(dep_count or 0),
                    "all_deeper": 0
                }

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

        # Collect internal dependents data (transitive dependencies with depth)
        table_exists = db.table_exists("library_dependency")
        internal_dependents_data = {}
        if table_exists:
            internal_dependents_data = _collect_dependents_data(db)

        # Collect library data
        libraries = db.fetchall("SELECT id, name FROM boost_library ORDER BY name")

        latest_version_rows = db.fetchall("""
            SELECT id, version FROM boost_version
            ORDER BY major DESC, minor DESC, patch DESC
            LIMIT 2
        """)
        latest_version_id = latest_version_rows[0]["id"] if latest_version_rows else None
        latest_version_str = latest_version_rows[0]["version"] if latest_version_rows else None

        # Get all versions from 1.66.0 to latest version for chart x-axis
        all_versions_db = db.fetchall("SELECT version, major, minor, patch FROM boost_version ORDER BY major DESC, minor DESC, patch DESC")
        latest_version_row = all_versions_db[0] if all_versions_db else None

        all_versions_for_chart = []
        if latest_version_row:
            latest_major = latest_version_row["major"]
            latest_minor = latest_version_row["minor"]
            latest_patch = latest_version_row["patch"]

            for row in db.fetchall("SELECT version, major, minor, patch FROM boost_version"):
                version_str = row["version"]
                major = row["major"]
                minor = row["minor"]
                patch = row["patch"]
                # Include versions from 1.66.0 to latest version (inclusive)
                if major == 1 and minor >= 66:
                    # Compare with latest version
                    if (major < latest_major or
                        (major == latest_major and minor < latest_minor) or
                        (major == latest_major and minor == latest_minor and patch <= latest_patch)):
                        all_versions_for_chart.append(version_str)

        dashboard_data["all_versions_for_chart"] = sorted(all_versions_for_chart, key=version_sort_key)

        # Build version info mapping for library pages
        all_versions = db.fetchall("SELECT id, version FROM boost_version")
        versions_info = {row["id"]: row["version"] for row in all_versions}
        dashboard_data["versions_info"] = versions_info

        libraries_data: Dict[str, Dict[str, Any]] = {}
        for lib_row in libraries:
            lib_id = lib_row["id"]
            library_name = lib_row["name"]
            lib_data = _collect_library_data(
                db, db1, lib_id, library_name, latest_version_id, latest_version_str, table_exists
            )

            # Override with transitive dependency data if available
            if table_exists and lib_id in internal_dependents_data:
                dep_data = internal_dependents_data[lib_id]
                lib_data["dependents_table_data"] = dep_data.get("table_data", [])
                lib_data["dependents_by_version"] = dep_data.get("chart_data", {})
                lib_data["latest_version_id"] = dep_data.get("latest_version_id")

            libraries_data[library_name] = lib_data

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

