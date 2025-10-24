#!/usr/bin/env python3
"""
Clean up csv_data_v1.csv by removing duplicate author names within each file.

Rules:
1. Each file is identified by (year, paper_id, file_name)
2. Remove duplicate author names within a file
3. If a name has an email, prefer that version
4. If same name has different emails, keep both
5. Detect abbreviated names (e.g., "B. Stroustrup" == "Bjarne Stroustrup")
6. Keep the full name when abbreviation is detected
"""

import csv
import re
from collections import defaultdict
from typing import List, Dict, Tuple, Set


def normalize_name_for_comparison(name: str) -> str:
    """
    Normalize a name for loose comparison.
    Removes extra spaces, converts to lowercase.
    """
    return " ".join(name.strip().split()).lower()


def extract_initials_and_lastname(name: str) -> Tuple[List[str], str, List[str]]:
    """
    Extract first names/initials, last name from a name.
    Returns: (list of first_parts, last_name, list of first_letters)

    Examples:
    - "Bjarne Stroustrup" -> (["bjarne"], "stroustrup", ["b"])
    - "B. Stroustrup" -> (["b"], "stroustrup", ["b"])
    - "John A. Smith" -> (["john", "a"], "smith", ["j", "a"])
    - "J. A. Smith" -> (["j", "a"], "smith", ["j", "a"])
    """
    parts = name.strip().split()
    if not parts:
        return ([], "", [])

    if len(parts) == 1:
        # Only one part - it's the last name
        return ([], parts[0].lower(), [])

    # Assume last part is the last name
    last_name = parts[-1].lower()
    first_parts_raw = parts[:-1]

    first_parts = []
    first_letters = []

    for part in first_parts_raw:
        part_lower = part.rstrip(".").lower()
        first_parts.append(part_lower)
        if part_lower:
            first_letters.append(part_lower[0])

    return (first_parts, last_name, first_letters)


def is_abbreviated_match(name1: str, name2: str) -> Tuple[bool, str]:
    """
    Check if two names are the same person where one might be abbreviated.
    Returns: (is_match, fuller_name)

    Examples:
    - "B. Stroustrup" and "Bjarne Stroustrup" -> (True, "Bjarne Stroustrup")
    - "A. Tomazos" and "Andrew Tomazos" -> (True, "Andrew Tomazos")
    - "John Smith" and "J. Smith" -> (True, "John Smith")
    - "Stephen D. Clamage" and "Stephen Clamage" -> (True, "Stephen D. Clamage")
    """
    name1_norm = normalize_name_for_comparison(name1)
    name2_norm = normalize_name_for_comparison(name2)

    # Exact match
    if name1_norm == name2_norm:
        # Return the longer one (likely has more complete formatting)
        return (True, name1 if len(name1) >= len(name2) else name2)

    # Extract components
    first_parts1, lastname1, first_letters1 = extract_initials_and_lastname(name1)
    first_parts2, lastname2, first_letters2 = extract_initials_and_lastname(name2)

    # Last names must match
    if lastname1 != lastname2:
        return (False, "")

    # If no first parts, can't match
    if not first_letters1 or not first_letters2:
        return (False, "")

    # Check if first letters match exactly
    if first_letters1 == first_letters2:
        # Same initials - one might be more expanded than the other
        # Check which has longer first parts (more full names vs initials)
        total_len1 = sum(len(p) for p in first_parts1)
        total_len2 = sum(len(p) for p in first_parts2)

        if total_len1 > total_len2:
            return (True, name1)  # name1 is fuller
        else:
            return (True, name2)  # name2 is fuller or equal

    # Check if one is a subset of the other
    # This handles: "Stephen D. Clamage" vs "Stephen Clamage"
    # or "J. Smith" vs "John A. Smith"

    # Case 1: name2 has fewer parts, check if it matches beginning of name1
    if len(first_letters2) < len(first_letters1):
        # Check if first_letters2 matches the beginning of first_letters1
        if first_letters1[: len(first_letters2)] == first_letters2:
            # Also verify the matching parts are similar (not just initials)
            # If name2 has a full first name, check if name1's first name matches
            match_quality = 0
            for i in range(len(first_letters2)):
                part1 = first_parts1[i]
                part2 = first_parts2[i]
                # If both are full names (length > 1), they should match
                if len(part1) > 1 and len(part2) > 1:
                    if part1 == part2:
                        match_quality += 2
                    else:
                        return (False, "")  # Full names don't match
                # If they start with the same letter, that's good
                elif part1[0] == part2[0]:
                    match_quality += 1

            if match_quality > 0:
                return (True, name1)  # name1 is fuller (has more parts)

    # Case 2: name1 has fewer parts, check if it matches beginning of name2
    if len(first_letters1) < len(first_letters2):
        # Check if first_letters1 matches the beginning of first_letters2
        if first_letters2[: len(first_letters1)] == first_letters1:
            # Also verify the matching parts are similar
            match_quality = 0
            for i in range(len(first_letters1)):
                part1 = first_parts1[i]
                part2 = first_parts2[i]
                # If both are full names (length > 1), they should match
                if len(part1) > 1 and len(part2) > 1:
                    if part1 == part2:
                        match_quality += 2
                    else:
                        return (False, "")  # Full names don't match
                # If they start with the same letter, that's good
                elif part1[0] == part2[0]:
                    match_quality += 1

            if match_quality > 0:
                return (True, name2)  # name2 is fuller (has more parts)

    return (False, "")


