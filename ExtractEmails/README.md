# Email Extraction Tool

A Python-based tool for extracting and processing name-email pairs from three data sources:

1. **Boost GitHub History** - Extracts contributor information from Boost library git commit logs
2. **Boost Mailing Lists** - Extracts participant information from Boost mailing list JSON exports
3. **WG21 Papers** - Extracts author and contact information from C++ standardization committee papers

## Features

- **Triple Data Source Processing**: Handles Boost git histories, Boost mailing list archives, and WG21 papers
- **Email Normalization**: Converts emails to lowercase and handles special formatting (e.g., `(a)` → `@`)
- **Validation**: Validates email formats using regex patterns
- **Deduplication**: Groups emails by person to identify multiple email addresses per contributor
- **Multiple Output Formats**: Exports data as CSV for easy analysis
- **Comprehensive Reporting**: Provides detailed statistics and processing summaries
- **PDF/HTML/Text Processing**: Extracts emails from various document formats in WG21 papers

## Requirements

- Python 3.9 or higher (uses modern type hints with `list[dict]` syntax)
- External dependencies: requests, beautifulsoup4, PyPDF2, python-dotenv (see requirements.txt)

## Installation

1. Clone or download this repository

2. Ensure you have Python 3.9+ installed:

   ```bash
   python --version
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy the `.env.example` file to `.env` and configure:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and set the `BASE_URL` for WG21 papers (e.g., `https://www.open-std.org/jtc1/sc22/wg21/docs/papers/`)

## Project Structure

```
ExtractEmails/
├── process_git_history.py      # Processes Boost git commit history files
├── process_mailing_lists.py    # Processes Boost mailing list JSON files
├── process_wg21_paper.py       # Downloads and processes WG21 papers
├── app.py                      # Main entry point to run all extractors
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── README.md                   # This file
├── wg21_utils/                 # Utilities for WG21 paper processing
├── git_histories/              # Input folder for git history files (not included)
├── mailing_lists_data/         # Input folder for mailing list JSON files (not included)
├── wg21/                       # WG21 HTML index files (not included)
└── output/                     # Downloaded WG21 papers (not included)
```

## Usage

### Quick Start - Run All Extractors

To run all three extractors in sequence:

```bash
python app.py
```

This will process:

1. Boost Git Histories
2. Boost Mailing Lists
3. WG21 Papers (if configured)

### Extracting Boost Git History

#### Step 1: Clone Boost Repository with Submodules

```bash
# Clone the Boost repository
git clone --recurse-submodules https://github.com/boostorg/boost.git boost_repo

# Or if already cloned, initialize submodules
cd boost_repo
git submodule update --init --recursive
```

#### Step 2: Extract All Commit History (Including Submodules)

```bash
# Navigate to the Boost repository
cd boost_repo

# Extract commit history from main repository
git log --all --format="%H | %an | %ae | %ad | %s" > ../git_histories/boost_main_history.txt

# Extract commit history from all submodules
git submodule foreach --recursive 'git log --all --format="%H | %an | %ae | %ad | %s" > "$toplevel/git_histories/${name}_history.txt"'

# Alternative: Extract all in one go with submodule paths
git submodule foreach --recursive 'echo "Processing: $name" && git log --all --format="%H | %an | %ae | %ad | %s" > "$toplevel/git_histories/$(echo $sm_path | tr / _)_history.txt"'
```

#### Step 3: Process the Extracted Histories

```bash
cd ..
python process_git_history.py
```

**Input Format**: Text files with pipe-delimited data:

```
commit_hash | Name | email | date | commit_message
```

**Example**:

```
a1b2c3d4 | John Doe | john.doe@example.com | 2024-01-15 | Fixed bug in parser
```

### Processing Boost Mailing Lists

1. Place your Boost mailing list JSON files in the `mailing_lists_data/` folder
2. Run the script:
   ```bash
   python process_mailing_lists.py
   ```

**Input Format**: JSON files starting with `emails_*.json` containing:

```json
{
  "results": [
    {
      "sender_name": "Jane Smith",
      "sender": {
        "address": "jane.smith (a) example.com"
      },
      "url": "https://lists.boost.org/message/123"
    }
  ]
}
```

Or content files format:

```json
[
  {
    "content": {
      "sender_name": "Jane Smith",
      "sender": {
        "address": "jane.smith (a) example.com"
      },
      "url": "https://lists.boost.org/message/123"
    }
  }
]
```

### Processing WG21 Papers

1. Download WG21 HTML index files into the `wg21/` folder (e.g., `2022.html`, `2023.html`, etc.)
2. Configure the `BASE_URL` in your `.env` file
3. Run the script:
   ```bash
   python process_wg21_paper.py
   ```

This will:

- Parse the HTML index files
- Download papers (PDF, HTML, TXT, MD, PS, ASC formats)
- Extract emails from paper contents
- Generate CSV output with author-email mappings

## Output

All scripts generate timestamped CSV files with the following columns:

| Column | Description                                                                    |
| ------ | ------------------------------------------------------------------------------ |
| Email  | Email address (normalized to lowercase)                                        |
| Name   | Person's name or author name                                                   |
| Source | Data source identifier (e.g., `git@boost/algorithm`, `mailing_list`)           |
| URL    | Reference URL (commit hash for git, message URL for lists, paper URL for WG21) |

**Example Outputs**:

- `git_history_emails_20241023_143022.csv` - Boost git commit history
- `mailing_list_emails_20241023_143022.csv` - Boost mailing list participants
- `csv_data_v1.csv` - WG21 paper authors and extracted emails

```csv
Email,Name,Source,URL
jane.smith@example.com,Jane Smith,mailing_list,https://lists.boost.org/message/123
john.doe@example.com,John Doe,git@boost/algorithm,a1b2c3d4
author@cpp.com,C++ Author,wg21,https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p1234r0.pdf
```

## Features in Detail

### Email Normalization

- Converts all emails to lowercase for consistency
- Replaces `(a)` with `@` (common obfuscation in mailing lists)
- Validates email format using regex

### Data Validation

- Skips entries with missing or invalid email addresses
- Handles malformed JSON gracefully
- Provides detailed error messages for debugging

### Processing Statistics

- Reports number of files processed
- Shows count of extracted email pairs
- Displays progress during processing

### Grouping Capabilities

The scripts include functions to group multiple emails by person name (currently disabled in main execution, but available for use):

- `group_emails_by_person()`: Groups emails by normalized names
- `save_to_txt()`: Generates reports showing email distribution

## Troubleshooting

### "Folder does not exist" error

Ensure the required input folders exist:

```bash
mkdir git_histories
mkdir mailing_lists_data
mkdir wg21
mkdir output
```

### Git submodule extraction fails

If you encounter issues extracting submodule history, try:

```bash
# Ensure all submodules are initialized
git submodule update --init --recursive

# Force update all submodules
git submodule foreach --recursive git fetch --all
```

### "No name-email pairs found"

- Check that input files are in the correct format
- For git histories: Ensure files contain pipe-delimited data
- For mailing lists: Ensure JSON files start with `emails_` prefix

### JSON parsing errors

- Validate JSON structure using a JSON validator
- Check file encoding (should be UTF-8)
- Look for null/None values in the data

## License

This project is part of the CPPA Unified Dashboard project.

## Contributing

For questions or contributions, please contact the project maintainers.
