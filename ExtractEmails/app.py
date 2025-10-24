"""
Email Extraction Tool - Main Entry Point

This script runs all three email extraction processes:
1. Boost Git History
2. Boost Mailing Lists
3. WG21 Papers

Usage:
    python app.py
"""

import os
import sys
from datetime import datetime


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def check_folder_exists(folder_path: str, create: bool = False) -> bool:
    """
    Check if a folder exists, optionally create it.

    Args:
        folder_path: Path to the folder
        create: Whether to create the folder if it doesn't exist

    Returns:
        True if folder exists (or was created), False otherwise
    """
    if not os.path.exists(folder_path):
        if create:
            os.makedirs(folder_path, exist_ok=True)
            print(f"Created folder: {folder_path}")
            return True
        else:
            return False
    return True


def process_git_history() -> bool:
    """
    Process Boost git commit history files.

    Returns:
        True if successful, False otherwise
    """
    print_header("Processing Boost Git History")

    # Check if git_histories folder exists
    if not check_folder_exists("git_histories"):
        print("⚠ Warning: 'git_histories' folder not found.")
        print("Please create the folder and add git history files, or run:")
        print("  mkdir git_histories")
        return False

    # Check if there are any files to process
    files = os.listdir("git_histories")
    if not files:
        print("⚠ Warning: No files found in 'git_histories' folder.")
        print("Please extract git history using the commands in README.md")
        return False

    try:
        # Import and run the git history processor
        from process_git_history import main as process_git_main

        process_git_main()
        print("✓ Git history processing completed successfully")
        return True
    except Exception as e:
        print(f"✗ Error processing git history: {e}")
        return False


def process_mailing_lists() -> bool:
    """
    Process Boost mailing list JSON files.

    Returns:
        True if successful, False otherwise
    """
    print_header("Processing Boost Mailing Lists")

    # Check if mailing_lists_data folder exists
    if not check_folder_exists("mailing_lists_data"):
        print("⚠ Warning: 'mailing_lists_data' folder not found.")
        print("Please create the folder and add mailing list JSON files, or run:")
        print("  mkdir mailing_lists_data")
        return False

    # Check if there are any email files to process
    files = [
        f
        for f in os.listdir("mailing_lists_data")
        if f.startswith("emails_") and f.endswith(".json")
    ]
    if not files:
        print(
            "⚠ Warning: No 'emails_*.json' files found in 'mailing_lists_data' folder."
        )
        return False

    try:
        # Import and run the mailing list processor
        from process_mailing_lists import main as process_mailing_main

        process_mailing_main()
        print("✓ Mailing list processing completed successfully")
        return True
    except Exception as e:
        print(f"✗ Error processing mailing lists: {e}")
        return False


def process_wg21_papers() -> bool:
    """
    Process WG21 papers (download and extract emails).

    Returns:
        True if successful, False otherwise
    """
    print_header("Processing WG21 Papers")

    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠ Warning: .env file not found.")
        print("Please copy .env.example to .env and configure BASE_URL:")
        print("  cp .env.example .env")
        return False

    # Check if wg21 folder exists
    if not check_folder_exists("wg21"):
        print("⚠ Warning: 'wg21' folder not found.")
        print("Please create the folder and add WG21 HTML index files:")
        print("  mkdir wg21")
        return False

    # Check if there are any HTML files to process
    html_files = [f for f in os.listdir("wg21") if f.endswith(".html")]
    if not html_files:
        print("⚠ Warning: No HTML index files found in 'wg21' folder.")
        print("Please download WG21 year index files (e.g., 2022.html, 2023.html)")
        return False

    # Create output folder if it doesn't exist
    check_folder_exists("output", create=True)

    try:
        # Import and run the WG21 processor
        from process_wg21_paper import download_wg21
        from wg21_utils.data import process_wg21

        print("Downloading WG21 papers...")
        download_wg21()

        print("\nProcessing WG21 papers and extracting emails...")
        process_wg21()

        print("✓ WG21 paper processing completed successfully")
        return True
    except Exception as e:
        print(f"✗ Error processing WG21 papers: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """
    Main function to run all email extractors.
    """
    print("\n" + "=" * 80)
    print("  EMAIL EXTRACTION TOOL")
    print("  Extracting emails from Boost and WG21 sources")
    print("=" * 80)
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    results = {"git_history": False, "mailing_lists": False, "wg21_papers": False}

    # Process each data source
    results["git_history"] = process_git_history()
    results["mailing_lists"] = process_mailing_lists()
    results["wg21_papers"] = process_wg21_papers()

    # Print summary
    print_header("Summary")
    print(
        f"Boost Git History:    {'✓ Success' if results['git_history'] else '✗ Failed/Skipped'}"
    )
    print(
        f"Boost Mailing Lists:  {'✓ Success' if results['mailing_lists'] else '✗ Failed/Skipped'}"
    )
    print(
        f"WG21 Papers:          {'✓ Success' if results['wg21_papers'] else '✗ Failed/Skipped'}"
    )

    total_success = sum(results.values())
    print(f"\nTotal: {total_success}/3 processes completed successfully")

    print("\n" + "=" * 80)
    print(f"  Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")

    # Exit with appropriate code
    sys.exit(0 if total_success > 0 else 1)


if __name__ == "__main__":
    main()
