import os
import re
import json
from pathlib import Path


def extract_email_name_pairs_from_file(md_file_path):
    """
    Extract name and email pairs from a single MD file.
    Handles both regular emails and obfuscated emails (e.g., "user at domain dot com").

    Args:
        md_file_path: Path to the MD file (string or Path object)

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

        with open(md_file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            lines = content.split("\n")

        # Track results for this file
        name_email_dict = {}

        # Find all regular emails
        emails_in_file = email_pattern.findall(content)

        # Find obfuscated emails - Pattern 1: "user at domain dot com"
        obfuscated_matches1 = obfuscated_pattern1.findall(content)
        for user, domain, tld in obfuscated_matches1:
            # Convert "user at domain dot com" to "user@domain.com"
            real_email = f"{user}@{domain}.{tld}"
            emails_in_file.append(real_email)

        # Find obfuscated emails - Pattern 2: "user at domain.com"
        obfuscated_matches2 = obfuscated_pattern2.findall(content)
        for user, domain_with_tld in obfuscated_matches2:
            # Convert "user at domain.com" to "user@domain.com"
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
                    # Keep first occurrence of each name
                    if name not in name_email_dict:
                        name_email_dict[name] = email

            # Check for obfuscated email - Pattern 1: "user at domain dot com"
            obf_match1 = obfuscated_pattern1.search(line)
            if obf_match1:
                user, domain, tld = obf_match1.groups()
                real_email = f"{user}@{domain}.{tld}"

                # Extract name from obfuscated email context
                # Patterns: "Reply-to: Name <email...>", "Name. email...", "Reply-to: Name. email..."
                name_pattern = re.compile(
                    r"(?:Reply-to:|From:|Author:)?\s*([A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+)+)\s*[<\.,\s]",
                    re.IGNORECASE,
                )
                name_match = name_pattern.search(line)
                if name_match:
                    name = clean_name(name_match.group(1))
                    if name and name not in name_email_dict:
                        name_email_dict[name] = real_email

            # Check for obfuscated email - Pattern 2: "user at domain.com"
            obf_match2 = obfuscated_pattern2.search(line)
            if obf_match2:
                user, domain_with_tld = obf_match2.groups()
                real_email = f"{user}@{domain_with_tld}"

                # Extract name from obfuscated email context
                # Patterns: "Reply-to: Name <email...>", "Name. email...", "Reply-to: Name. email..."
                name_pattern = re.compile(
                    r"(?:Reply-to:|From:|Author:)?\s*([A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+)+)\s*[<\.,\s]",
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
            "file_path": str(md_file_path),
        }

    except Exception as e:
        print(f"[ERROR] Error processing {md_file_path}: {e}")
        return None


def extract_email_name_pairs_per_file(output_dir="output"):
    """
    Extract name and email pairs from each MD file in the output directory.

    Args:
        output_dir: Directory to search for MD files (default: "output")

    Returns:
        tuple: (results_per_file, global_name_email_dict, global_emails)
            - results_per_file: Dictionary with per-file results
            - global_name_email_dict: Combined name-email pairs across all files
            - global_emails: List of all unique emails
    """
    results_per_file = {}
    global_name_email_dict = {}
    global_emails = set()

    # Find all MD files
    md_files = list(Path(output_dir).rglob("*.md"))

    print(f"Found {len(md_files)} MD files to process\n")

    for md_file in md_files:
        # Extract from this file
        file_result = extract_email_name_pairs_from_file(md_file)

        if file_result is None:
            continue

        # Get relative path for display
        relative_path = str(md_file).replace(str(Path(output_dir)), "").lstrip("\\/")

        # Update global collections
        global_emails.update(file_result["emails"])

        for name, email in file_result["name_email_pairs"].items():
            if name not in global_name_email_dict:
                global_name_email_dict[name] = email

        # Store results for this file
        results_per_file[str(md_file)] = {
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


def extract_name_from_context(lines, email_line_idx, email):
    """
    Extract name from the context around an email address.

    Args:
        lines: List of all lines in the file
        email_line_idx: Index of the line containing the email
        email: The email address found

    Returns:
        str: Extracted name or None
    """
    line = lines[email_line_idx]

    # Pattern 0: "* Name (email) (Organization)" format - common in MD files
    # This pattern: "Name (email@domain.com) (Organization)"
    bullet_match = re.search(
        r"[*\-•]\s*([A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+)*)\s*\(", line
    )
    if bullet_match:
        name = bullet_match.group(1).strip()
        return clean_name(name)

    # Pattern 1: "Email: name@domain.com" format - look for name in previous lines
    if re.search(r"Email\s*:\s*", line, re.IGNORECASE):
        # Look backward for name (typically 1-5 lines before)
        for i in range(max(0, email_line_idx - 5), email_line_idx):
            prev_line = lines[i].strip()
            # Look for name patterns (capitalized words, including hyphens)
            name_match = re.search(
                r"\b([A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+)+)\b", prev_line
            )
            if name_match:
                potential_name = name_match.group(1)
                # Filter out common words that aren't names
                if not re.match(
                    r"(Submitted|Convener|Author|Editor|Date|Document|Project|Period)",
                    potential_name,
                ):
                    return clean_name(potential_name)

    # Pattern 2: "Author: Name" format
    author_match = re.search(r"Author\s*:\s*([A-Za-z\s\.\-]+)", line, re.IGNORECASE)
    if author_match:
        return clean_name(author_match.group(1))

    # Pattern 3: Name before (email) in same line
    # Match pattern: "Name (email@domain.com)"
    paren_match = re.search(
        r"([A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+)*)\s*\([^)]*" + re.escape(email), line
    )
    if paren_match:
        name = paren_match.group(1).strip()
        # Remove leading bullets or markers
        name = re.sub(r"^[*\-•\s]+", "", name)
        return clean_name(name)

    # Pattern 4: Name in same line as email (fallback)
    # Remove email and common keywords, then extract name
    line_without_email = line.replace(email, "").strip()
    line_cleaned = re.sub(
        r"(Email|Tel|Phone|Contact|:|,|\(|\))",
        " ",
        line_without_email,
        flags=re.IGNORECASE,
    )

    # Extract capitalized name pattern (including hyphens)
    name_match = re.search(
        r"\b([A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+){1,2})\b", line_cleaned
    )
    if name_match:
        return clean_name(name_match.group(1))

    # Pattern 5: Check line before email line for names
    if email_line_idx > 0:
        prev_line = lines[email_line_idx - 1].strip()
        name_match = re.search(
            r"\b([A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+){1,2})\b", prev_line
        )
        if name_match:
            potential_name = name_match.group(1)
            # Filter out common words
            if not re.match(
                r"(Submitted|Convener|Author|Editor|Date|Document|Project|Microsoft|Corporation)",
                potential_name,
            ):
                return clean_name(potential_name)

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

    # Remove common organizational suffixes (but don't remove if it's part of the name)
    org_suffixes = [
        "Sandia National Laboratories",
        "Oak Ridge National Laboratory",
        "Los Alamos National Laboratory",
        "Argonne National Laboratory",
        "National Laboratories",
        "National Laboratory",
        "University",
        "Corporation",
    ]

    # Only remove suffixes that appear at the end or as separate parts
    for suffix in org_suffixes:
        if cleaned.endswith(suffix):
            cleaned = cleaned[: -len(suffix)].strip()
        elif suffix in cleaned:
            # Split and keep only the first part before the organization
            parts = cleaned.split(suffix)
            cleaned = parts[0].strip()

    # Keep only 2-3 word names (First Middle? Last)
    words = cleaned.split()
    if len(words) > 3:
        # Keep first 2-3 words only
        cleaned = " ".join(words[:3])

    # Final validation: must have at least 2 words
    if len(cleaned.split()) >= 2:
        return cleaned

    return None


def save_results(
    results_per_file,
    global_name_email_dict,
    global_emails,
    output_file="email_name_pairs_per_file.json",
):
    """
    Save the extraction results to a JSON file.

    Args:
        results_per_file: Dictionary of results per file
        global_name_email_dict: Global dictionary of {name: email}
        global_emails: List of all unique emails
        output_file: Path to output JSON file
    """
    # Prepare per-file results with relative paths
    per_file_output = {}
    for file_path, data in results_per_file.items():
        if data["name_email_pairs"] or data["emails"]:  # Only include files with data
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
    print("Extracting email-name pairs from MD files (per-file extraction)...\n")

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
