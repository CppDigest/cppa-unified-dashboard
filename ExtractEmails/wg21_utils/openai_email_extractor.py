"""
OpenAI-based Email Extraction Class

Complete class for extracting emails and matching names using OpenAI API.
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv not installed, will use system environment variables


class OpenAIEmailExtractor:
    """
    Complete email extraction and processing using OpenAI API.

    Features:
    - Extract emails from text using GPT models
    - Match emails with author names
    - Process PDF, HTML, and text files
    - Support for obfuscated email formats
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
        max_tokens: int = 1000,
    ):
        """
        Initialize OpenAI Email Extractor.

        Args:
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
            model: OpenAI model to use (default: gpt-4o-mini - fast and cheap)
            temperature: Temperature for generation (0.0-1.0, lower = more deterministic)
            max_tokens: Maximum tokens for response
        """
        try:
            import openai

            self.openai = openai
        except ImportError:
            raise ImportError(
                "openai package not installed. Install with: pip install openai"
            )

        # Get API key
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No OpenAI API key provided. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Initialize OpenAI client
        self.client = self.openai.OpenAI(
            base_url="https://openrouter.ai/api/v1", api_key=self.api_key
        )
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _extract_text_around_emails(self, text: str, max_length: int = 5000) -> str:
        """
        Find first email pattern and extract text around it.

        Args:
            text: Full text content
            max_length: Maximum excerpt length

        Returns:
            Text excerpt containing email context
        """
        # Email patterns to search for
        patterns = [
            r"@",  # Standard @ symbol
            r"\sat\s",  # " at " with spaces
            r"-at-",  # "-at-" format
            r"_at_",  # "_at_" format
            r"\(at\)",  # "(at)" format
            r"(at)",
            r" at ",
        ]

        # Find first occurrence of any email pattern
        first_pos = -1
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                pos = match.start()
                if first_pos == -1 or pos < first_pos:
                    first_pos = pos
                    start = max(0, first_pos - 1000)
                    end = min(len(text), first_pos + 4000)
                    return text[start:end]

        # If email pattern found, extract around it (1000 before, 4000 after)
        if first_pos != -1:
            start = max(0, first_pos - 1000)
            end = min(len(text), first_pos + 4000)
            return text[start:end]

        # If no email pattern found, use default (first max_length chars)
        return text[:max_length]

    def extract_emails_from_text(self, text: str, max_length: int = 5000) -> List[str]:
        """
        Extract all email addresses from text using OpenAI.

        Args:
            text: Text content to extract emails from
            max_length: Maximum text length to process (to save tokens)

        Returns:
            List of unique email addresses found
        """
        # Find first email pattern and extract text around it
        text_excerpt = self._extract_text_around_emails(text, max_length)

        # Create prompt
        prompt = f"""Extract ALL email addresses from the following text.
Include regular emails (user@domain.com) and obfuscated formats like:
- "user at domain dot com"
- "user-at-domain.com"
- "username -> domain dot tld"

Return ONLY a valid JSON array of email addresses, nothing else.
If no emails are found, return an empty array [].

Text:
{text_excerpt}

Return format (valid JSON array only, no explanation):
["email1@domain.com", "email2@domain.com"]"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise email extraction assistant. Extract all email addresses from text and return only a valid JSON array.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            # Parse response
            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            content = re.sub(r"```json\s*", "", content)
            content = re.sub(r"```\s*", "", content)
            content = content.strip()

            # Try to extract JSON array
            if "[" in content and "]" in content:
                start = content.find("[")
                end = content.rfind("]") + 1
                content = content[start:end]

            # Parse JSON
            emails = json.loads(content)

            # Validate and clean
            if not isinstance(emails, list):
                print(f"Warning: API returned non-list result")
                return []

            # Filter valid emails
            valid_emails = []
            for email in emails:
                email_str = str(email).strip()
                if "@" in email_str and "." in email_str:
                    valid_emails.append(email_str)

            return sorted(list(set(valid_emails)))

        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse API response as JSON: {e}")
            return []
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return []

    def match_names_to_emails(
        self, text: str, emails: List[str], max_length: int = 3000
    ) -> Dict[str, str]:
        """
        Match author names to email addresses using OpenAI.

        Args:
            text: Document text content
            emails: List of email addresses to find names for
            max_length: Maximum text length to process

        Returns:
            Dictionary mapping author names to email addresses
        """
        if not emails:
            return {}

        # Find first email pattern and extract text around it
        text_excerpt = self._extract_text_around_emails(text, max_length)

        # Create prompt
        prompt = f"""Find the author names associated with the following email addresses in the document text.
