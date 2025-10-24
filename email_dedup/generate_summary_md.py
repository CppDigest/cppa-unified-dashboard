#!/usr/bin/env python3
"""
Generate Executive Summary Markdown from dedup_summary.csv

Creates a markdown file with three top-10 tables:
1. Top contributors by Boost Commits
2. Top contributors by WG21 Papers
3. Top contributors by Boost Mailing
"""

import csv
from pathlib import Path
from datetime import datetime


def read_summary_csv(csv_file):
    """Read the summary CSV and return list of contributor dicts."""
    contributors = []
    
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert counts to integers
            contributors.append({
                'Name': row['Name'],
                'Email': row['Email'],
                'GitHub': int(row['GitHub']),
                'WG21': int(row['WG21']),
                'Mailing_List': int(row['Mailing_List'])
            })
    
    return contributors


def format_table(contributors, column_name):
    """
    Format a markdown table for top 10 contributors by specified column.
    
    Args:
        contributors: List of contributor dictionaries
        column_name: Column to sort by ('GitHub', 'WG21', or 'Mailing_List')
    
    Returns:
        Markdown formatted table string
    """
    # Sort by the specified column in descending order and take top 10
    sorted_contributors = sorted(
        contributors, 
        key=lambda x: x[column_name], 
        reverse=True
    )[:10]
    
    # Build markdown table
    lines = []
    lines.append("| Rank | Name | Email | Boost Commits | WG21 Papers | Boost Mailing |")
    lines.append("|------|------|-------|---------------|-------------|---------------|")
    
    for i, contrib in enumerate(sorted_contributors, start=1):
        lines.append(
            f"| {i} | {contrib['Name']} | {contrib['Email']} | "
            f"{contrib['GitHub']:,} | {contrib['WG21']:,} | {contrib['Mailing_List']:,} |"
        )
    
    return '\n'.join(lines)


def generate_markdown(contributors, output_file):
    """Generate the executive summary markdown file."""
    
    # Calculate overall statistics
    total_contributors = len(contributors)
    total_commits = sum(c['GitHub'] for c in contributors)
    total_papers = sum(c['WG21'] for c in contributors)
    total_mailings = sum(c['Mailing_List'] for c in contributors)
    
    # Count contributors by type
    github_contributors = sum(1 for c in contributors if c['GitHub'] > 0)
    wg21_contributors = sum(1 for c in contributors if c['WG21'] > 0)
    mailing_contributors = sum(1 for c in contributors if c['Mailing_List'] > 0)
    
    # Build markdown content
    md_lines = []
    md_lines.append("# Boost & WG21 Contributor Executive Summary\n")
    md_lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    # Overall statistics
    md_lines.append("## Overall Statistics\n")
    md_lines.append(f"- **Total Unique Contributors**: {total_contributors:,}")
    md_lines.append(f"- **Contributors with Boost Commits**: {github_contributors:,}")
    md_lines.append(f"- **Contributors with WG21 Papers**: {wg21_contributors:,}")
    md_lines.append(f"- **Contributors to Mailing List**: {mailing_contributors:,}\n")
    
    # Table 1: Top by Boost Commits (exclude automated commits)
    md_lines.append("## Top 10 Contributors by Boost Commits\n")
    excluded_names = ['Automated Commit', 'boost-commitbot']
    non_automated = [c for c in contributors if c['Name'] not in excluded_names]
    md_lines.append(format_table(non_automated, 'GitHub'))
    md_lines.append("")
    
    # Table 2: Top by WG21 Papers
    md_lines.append("## Top 10 Contributors by WG21 Papers\n")
    md_lines.append(format_table(contributors, 'WG21'))
    md_lines.append("")
    
    # Table 3: Top by Boost Mailing
    md_lines.append("## Top 10 Contributors by Boost Mailing List Posts\n")
    md_lines.append(format_table(contributors, 'Mailing_List'))
    md_lines.append("")
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    
    print(f"Generated: {output_file}")
    print(f"  Total contributors: {total_contributors:,}")
    print(f"  Total commits: {total_commits:,}")
    print(f"  Total papers: {total_papers:,}")
    print(f"  Total mailing posts: {total_mailings:,}")


def main():
    """Main function."""
    # File paths
    script_dir = Path(__file__).parent
    csv_file = script_dir / 'data' / 'dedup_summary.csv'
    output_file = script_dir / 'data' / 'contributor_summary.md'
    
    # Check if CSV exists
    if not csv_file.exists():
        print(f"Error: {csv_file} not found")
        return 1
    
    print(f"Reading: {csv_file}")
    contributors = read_summary_csv(csv_file)
    
    print(f"Processing {len(contributors):,} contributors...")
    generate_markdown(contributors, output_file)
    
    print("\nDone!")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

