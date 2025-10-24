#!/usr/bin/env python3
"""
CSV Deduplication Script

This script reads a CSV file containing Email, Name, Source, and URL fields,
deduplicates entries based on (Email, Name) pairs, and merges URLs by source.
"""

import csv
import sys
import re
from collections import defaultdict
from pathlib import Path


# Email regex pattern (RFC 5322 simplified)
# Matches email addresses, ensuring the domain ends with a valid TLD (2-6 chars)
# and is followed by a word boundary (space, punctuation, or end of string)
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}\b(?![A-Za-z])')


def extract_email(email_str):
    """
    Extract valid email address from a string using regex.
    
    Args:
        email_str: String potentially containing an email address
        
    Returns:
        Cleaned email string or empty string if no valid email found
    """
    if not email_str:
        return ''
    
    # Try to find email pattern
    match = EMAIL_PATTERN.search(email_str)
    if match:
        return match.group(0).strip().lower()
    
    # If no match, return cleaned original (remove quotes, whitespace)
    cleaned = email_str.strip().strip('"').strip("'").strip()
    return cleaned.lower() if cleaned else ''


def clean_name(name_str):
    """
    Clean name by removing non-alphabetical characters from front and back.
    Preserves balanced parentheses unless they wrap the entire text.
    
    Examples:
        '(John Maddock)' -> 'John Maddock' (wraps entire text, removed)
        'John Smith (Company)' -> 'John Smith (Company)' (partial, kept)
        '***John Smith***' -> 'John Smith'
    
    Args:
        name_str: Name string to clean
        
    Returns:
        Cleaned name string
    """
    if not name_str:
        return ''
    
    # Remove quotes first
    name = name_str.strip().strip('"').strip("'").strip()
    
    if not name:
        return ''
    
    # Check if the entire text is wrapped in parentheses
    # Pattern: (everything inside) - handle nested parens by recursion
    full_wrap_match = re.match(r'^\s*\((.*)\)\s*$', name)
    
    if full_wrap_match:
        # Remove the wrapping parentheses and recursively clean
        inner_content = full_wrap_match.group(1).strip()
        # Recursively clean in case there are more layers or edge chars
        return clean_name(inner_content)
    
    # Check for balanced parentheses at the end (but not wrapping entire text)
    # Pattern: content (stuff) or content(stuff)
    trailing_paren_match = re.search(r'^(.+?)(\s*\([^)]*\)\s*)$', name)
    
    if trailing_paren_match:
        main_part = trailing_paren_match.group(1).strip()
        paren_part = trailing_paren_match.group(2).strip()
        
        # Clean main part by removing unwanted chars from edges (preserve Unicode letters)
        # Remove leading non-letter characters (but preserve Unicode letters)
        main_cleaned = ''.join(char for i, char in enumerate(main_part) 
                               if i > 0 or char.isalpha() or char == ' ')
        main_cleaned = main_cleaned.lstrip()
        # Remove trailing non-letter characters (except closing parens)
        while main_cleaned and not main_cleaned[-1].isalpha() and main_cleaned[-1] not in ')':
            main_cleaned = main_cleaned[:-1]
        
        return f"{main_cleaned} {paren_part}" if main_cleaned else paren_part
    
    # Check for balanced parentheses at the beginning (but not wrapping entire text)
    leading_paren_match = re.search(r'^(\s*\([^)]*\)\s*)(.+)$', name)
    
    if leading_paren_match:
        paren_part = leading_paren_match.group(1).strip()
        main_part = leading_paren_match.group(2).strip()
        
        # Clean main part (preserve Unicode letters)
        main_cleaned = ''.join(char for i, char in enumerate(main_part) 
                               if i > 0 or char.isalpha() or char == ' ')
        main_cleaned = main_cleaned.lstrip()
        while main_cleaned and not main_cleaned[-1].isalpha() and main_cleaned[-1] not in ')':
            main_cleaned = main_cleaned[:-1]
        
        return f"{paren_part} {main_cleaned}" if main_cleaned else paren_part
    
    # No parentheses, just clean edges (preserve Unicode letters)
    # Remove leading non-letter characters
    cleaned = name.lstrip()
    while cleaned and not cleaned[0].isalpha() and cleaned[0] not in '(':
        cleaned = cleaned[1:]
    
    # Remove trailing non-letter characters (except closing parens)
    while cleaned and not cleaned[-1].isalpha() and cleaned[-1] not in ')':
        cleaned = cleaned[:-1]
    
    return cleaned.strip()