Return ONLY a valid JSON object mapping author names to their email addresses.
If a name is not found for an email, omit that email from the result.
Look for patterns like "Reply to: Name" followed by an email, or "Name <email>", or "Name (email)".

Email addresses to find names for:
{json.dumps(emails, indent=2)}

Document text:
{text_excerpt}

Return format (valid JSON only, no explanation):
{{
  "Author Name": "email@domain.com",
  "Another Author": "another@domain.com"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise data extraction assistant. Find author names for email addresses and return only valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            # Parse response
            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks
            content = re.sub(r"```json\s*", "", content)
            content = re.sub(r"```\s*", "", content)
            content = content.strip()

            # Try to extract JSON object
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                content = content[start:end]

            # Parse JSON
            result = json.loads(content)

            # Validate result
            if not isinstance(result, dict):
                print(f"Warning: API returned non-dict result")
                return {}

            # Filter to only requested emails
            valid_result = {}
            for name, email in result.items():
                if email in emails:
                    valid_result[name] = email

            return valid_result

        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse API response as JSON: {e}")
            return {}
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return {}

    def extract_from_text(
        self, text: str
    ) -> Tuple[List[Tuple[str, str]], Dict[str, str]]:
        """
        Complete extraction: find emails and match with names.

        Args:
            text: Document text content

        Returns:
            Tuple of (pairs_list, name_email_dict):
            - pairs_list: List of (name, email) tuples
            - name_email_dict: Dictionary mapping names to emails
        """
        # Step 1: Extract all emails
        emails = self.extract_emails_from_text(text)

        if not emails:
            return [], {}

        # Step 2: Match names to emails
        name_email_dict = self.match_names_to_emails(text, emails)

        # Step 3: Create pairs list
        pairs = [(name, email) for name, email in name_email_dict.items()]

        return pairs, name_email_dict

    def extract_from_file(
        self, file_path: str
    ) -> Tuple[List[Tuple[str, str]], Dict[str, str]]:
        """
        Extract emails and name-email pairs from a file.

        Args:
            file_path: Path to file (PDF, HTML, TXT, etc.)

        Returns:
            Tuple of (pairs_list, name_email_dict)
        """
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            print(f"Error: File not found: {file_path}")
            return [], {}

        # Read file content
        try:
            content = self._read_file_content(file_path_obj)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return [], {}

        # Extract emails and names
        return self.extract_from_text(content)

    def _read_file_content(self, file_path: Path) -> str:
        """
        Read content from different file types.

        Args:
            file_path: Path to the file

        Returns:
            File content as text
        """
        extension = file_path.suffix.lower()

        if extension in [".html", ".htm"]:
            return self._read_html_file(file_path)
        elif extension in [".txt", ".md", ".asc"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        elif extension == ".pdf":
            try:
                import pdfplumber

                with pdfplumber.open(file_path) as pdf:
                    text = ""
                    cnt = 0
                    for page in pdf.pages:
                        if cnt > 5:
                            break
                        cnt += 1
                        text += page.extract_text() or ""
                    return text
            except ImportError:
                print(
                    "Warning: pdfplumber not installed. Install: pip install pdfplumber"
                )
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading PDF: {e}")
                return ""
        elif extension == ".ps":
            return self._read_postscript_file(file_path)
        else:
            # Default: try to read as text
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

    def _read_postscript_file(self, file_path: Path) -> str:
        """ """
        import subprocess
        import tempfile

        # Try to convert PS to PDF using Ghostscript
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            try:

                new_content = content.split("%%EndSetup")[1]
                # Try common Ghostscript executable names
                return new_content
            except Exception as e:
                print(f"Error splitting content: {e}")
                return content

        except Exception as e:
            # If conversion fails, fall back to reading as text
            pass

        # Fallback: read as plain text (will include PostScript code)
        # But smart extraction will still find emails
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _read_html_file(self, file_path: Path) -> str:
        """
        Read and clean HTML file content.

        Args:
            file_path: Path to HTML file

        Returns:
            Cleaned text content
        """
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Remove script and style elements
        text_content = re.sub(
            r"<script[^>]*>.*?</script>", " ", content, flags=re.DOTALL | re.IGNORECASE
        )
        text_content = re.sub(
            r"<style[^>]*>.*?</style>",
            " ",
            text_content,
            flags=re.DOTALL | re.IGNORECASE,
        )

        # Remove inline tags without spaces (preserve emails)
        # inline_tags = (
        #     r"</?(?:tt|sup|sub|i|b|em|strong|small|mark|code|span|font|a)[^>]*>"
        # )
        # text_content = re.sub(inline_tags, "", text_content, flags=re.IGNORECASE)

        # Remove remaining HTML tags with spaces
        # text_content = re.sub(r"<[^>]+>", " ", text_content)

        # Decode HTML entities
        text_content = (
            text_content.replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&amp;", "&")
            .replace("&nbsp;", " ")
            .replace("&#160;", " ")
            .replace("&#64;", "@")
            .replace("&#46;", ".")
        )

        return text_content

    def process_directory(
        self, directory: str, pattern: str = "*.pdf", output_dir: str = "openai_results"
    ) -> Dict[str, Dict]:
        """
        Process all files in a directory.

        Args:
            directory: Directory path to process
            pattern: File pattern to match (default: *.pdf)
            output_dir: Directory to save results

        Returns:
            Dictionary with processing results
        """
        dir_path = Path(directory)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Find all matching files
        files = sorted(list(dir_path.rglob(pattern)))

        print(f"Found {len(files)} files matching pattern: {pattern}")
        results = {}

        for idx, file_path in enumerate(files, 1):
            relative_path = file_path.relative_to(dir_path)
            print(f"[{idx}/{len(files)}] {relative_path}")

            try:
                pairs, name_dict = self.extract_from_file(str(file_path))

                result = {
                    "file_path": str(relative_path),
                    "all_emails": sorted(list(set(name_dict.values()))),
                    "all_pairs": [{"name": n, "email": e} for n, e in pairs],
                }

                results[str(relative_path)] = result

                # Save individual JSON
                json_filename = str(relative_path).replace("\\", "_").replace("/", "_")
                json_filename = json_filename.replace(file_path.suffix, ".json")
                json_file_path = output_path / json_filename

                with open(json_file_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)

            except Exception as e:
                print(f"Error: {e}")
                results[str(relative_path)] = {
                    "file_path": str(relative_path),
                    "error": str(e),
                }

        print(f"\nProcessed {len(results)} files")
        print(f"Results saved in: {output_dir}/")

        return results

    def __repr__(self):
        """String representation of the extractor."""
        return f"OpenAIEmailExtractor(model='{self.model}', temperature={self.temperature})"


# Example usage
if __name__ == "__main__":
    import sys

    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("=" * 70)
        print("ERROR: OPENAI_API_KEY environment variable not set")
        print("=" * 70)
        print("\nSet your OpenAI API key:")
        print("  Windows: $env:OPENAI_API_KEY='your-api-key-here'")
        print("  Linux/Mac: export OPENAI_API_KEY='your-api-key-here'")
        print("\nOr pass it to the constructor:")
        print("  extractor = OpenAIEmailExtractor(api_key='your-api-key-here')")
        print("=" * 70)
        sys.exit(1)

    # Create extractor instance
    print("=" * 70)
    print("OpenAI Email Extractor - Example Usage")
    print("=" * 70)

    extractor = OpenAIEmailExtractor(model="gpt-4o-mini")
    print(f"Initialized: {extractor}")
    print("=" * 70)

    # Test with sample text
    sample_text = """

    """
    # Create extractor instance
    print("=" * 70)
    print("OpenAI Email Extractor - Example Usage")
    print("=" * 70)

    extractor = OpenAIEmailExtractor(model="gpt-4o-mini")
    print(f"Initialized: {extractor}")
    print("=" * 70)

    # Test with sample text
    sample_text = """
    Doc Number: X3J16/92-0053
    WG21/N0130
    Date: June 2, 1992
    Project: Programming Language C++
    Reply to: Samuel C. Kendall
              CenterLine Software, Inc.
              10 Fawcett Street
              Cambridge, MA 02138
              kendall@centerline.com
    
    Contact: john at example dot com
    Alternative: jane-at-domain.org
    """

    print("\nTest 1: Extract emails from text")
    print("-" * 70)
    emails = extractor.extract_emails_from_text(sample_text)
    print(f"Found {len(emails)} email(s):")
    for email in emails:
        print(f"  • {email}")

    print("\n" + "=" * 70)
    print("Test 2: Extract emails and match names")
    print("-" * 70)
    pairs, name_dict = extractor.extract_from_text(sample_text)
    print(f"Found {len(pairs)} name-email pair(s):")
    for name, email in pairs:
        print(f"  • {name} -> {email}")

    print("\n" + "=" * 70)
    print("Test 3: Process a file")
    print("-" * 70)
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"Processing: {file_path}")
        pairs, name_dict = extractor.extract_from_file(file_path)
        print(f"Found {len(pairs)} name-email pair(s):")
        for name, email in pairs:
            print(f"  • {name} -> {email}")
    else:
        print("No file provided. Usage: python openai_email_extractor.py <file_path>")

    print("\n" + "=" * 70)
    print("Examples complete!")
    print("=" * 70)