def find_duplicate_groups(authors: List[Dict]) -> List[List[int]]:
    """
    Find groups of duplicate authors by index.
    Returns list of lists, where each inner list contains indices of duplicates.
    """
    n = len(authors)
    groups = []
    processed = set()

    for i in range(n):
        if i in processed:
            continue

        group = [i]
        name_i = authors[i]["author"]

        for j in range(i + 1, n):
            if j in processed:
                continue

            name_j = authors[j]["author"]
            is_match, _ = is_abbreviated_match(name_i, name_j)

            if is_match:
                group.append(j)
                processed.add(j)

        if len(group) > 1:
            groups.append(group)
        processed.add(i)

    return groups


def select_best_author(duplicates: List[Dict]) -> List[Dict]:
    """
    From a group of duplicate authors, select the best one(s) to keep.

    Rules:
    - If only one has an email, keep that one
    - If multiple have different emails, keep all with emails
    - If none have emails or all have same email, keep the fullest name
    """
    # Separate by email status
    with_email = [
        a
        for a in duplicates
        if a["email"]
        and a["email"] != "No Email"
        and not a["email"].startswith("Estimated Email List:")
    ]
    without_email = [
        a
        for a in duplicates
        if not a["email"]
        or a["email"] == "No Email"
        or a["email"].startswith("Estimated Email List:")
    ]

    # If no one has a proper email, keep the fullest name
    if not with_email:
        # Find the fullest name
        fullest = max(duplicates, key=lambda x: len(x["author"]))
        return [fullest]

    # If only one has email, keep that
    if len(with_email) == 1:
        return with_email

    # Multiple have emails - check if emails are different
    emails_set = set(a["email"] for a in with_email)

    if len(emails_set) == 1:
        # Same email - keep the fullest name
        fullest = max(with_email, key=lambda x: len(x["author"]))
        return [fullest]
    else:
        # Different emails - keep all with emails
        # But deduplicate by email to avoid same email appearing twice
        seen_emails = set()
        result = []
        for a in with_email:
            if a["email"] not in seen_emails:
                seen_emails.add(a["email"])
                result.append(a)
        return result


def cleanup_csv(input_file: str, output_file: str):
    """
    Main function to clean up the CSV file.
    """
    print("=" * 80)
    print("CSV CLEANUP SCRIPT")
    print("=" * 80)

    # Read all data
    print(f"\n[1/5] Reading CSV file: {input_file}")
    rows = []
    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    print(f"Total rows read: {len(rows)}")

    # Group by file (year, paper_id, file_name)
    print("\n[2/5] Grouping by file...")
    files = defaultdict(list)
    for idx, row in enumerate(rows):
        file_key = (row["year"], row["paper_id"], row["file_name"])
        files[file_key].append((idx, row))

    print(f"Total unique files: {len(files)}")

    # Process each file to find and resolve duplicates
    print("\n[3/5] Finding and resolving duplicates...")
    rows_to_keep = set(range(len(rows)))  # Start with all rows
    total_duplicates_removed = 0
    files_with_duplicates = 0

    for file_key, file_rows in files.items():
        indices = [idx for idx, _ in file_rows]
        authors = [row for _, row in file_rows]

        if len(authors) <= 1:
            continue

        # Find duplicate groups
        duplicate_groups = find_duplicate_groups(authors)

        if not duplicate_groups:
            continue

        files_with_duplicates += 1

        # For each duplicate group, select best author(s)
        for group in duplicate_groups:
            # Get actual indices in the original rows list
            actual_indices = [indices[g] for g in group]
            group_authors = [authors[g] for g in group]

            # Select best authors to keep
            to_keep = select_best_author(group_authors)
            to_keep_indices = set()

            for keep_author in to_keep:
                # Find which index in group matches (by object identity)
                for g_idx, auth in enumerate(group_authors):
                    if auth is keep_author:
                        to_keep_indices.add(actual_indices[g_idx])
                        break

            # Remove all except those to keep
            for actual_idx in actual_indices:
                if actual_idx not in to_keep_indices:
                    rows_to_keep.discard(actual_idx)
                    total_duplicates_removed += 1

    print(f"Files with duplicates: {files_with_duplicates}")
    print(f"Total duplicate rows removed: {total_duplicates_removed}")
    print(f"Rows remaining: {len(rows_to_keep)}")

    # Create cleaned dataset
    print("\n[4/5] Creating cleaned dataset...")
    cleaned_rows = [rows[idx] for idx in sorted(rows_to_keep)]

    final_rows = []
    for row in cleaned_rows:
        if "Estimated Email List:" in row["email"]:
            continue
        final_rows.append(row)

    # Write to output file
    print(f"\n[5/5] Writing to output file: {output_file}")
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_rows)

    print(f"\nSuccessfully wrote {len(cleaned_rows)} rows to {output_file}")

    # Statistics
    print("\n" + "=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"Original rows: {len(rows)}")
    print(f"Cleaned rows: {len(cleaned_rows)}")
    print(f"Rows removed: {total_duplicates_removed}")
    print(f"Reduction: {(total_duplicates_removed / len(rows) * 100):.2f}%")
    print("\n" + "=" * 80)
    print("DONE!")
    print("=" * 80)


if __name__ == "__main__":
    cleanup_csv("csv_data_v1.csv", "csv_data_v1_cleaned.csv")