def read_csv_to_list(file_path):
    """
    Read CSV file into a list of dictionaries.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Tuple of (data, encoding_used) where data is a list of dictionaries
    """
    data = []
    # Try different encodings in order of preference
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    encoding_used = None
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                data = [row for row in reader]
            # If successful, save the encoding and break
            encoding_used = encoding
            break
        except (UnicodeDecodeError, UnicodeError):
            # Try the next encoding
            continue
    
    if not data:
        # Fallback: read with utf-8 and ignore errors
        encoding_used = 'utf-8 (with errors replaced)'
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            data = [row for row in reader]
    
    return data, encoding_used


def merge_duplicates(data):
    """
    Merge duplicate (Email, Name) pairs and group URLs by source.
    Comparison is case-insensitive but preserves original casing for display.
    
    Args:
        data: List of dictionaries with Email, Name, Source, URL fields
        
    Returns:
        List of merged dictionaries with structure:
        {
            'email': str,
            'name': str,
            'sources': [
                {'source': str, 'urls': [url1, url2, ...]},
                ...
            ]
        }
    """
    # Dictionary to group by (email, name) pairs (case-insensitive)
    grouped = defaultdict(lambda: defaultdict(set))
    # Track original casing for display (prefer non-lowercase versions)
    original_casing = {}
    
    # Group URLs by (email, name) and source
    for row in data:
        email = extract_email(row.get('Email', ''))
        name = clean_name(row.get('Name', ''))
        source = row.get('Source', '').strip()
        url = row.get('URL', '').strip()
        
        # Skip if email or name is empty after cleaning
        if not email or not name:
            continue
        
        # Use lowercase for comparison key (email already lowercase from extract_email)
        key = (email, name.lower())
        
        # Store original casing (prefer versions that aren't all lowercase/uppercase)
        if key not in original_casing:
            original_casing[key] = (email, name)
        else:
            # Prefer mixed case over all lowercase/uppercase
            existing_name = original_casing[key][1]
            if name != name.lower() and name != name.upper():
                # Current name has mixed case, prefer it
                if existing_name == existing_name.lower() or existing_name == existing_name.upper():
                    original_casing[key] = (email, name)
        
        if url:  # Only add if URL is not empty
            grouped[key][source].add(url)
    
    # Convert to list format sorted by name then email
    result = []
    for key in sorted(grouped.keys(), key=lambda x: (x[1], x[0])):
        # Use original casing for display
        email, name = original_casing[key]
        
        sources_list = []
        for source in sorted(grouped[key].keys()):
            urls = sorted(list(grouped[key][source]))
            sources_list.append({
                'source': source,
                'urls': urls
            })
        
        result.append({
            'email': email,
            'name': name,
            'sources': sources_list
        })
    
    return result


def write_dedup_csv(merged_data, output_file):
    """
    Write deduplicated data to a CSV file with UTF-8 BOM for Excel compatibility.
    
    The output CSV will have columns: Name, Email, Ref_Json
    where Ref_Json is a JSON string mapping sources to their references.
    Each (Name, Email) pair appears only once with all sources combined.
    
    Note: Python's csv.writer automatically handles proper escaping of special 
    characters (commas, quotes, newlines) according to CSV RFC 4180.
    
    Args:
        merged_data: List of merged dictionaries
        output_file: Path to the output CSV file
    
    Returns:
        Number of rows written
    """
    import json
    
    rows_written = 0
    
    # Use utf-8-sig encoding to add BOM for Excel compatibility
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        # csv.writer with default quoting handles all special char escaping
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        
        # Write header
        writer.writerow(['Name', 'Email', 'Ref_Json'])
        
        # Write data (email/name already validated in merge_duplicates)
        for entry in merged_data:
            email = entry['email']
            name = entry['name']
            
            # Skip if name looks like an email address (contains @ and matches email pattern)
            if '@' in name and EMAIL_PATTERN.search(name):
                continue
            
            # Build JSON object mapping sources to their references
            ref_json = {}
            for source_info in entry['sources']:
                source = source_info['source']
                urls = source_info['urls']
                
                # Skip if no URLs or no source
                if not urls or not source:
                    continue
                
                # Store as list in JSON
                ref_json[source] = sorted(list(urls))
            
            # Only write if there are references
            if ref_json:
                # Convert to compact JSON string
                json_str = json.dumps(ref_json, ensure_ascii=False, separators=(',', ':'))
                writer.writerow([name, email, json_str])
                rows_written += 1
    
    return rows_written


