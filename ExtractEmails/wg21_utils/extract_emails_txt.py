"""
Extract email-name pairs from TXT files in the output directory.
Supports regular emails and obfuscated formats.
"""

import os
import re
import json
from pathlib import Path


def extract_email_name_pairs_from_file(txt_file_path):
    """
    Extract name and email pairs from a single TXT file.
    Handles both regular emails and obfuscated emails.

    Args:
        txt_file_path: Path to the TXT file (string or Path object)

    Returns:
        dict: Dictionary with structure:
            {
                'name_email_pairs': {name: email},
                'emails': [list of all emails],
                'file_path': str
            }
        Returns None if there's an error processing the file.
    """
    try:
        # Regular email pattern
        email_pattern = re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        )

        # Obfuscated email patterns:
        # Pattern 1: "user at domain dot com" (both @ and . are obfuscated)
        obfuscated_pattern1 = re.compile(
            r"\b([A-Za-z0-9._%-]+)\s+at\s+([A-Za-z0-9.-]+)\s+dot\s+([A-Za-z]{2,})\b",
            re.IGNORECASE,
        )

        # Pattern 2: "user at domain.com" (only @ is obfuscated, . is kept)
        obfuscated_pattern2 = re.compile(
            r"\b([A-Za-z0-9._%-]+)\s+at\s+([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b",
            re.IGNORECASE,
        )

        with open(txt_file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            lines = content.split("\n")

        # Track results for this file
        name_email_dict = {}

        # Find all regular emails
        emails_in_file = email_pattern.findall(content)

        # Find obfuscated emails - Pattern 1: "user at domain dot com"
        obfuscated_matches1 = obfuscated_pattern1.findall(content)
        for user, domain, tld in obfuscated_matches1:
            real_email = f"{user}@{domain}.{tld}"
            emails_in_file.append(real_email)

        # Find obfuscated emails - Pattern 2: "user at domain.com"
        obfuscated_matches2 = obfuscated_pattern2.findall(content)
        for user, domain_with_tld in obfuscated_matches2:
            real_email = f"{user}@{domain_with_tld}"
            emails_in_file.append(real_email)

        unique_emails = sorted(list(set(emails_in_file)))

        # Process line by line to find name-email pairs
        for i, line in enumerate(lines):
            # Check for regular email
            email_match = email_pattern.search(line)
            if email_match:
                email = email_match.group()
                name = extract_name_from_context(lines, i, email)

                if name:
                    if name not in name_email_dict:
                        name_email_dict[name] = email

            # Check for obfuscated email - Pattern 1
            obf_match1 = obfuscated_pattern1.search(line)
            if obf_match1:
                user, domain, tld = obf_match1.groups()
                real_email = f"{user}@{domain}.{tld}"

                name_pattern = re.compile(
                    r"(?:Reply-to:|Reply to:|From:|Author:)?\s*([A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+)+)\s*[<\.,\s\(]",
                    re.IGNORECASE,
                )
                name_match = name_pattern.search(line)
                if name_match:
                    name = clean_name(name_match.group(1))
                    if name and name not in name_email_dict:
                        name_email_dict[name] = real_email

            # Check for obfuscated email - Pattern 2
            obf_match2 = obfuscated_pattern2.search(line)
            if obf_match2:
                user, domain_with_tld = obf_match2.groups()
                real_email = f"{user}@{domain_with_tld}"

                name_pattern = re.compile(
                    r"(?:Reply-to:|Reply to:|From:|Author:)?\s*([A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+)+)\s*[<\.,\s\(]",
                    re.IGNORECASE,
                )
                name_match = name_pattern.search(line)
                if name_match:
                    name = clean_name(name_match.group(1))
                    if name and name not in name_email_dict:
                        name_email_dict[name] = real_email

        return {
            "name_email_pairs": name_email_dict,
            "emails": unique_emails,
            "file_path": str(txt_file_path),
        }

    except Exception as e:
        print(f"[ERROR] Error processing {txt_file_path}: {e}")
        return None


def extract_name_from_context(lines, email_line_idx, email):
    """
    Extract name from the context around an email address in TXT files.

    Args:
        lines: List of all lines in the file
        email_line_idx: Index of the line containing the email
        email: The email address found

    Returns:
        str: Extracted name or None
    """
    line = lines[email_line_idx]

    # Pattern 1: "Email: name@domain.com" format - look for name in previous lines
    if re.search(r"Email\s*:\s*", line, re.IGNORECASE):
        # Look backward for name (typically 1-10 lines before in TXT files)
        for i in range(max(0, email_line_idx - 10), email_line_idx):
            prev_line = lines[i].strip()

            # Check if this line has "Reply to:" with nothing or only whitespace after
            # Example:
            #   Reply to: Thomas Plum
            #             Plum Hall Inc
            #             ...
            #             standards@plumhall.com
            reply_to_match = re.match(
                r"^(?:Reply\s*-?\s*to|Author|From)\s*:\s*$", prev_line, re.IGNORECASE
            )
            if reply_to_match:
                # Name should be on the next line
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    # Check if it looks like a name
                    name_match = re.search(
                        r"^([A-Z][a-zA-Z]*\.?\s+)?([A-Z]\.?\s+)?([A-Z][a-zA-Z\-]+)$",
                        next_line,
                    )
                    if name_match and len(next_line.split()) >= 2:
                        # Skip if it looks like an organization
                        if not re.search(
                            r"\b(Ltd|LLC|Inc|Corp|Corporation|Company|Group|Association|Foundation|Institute)\b",
                            next_line,
                            re.IGNORECASE,
                        ):
                            cleaned = clean_name(next_line)
                            if cleaned:
                                return cleaned

            # Look for patterns like "Reply to:", "Reply-to:", "Author:", "From:"
            # Pattern: "Reply to: Name" or "Reply-to: Name" (name on same line)
            name_match = re.search(
                r"(?:Reply\s*-?\s*to|Author|From)\s*:\s*([A-Z][a-zA-Z\-\.]+(?:\s+[A-Z][a-zA-Z\-\.]+)+)",
                prev_line,
                re.IGNORECASE,
            )
            if name_match:
                potential_name = name_match.group(1)
                if not re.match(
                    r"(Submitted|Convener|Author|Editor|Date|Document|Project|Period)",
                    potential_name,
                ):
                    cleaned = clean_name(potential_name)
                    if cleaned:
                        return cleaned

            # Check for standalone name (with initials like P.J.)
            # Pattern: Name that may include periods (for initials)
            name_match = re.search(
                r"^([A-Z][a-zA-Z]*\.?\s+)?([A-Z]\.?\s+)?([A-Z][a-zA-Z\-]+)$",
                prev_line,
            )
            if name_match and len(prev_line.split()) >= 2:
                potential_name = prev_line
                # Skip if it looks like an organization
                if not re.search(
                    r"\b(Ltd|LLC|Inc|Corp|Corporation|Company|Group|Association|Foundation|Institute)\b",
                    potential_name,
                    re.IGNORECASE,
                ):
                    cleaned = clean_name(potential_name)
                    if cleaned:
                        return cleaned

    # Pattern 2: Email on its own line - look 1-3 lines above
    # Common pattern: Name / Organization / email
    if not re.search(r"[A-Za-z].*" + re.escape(email), line):
        # Email is standalone, check previous lines
        for offset in [1, 2, 3]:
            if email_line_idx - offset >= 0:
                check_line = lines[email_line_idx - offset].strip()

                # Skip empty lines
                if not check_line:
                    continue

                # Skip organization lines
                if re.search(
                    r"\b(Ltd|LLC|Inc|Corp|Corporation|Company|Group|Association|Foundation|Institute)\b",
                    check_line,
                    re.IGNORECASE,
                ):
                    continue

                # Check if it looks like a name (including initials like P.J.)
                name_match = re.search(
                    r"^([A-Z][a-zA-Z]*\.?\s+)?([A-Z]\.?\s+)?([A-Z][a-zA-Z\-]+)$",
                    check_line,
                )
                if name_match and len(check_line.split()) >= 2:
                    cleaned = clean_name(check_line)
                    if cleaned:
                        return cleaned

    # Pattern 2b: Email on its own line - look further back (up to 10 lines) for "Reply to:" patterns
    # Example:
    #   Reply to: Thomas Plum
    #             Plum Hall Inc
    #             PO Box 44610
    #             standards@plumhall.com
    if not re.search(r"[A-Za-z].*" + re.escape(email), line):
        # Email is standalone, look for "Reply to:" patterns further back
        for i in range(max(0, email_line_idx - 10), email_line_idx):
            check_line = lines[i].strip()

            if not check_line:
                continue

            # Look for "Reply to: Name" pattern
            name_match = re.search(
                r"(?:Reply\s*-?\s*to|Author|From)\s*:\s*([A-Z][a-zA-Z\-\.]+(?:\s+[A-Z][a-zA-Z\-\.]+)+)",
                check_line,
                re.IGNORECASE,
            )
            if name_match:
                potential_name = name_match.group(1)
                if not re.match(
                    r"(Submitted|Convener|Author|Editor|Date|Document|Project|Period)",
                    potential_name,
                ):
                    cleaned = clean_name(potential_name)
                    if cleaned:
                        return cleaned

    # Pattern 3: "Name - email@domain.com" format (name and email on same line with hyphen)
    # Example: "Joshua Berne - jberne4@Bloomberg.net"
    hyphen_match = re.search(
        r"([A-Z][a-zA-Z\-\.]+(?:\s+[A-Z][a-zA-Z\-\.]+)+)\s*-\s*" + re.escape(email),
        line,
    )
    if hyphen_match:
        name = hyphen_match.group(1).strip()
        return clean_name(name)

    # Pattern 4: "Author: Name" format in same line
    author_match = re.search(
        r"(?:Author|Reply-?to|From)\s*:\s*([A-Za-z\s\.\-]+)", line, re.IGNORECASE
    )
    if author_match:
        return clean_name(author_match.group(1))

    # Pattern 5: Name in parentheses with email: (name@domain.com)
    paren_match = re.search(
        r"([A-Z][a-zA-Z\-\.]+(?:\s+[A-Z][a-zA-Z\-\.]+)*)\s*\([^)]*" + re.escape(email),
        line,
    )
    if paren_match:
        name = paren_match.group(1).strip()
        return clean_name(name)

    return None


def clean_name(name):
    """
    Clean up extracted name by removing organizational suffixes and extra text.

    Args:
        name: Raw extracted name string

    Returns:
        str: Cleaned name
    """
    if not name:
        return None

    cleaned = name.strip()

    # Filter out obvious non-person names
    # Check for ALL CAPS (likely labels or headers)
    if cleaned.isupper():
        return None

    # Filter out company/organization indicators
    org_indicators = [
        "Ltd",
        "LLC",
        "Inc",
        "Corp",
        "Corporation",
        "Company",
        "Location",
        "Inn",
        "Hotel",
        "Venue",
        "Website",
        "Doc No",
        "Document",
        "PERIOD",
        "COVERED",
        "Meeting",
        "Address",
        "Tel",
        "Fax",
        "Email",
        "Dinkumware",
        "Bloomberg",
        "Microsoft",
        "Google",
        "Reservation",
        "Sales",
    ]

    for indicator in org_indicators:
        if indicator.lower() in cleaned.lower():
            return None

    # Remove common organizational suffixes
    org_suffixes = [
        "Sandia National Laboratories",
        "Oak Ridge National Laboratory",
        "Los Alamos National Laboratory",
        "Argonne National Laboratory",
        "National Laboratories",
        "National Laboratory",
        "University",
        "Corporation",
        "Microsoft Corp",
        "Bloomberg LP",
    ]

    for suffix in org_suffixes:
        if cleaned.endswith(suffix):
            cleaned = cleaned[: -len(suffix)].strip()
        elif suffix in cleaned:
            parts = cleaned.split(suffix)
            cleaned = parts[0].strip()

    # Keep only 2-3 word names (First Middle? Last)
    words = cleaned.split()
    if len(words) > 3:
        cleaned = " ".join(words[:3])

    # Final validation: must have at least 2 words and look like a person name
    words = cleaned.split()
    if len(words) >= 2:
        # Check if it looks like a person name (starts with capital letters)
        # Allow for initials with periods (like P.J., A.B.) and hyphenated names
        valid_words = 0
        for word in words:
            if not word:
                continue

            # Check if word is initials (like "P.", "J.", "P.J.", "A.B.")
            # Pattern: One or more capital letters each followed by a period
            if re.match(r"^([A-Z]\.)+$", word):
                valid_words += 1
                continue

            # Check if word starts with capital and rest is lowercase, or contains hyphen
            if word[0].isupper() and (word[1:].islower() or "-" in word):
                valid_words += 1
            else:
                # Invalid word found
                return None

        # Need at least 2 valid words (could be initials + surname, or first + last)
        if valid_words >= 2:
            return cleaned

    return None


def extract_email_name_pairs_per_file(output_dir="output"):
    """
    Extract name and email pairs from each TXT file in the output directory.

    Args:
        output_dir: Directory to search for TXT files (default: "output")

    Returns:
        tuple: (results_per_file, global_name_email_dict, global_emails)
    """
    results_per_file = {}
    global_name_email_dict = {}
    global_emails = set()

    # Find all TXT files
    txt_files = list(Path(output_dir).rglob("*.txt"))

    print(f"Found {len(txt_files)} TXT files to process\n")

    for txt_file in txt_files:
        # Extract from this file
        file_result = extract_email_name_pairs_from_file(txt_file)

        if file_result is None:
            continue

        # Get relative path for display
        relative_path = str(txt_file).replace(str(Path(output_dir)), "").lstrip("\\/")

        # Update global collections
        global_emails.update(file_result["emails"])

        for name, email in file_result["name_email_pairs"].items():
            if name not in global_name_email_dict:
                global_name_email_dict[name] = email

        # Store results for this file
        results_per_file[str(txt_file)] = {
            "name_email_pairs": file_result["name_email_pairs"],
            "emails": file_result["emails"],
            "relative_path": relative_path,
        }

        # Print progress
        if file_result["name_email_pairs"] or file_result["emails"]:
            print(f"[OK] {relative_path}")
            print(f"     - {len(file_result['name_email_pairs'])} name-email pairs")
            print(f"     - {len(file_result['emails'])} emails found")

    return results_per_file, global_name_email_dict, sorted(list(global_emails))


def save_results(
    results_per_file,
    global_name_email_dict,
    global_emails,
    output_file="email_name_pairs_per_file_txt.json",
):
    """Save the extraction results to a JSON file."""
    # Prepare per-file results with relative paths
    per_file_output = {}
    for file_path, data in results_per_file.items():
        if data["name_email_pairs"] or data["emails"]:
            per_file_output[data["relative_path"]] = {
                "name_email_pairs": data["name_email_pairs"],
                "emails": data["emails"],
            }

    results = {
        "per_file_results": per_file_output,
        "global_summary": {
            "name_email_pairs": global_name_email_dict,
            "all_emails": global_emails,
        },
        "statistics": {
            "total_files_processed": len(results_per_file),
            "files_with_data": len(per_file_output),
            "total_unique_pairs": len(global_name_email_dict),
            "total_unique_emails": len(global_emails),
            "emails_without_names": len(global_emails) - len(global_name_email_dict),
        },
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print(f"Results saved to: {output_file}")
    print(f"{'='*70}")


def main():
    """Main function to extract and display results"""
    print("Extracting email-name pairs from TXT files (per-file extraction)...\n")

    results_per_file, global_name_email_dict, global_emails = (
        extract_email_name_pairs_per_file()
    )

    print(f"\n{'='*70}")
    print(f"GLOBAL SUMMARY")
    print(f"{'='*70}\n")

    print(f"Name-Email Pairs ({len(global_name_email_dict)} unique pairs):")
    print(f"{'-'*70}")
    for name, email in sorted(global_name_email_dict.items()):
        print(f"{name:40} -> {email}")

    print(f"\n{'='*70}\n")
    print(f"All Emails Found ({len(global_emails)} unique emails):")
    print(f"{'-'*70}")
    for email in global_emails:
        print(f"  - {email}")

    print(f"\n{'='*70}\n")
    print(f"Per-File Statistics:")
    print(f"{'-'*70}")

    # Show files with most name-email pairs
    files_with_pairs = [
        (data["relative_path"], len(data["name_email_pairs"]))
        for data in results_per_file.values()
        if data["name_email_pairs"]
    ]
    files_with_pairs.sort(key=lambda x: x[1], reverse=True)

    print(f"\nFiles with most name-email pairs (top 10):")
    for file_path, count in files_with_pairs[:10]:
        print(f"  {count:2d} pairs - {file_path}")

    # Save results to JSON file
    save_results(results_per_file, global_name_email_dict, global_emails)

    return results_per_file, global_name_email_dict, global_emails


if __name__ == "__main__":
    results_per_file, global_name_email_dict, global_emails = main()
