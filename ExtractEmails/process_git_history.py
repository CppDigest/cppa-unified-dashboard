import os
import re
import csv
from collections import defaultdict
from datetime import datetime


def extract_name_email_from_file(file_path: str) -> list[dict]:
    """
    Extract name-email pairs from a git history file.
    Expected format: commit_hash | Name | email | date | commit_message

    Args:
        file_path: Path to the file

    Returns:
        List of dictionaries with 'name' and 'email' keys
    """
    pairs = []

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Split by pipe delimiter
            parts = [part.strip() for part in line.split("|")]

            # Expected format: commit_hash | Name | email | date | commit_message
            if len(parts) >= 3:
                # parts[0] = commit hash
                # parts[1] = name
                # parts[2] = email
                git_hash = parts[0]
                name = parts[1]
                email = parts[2]
                source = (
                    file_path.replace("git_histories\\", "boost/")
                    .replace(".txt", "")
                    .replace("_history", "")
                    .replace("_", "/")
                )

                # Validate email format
                email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
                if re.match(email_pattern, email):
                    pairs.append(
                        {
                            "name": name.strip(),
                            "email": email.strip().lower(),
                            "source": f"git@{source}",
                            "url": git_hash,
                        }
                    )
                else:
                    print(f"  Line {line_num}: Invalid email format: {email}")
            else:
                print(f"  Line {line_num}: Unexpected format (expected 5 fields)")

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return pairs


def normalize_name(name: str) -> str:
    """
    Normalize a name for comparison.
    Removes extra spaces, handles case variations.

    Args:
        name: Name to normalize

    Returns:
        Normalized name
    """
    # Remove extra whitespace
    name = " ".join(name.split())
    return name


def group_emails_by_person(all_pairs: list[dict]) -> dict:
    """
    Group emails by person name.
    One person can have multiple emails.

    Args:
        all_pairs: List of name-email pair dictionaries

    Returns:
        Dictionary mapping normalized names to their email list
    """
    # Use defaultdict to group emails by name
    person_emails = defaultdict(set)
    # Keep original name format (for display)
    name_display = {}

    for pair in all_pairs:
        name = pair["name"]
        email = pair["email"]

        # Normalize name for grouping
        normalized_name = normalize_name(name)

        # Add email to this person's set
        person_emails[normalized_name].add(email)

        # Keep the first occurrence's name format for display
        if normalized_name not in name_display:
            name_display[normalized_name] = name

    # Convert to final format
    result = {}
    for norm_name, emails in person_emails.items():
        display_name = name_display[norm_name]
        result[display_name] = sorted(list(emails))  # Sort emails for consistency

    return result


def process_git_history_folder(folder_path: str) -> dict:
    """
    Process all files in git_history folder.

    Args:
        folder_path: Path to git_history folder

    Returns:
        Dictionary of person names to their email lists
    """
    all_pairs = []
    file_count = 0

    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist")
        return {}

    print(f"Processing files in: {folder_path}")
    print("=" * 80)

    # Process all files in the directory
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_count += 1

            print(f"Processing ({file_count}): {file}")
            pairs = extract_name_email_from_file(file_path)

            if pairs:
                print(f"  Found {len(pairs)} name-email pairs")
                all_pairs.extend(pairs)

    print(f"\nTotal files processed: {file_count}")
    print(f"Total name-email pairs found: {len(all_pairs)}")

    return all_pairs


def save_to_csv(all_pairs: list[dict], output_file: str = None) -> None:
    """
    Save email-name pairs to CSV file.

    Args:
        all_pairs: List of dictionaries with email, name, source, url
        output_file: Output CSV filename (optional)
    """
    if output_file is None:
        output_file = (
            f"git_history_emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

    try:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Email", "Name", "Source", "URL"])

            # Sort by email
            sorted_pairs = sorted(all_pairs, key=lambda x: (x["email"], x["name"]))

            for pair in sorted_pairs:
                writer.writerow(
                    [pair["email"], pair["name"], pair["source"], pair["url"]]
                )

        print(f"\nCSV saved to: {output_file}")
        print(f"Total rows: {len(all_pairs)}")
    except Exception as e:
        print(f"Error saving CSV: {e}")


def save_to_txt(person_data: dict, output_file: str = None) -> None:
    """
    Save person-email data to text file.
    Groups people by number of emails they have.

    Args:
        person_data: Dictionary of names to email lists
        output_file: Output TXT filename (optional)
    """
    if output_file is None:
        output_file = (
            f"git_history_emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("GIT HISTORY - EMAIL COUNT REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            # Group people by email count
            email_count_groups = defaultdict(list)
            for name, emails in person_data.items():
                email_count = len(emails)
                email_count_groups[email_count].append((name, emails))

            # Sort by email count
            sorted_counts = sorted(email_count_groups.keys())

            for count in sorted_counts:
                people = email_count_groups[count]
                # Sort people alphabetically within each group
                people.sort(key=lambda x: x[0])

                f.write(
                    f"\n{count} email{'s' if count > 1 else ''}: {len(people)} member{'s' if len(people) > 1 else ''}\n"
                )
                f.write("-" * 80 + "\n")

                if count == 1:
                    # Don't mention names for people with only 1 email
                    f.write(f"(Names not listed for single-email members)\n")
                else:
                    # List all names and emails for people with multiple emails
                    for i, (name, emails) in enumerate(people, 1):
                        f.write(f"{i}. {name}\n")
                        for email in sorted(emails):
                            f.write(f"   - {email}\n")
                        f.write("\n")

            # Summary
            f.write("\n" + "=" * 80 + "\n")
            f.write("SUMMARY\n")
            f.write("=" * 80 + "\n")
            f.write(f"Total unique people: {len(person_data)}\n")
            total_emails = sum(len(emails) for emails in person_data.values())
            f.write(f"Total unique emails: {total_emails}\n")

            # Distribution
            f.write(f"\nEmail Count Distribution:\n")
            for count in sorted_counts:
                f.write(
                    f"  {count} email{'s' if count > 1 else ''}: {len(email_count_groups[count])} people\n"
                )

        print(f"TXT saved to: {output_file}")
    except Exception as e:
        print(f"Error saving TXT: {e}")


def main():
    """
    Main function to process git_history folder.
    """
    git_history_folder = "git_histories"

    print("GIT HISTORY NAME-EMAIL PROCESSOR")
    print("=" * 80)
    print()

    # Process all files
    all_pairs = process_git_history_folder(git_history_folder)

    if not all_pairs:
        print("\nNo name-email pairs found.")
        return

    # Save results
    print("\n" + "=" * 80)
    print("Saving results...")
    print("=" * 80)

    save_to_csv(all_pairs)


if __name__ == "__main__":
    main()