def write_summary_csv(merged_data, output_file):
    """
    Write summary CSV with contribution counts by source type.
    
    The output CSV will have columns: Name, Email, GitHub, WG21, Mailing_List
    where each count column represents the number of contributions to that source.
    
    Args:
        merged_data: List of merged dictionaries
        output_file: Path to the output summary CSV file
    
    Returns:
        Number of rows written
    """
    rows_written = 0
    
    # Use utf-8-sig encoding to add BOM for Excel compatibility
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        
        # Write header
        writer.writerow(['Name', 'Email', 'GitHub', 'WG21', 'Mailing_List'])
        
        # Write data
        for entry in merged_data:
            email = entry['email']
            name = entry['name']
            
            # Skip if name looks like an email address
            if '@' in name and EMAIL_PATTERN.search(name):
                continue
            
            # Count contributions by type
            github_count = 0
            wg21_count = 0
            mailing_count = 0
            
            for source_info in entry['sources']:
                source = source_info['source']
                urls = source_info['urls']
                
                if not urls or not source:
                    continue
                
                # Categorize sources
                if source.startswith('git@'):
                    github_count += len(urls)
                elif source == 'wg21_paper' or source == 'WG21':
                    wg21_count += len(urls)
                elif source == 'mailing_list':
                    mailing_count += len(urls)
            
            # Only write if there are any contributions
            if github_count > 0 or wg21_count > 0 or mailing_count > 0:
                writer.writerow([name, email, github_count, wg21_count, mailing_count])
                rows_written += 1
    
    return rows_written


def main():
    """Main function to process CSV deduplication."""
    # Find the data directory
    data_dir = Path(__file__).parent / 'data'
    
    if not data_dir.exists():
        print(f"Error: Data directory not found at {data_dir}")
        sys.exit(1)
    
    # Find all CSV files in data directory, excluding dedup files
    csv_files = [
        f for f in data_dir.glob('*.csv') 
        if 'dedup' not in f.name.lower()
    ]
    
    if not csv_files:
        print(f"Error: No CSV files found in {data_dir}")
        sys.exit(1)
    
    print(f"Found {len(csv_files)} CSV file(s) to process:")
    for f in csv_files:
        print(f"  - {f.name}")
    
    # Read and combine all CSV files
    all_data = []
    for csv_file in csv_files:
        print(f"\nReading: {csv_file.name}")
        file_data, encoding = read_csv_to_list(csv_file)
        print(f"  Rows: {len(file_data)}")
        print(f"  Encoding: {encoding}")
        all_data.extend(file_data)
    
    print(f"\nTotal rows read from all files: {len(all_data)}")
    data = all_data
    
    # Output files in the data directory
    output_file = data_dir / 'dedup.csv'
    summary_file = data_dir / 'dedup_summary.csv'
    
    print("Merging duplicates...")
    merged_data = merge_duplicates(data)
    print(f"Unique (Email, Name) pairs: {len(merged_data)}")
    
    # Calculate statistics
    total_sources = sum(len(entry['sources']) for entry in merged_data)
    total_urls = sum(
        len(source_info['urls']) 
        for entry in merged_data 
        for source_info in entry['sources']
    )
    
    print(f"Total unique sources: {total_sources}")
    print(f"Total unique references: {total_urls}")
    
    print(f"\nWriting deduplicated data to: {output_file}")
    rows_written = write_dedup_csv(merged_data, output_file)
    print(f"  Wrote {rows_written} rows")
    
    print(f"\nWriting summary data to: {summary_file}")
    summary_rows = write_summary_csv(merged_data, summary_file)
    print(f"  Wrote {summary_rows} rows")
    
    print("\nDone!")
    print(f"\nSummary:")
    print(f"  Input rows: {len(data)}")
    print(f"  Output rows (dedup.csv): {rows_written}")
    print(f"  Output rows (summary): {summary_rows}")
    print(f"  Reduction: {len(data) - rows_written} rows ({100 * (len(data) - rows_written) / len(data):.1f}%)")


if __name__ == "__main__":
    main()

