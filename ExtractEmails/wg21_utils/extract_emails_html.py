"""
Extract email-name pairs from HTML files in the output folder.
This script processes .htm and .html files and attempts to match emails with author names.
"""

import re
import json
from pathlib import Path


def extract_email_name_pairs_from_file(html_file_path):
    """
    Extract email-name pairs and all emails from a single HTML file.

    Args:
        html_file_path: Path to the HTML file

    Returns:
        dict: Contains name_email_pairs, emails list, and file_path
              Returns None if processing fails
    """
    try:
        # Email patterns
        email_pattern = re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        )
        obfuscated_pattern1 = re.compile(
            r"\b([A-Za-z0-9._%-]+)\s+at\s+([A-Za-z0-9.-]+)\s+dot\s+([A-Za-z]{2,})\b",
            re.IGNORECASE,
        )
        obfuscated_pattern2 = re.compile(
            r"\b([A-Za-z0-9._%-]+)\s+at\s+([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b",
            re.IGNORECASE,
        )
        # Pattern 3: "user-at-domain.com" format (hyphen instead of space)
        obfuscated_pattern3 = re.compile(
            r"\b([A-Za-z0-9._%-]+)-at-([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b",
            re.IGNORECASE,
        )
        # Pattern 4: "username -> domain dot tld" format (arrow with dot)
        # Can have "dot" in username: "thorsten dot ottosen -> dezide dot com"
        obfuscated_pattern4 = re.compile(
            r"\b([A-Za-z0-9._%-]+(?:\s+dot\s+[A-Za-z0-9._%-]+)*)\s+->\s+([A-Za-z0-9.-]+(?:\s+dot\s+[A-Za-z0-9.-]+)*)\s+dot\s+([A-Za-z]{2,})\b",
            re.IGNORECASE,
        )
        # Pattern 5: Curly brace notation "{user1,user2}@domain.com"
        # Expands to multiple emails: user1@domain.com, user2@domain.com
        curly_brace_pattern = re.compile(
            r"\{([a-zA-Z0-9._%-]+(?:,[a-zA-Z0-9._%-]+)+)\}@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
        )

        with open(html_file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Extract mailto links BEFORE stripping HTML tags
        # Pattern: <a href="mailto:email@domain.com">Name</a> or <a href="mailto:email@domain.com">Name
        # Note: Some HTML files have unclosed anchor tags, so we make </a> optional
        mailto_pattern = re.compile(
            r'<a[^>]*href="mailto:([^"]+)"[^>]*>([^<]+?)(?:</a>|(?=<))',
            re.IGNORECASE | re.DOTALL,
        )
        mailto_matches = mailto_pattern.findall(content)

        # Extract noscript content BEFORE stripping HTML tags
        # These often contain HTML entity-encoded emails in "at...dot" format
        noscript_pattern = re.compile(
            r"<noscript>(.*?)</noscript>", re.IGNORECASE | re.DOTALL
        )
        noscript_matches = noscript_pattern.findall(content)
        # Decode HTML entities in noscript content
        import html as html_module

        noscript_decoded = [html_module.unescape(ns) for ns in noscript_matches]

        # Extract names from context around noscript tags
        # Pattern: "Reply-to: Name <script>...</script><noscript>..."
        noscript_name_pattern = re.compile(
            r"(?:Reply-?to|Author|From|Contact)\s*:\s*([A-Z][a-zA-Z\s\.\-]+?)\s*<script",
            re.IGNORECASE,
        )
        noscript_names = noscript_name_pattern.findall(content)

        # Strip HTML tags to get text content
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
        # Remove inline formatting tags WITHOUT spaces (to preserve email addresses)
        # These tags are often used to obfuscate emails: <tt>.</tt>, <sup>@</sup>, etc.
        inline_tags = (
            r"</?(?:tt|sup|sub|i|b|em|strong|small|mark|code|span|font|a)[^>]*>"
        )
        text_content = re.sub(inline_tags, "", text_content, flags=re.IGNORECASE)
        # Remove remaining HTML tags WITH spaces (block-level elements)
        text_content = re.sub(r"<[^>]+>", " ", text_content)
        # Decode HTML entities
        text_content = (
            text_content.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
        )
        text_content = text_content.replace("&nbsp;", " ").replace("&#160;", " ")
        text_content = text_content.replace("&#64;", "@")  # Decode @ symbol
        text_content = text_content.replace("&#46;", ".")  # Decode . (dot/period)

        lines = text_content.split("\n")

        name_email_dict = {}

        # Find all regular emails
        emails_in_file = email_pattern.findall(text_content)

        # Process noscript content (already HTML-decoded)
        for idx, noscript_text in enumerate(noscript_decoded):
            # Look for regular emails in noscript
            noscript_emails = email_pattern.findall(noscript_text)
            emails_in_file.extend(noscript_emails)

            # Look for obfuscated patterns in noscript
            obf1_matches = obfuscated_pattern1.findall(noscript_text)
            for user, domain, tld in obf1_matches:
                real_email = f"{user}@{domain}.{tld}"
                emails_in_file.append(real_email)
                # Try to match with name from context
                if idx < len(noscript_names):
                    name = clean_name(noscript_names[idx])
                    if name and name not in name_email_dict:
                        name_email_dict[name] = real_email

            obf2_matches = obfuscated_pattern2.findall(noscript_text)
            for user, domain_with_tld in obf2_matches:
                real_email = f"{user}@{domain_with_tld}"
                emails_in_file.append(real_email)
                # Try to match with name from context
                if idx < len(noscript_names):
                    name = clean_name(noscript_names[idx])
                    if name and name not in name_email_dict:
                        name_email_dict[name] = real_email

        # Find obfuscated emails - pattern 1
        obfuscated_matches1 = obfuscated_pattern1.findall(text_content)
        for user, domain, tld in obfuscated_matches1:
            real_email = f"{user}@{domain}.{tld}"
            emails_in_file.append(real_email)

        # Find obfuscated emails - pattern 2
        obfuscated_matches2 = obfuscated_pattern2.findall(text_content)
        for user, domain_with_tld in obfuscated_matches2:
            real_email = f"{user}@{domain_with_tld}"
            emails_in_file.append(real_email)

        # Find obfuscated emails - pattern 3: "user-at-domain.com"
        obfuscated_matches3 = obfuscated_pattern3.findall(text_content)
        for user, domain_with_tld in obfuscated_matches3:
            real_email = f"{user}@{domain_with_tld}"
            emails_in_file.append(real_email)

        # Find obfuscated emails - pattern 4: "username -> domain dot tld"
        obfuscated_matches4 = obfuscated_pattern4.findall(text_content)
        for user, domain, tld in obfuscated_matches4:
            # Replace "dot" with "." in both username and domain
            user_clean = re.sub(r"\s+dot\s+", ".", user, flags=re.IGNORECASE)
            domain_clean = re.sub(r"\s+dot\s+", ".", domain, flags=re.IGNORECASE)
            real_email = f"{user_clean}@{domain_clean}.{tld}"
            emails_in_file.append(real_email)

        # Find curly brace notation: "{user1,user2}@domain.com"
        curly_brace_matches = curly_brace_pattern.findall(text_content)
        for users, domain_with_tld in curly_brace_matches:
            # Split comma-separated usernames
            usernames = [u.strip() for u in users.split(",")]
            for username in usernames:
                real_email = f"{username}@{domain_with_tld}"
                emails_in_file.append(real_email)

        # Process mailto links extracted before HTML stripping
        for email, name in mailto_matches:
            # Add email to the list
            emails_in_file.append(email)
            # Try to match name with email
            cleaned_name = clean_name(name)
            if cleaned_name and cleaned_name not in name_email_dict:
                name_email_dict[cleaned_name] = email

        unique_emails = sorted(list(set(emails_in_file)))

        # Pattern: "Author: Name1, Name2, Name3" followed by "Contact: email1, email2, email3"
        # Match them up in order
        # Note: Sometimes the names/emails are on the next line after "Author:" / "Contact:"
        for i, line in enumerate(lines):
            if re.search(r"Author\s*:", line, re.IGNORECASE):
                # Found Author line
                # Check if names are on same line or next line
                author_text = re.sub(
                    r"Author\s*:", "", line, flags=re.IGNORECASE
                ).strip()
                if not author_text and i + 1 < len(lines):
                    # Names are on the next line
                    author_text = lines[i + 1].strip()

                if author_text:
                    # Look for Contact line nearby (within next 5 lines)
                    for j in range(i + 1, min(i + 6, len(lines))):
                        contact_line = lines[j]
                        if re.search(r"Contact\s*:", contact_line, re.IGNORECASE):
                            # Extract contact emails
                            contact_text = re.sub(
                                r"Contact\s*:", "", contact_line, flags=re.IGNORECASE
                            ).strip()

                            # Accumulate contact text from multiple lines (emails may be on separate lines)
                            # Continue until we hit an empty line or another field
                            k = j + 1
                            while (
                                k < len(lines) and k < j + 5
                            ):  # Look ahead up to 5 lines
                                next_line = lines[k].strip()
                                # Stop if empty line or another field (contains ":")
                                if not next_line or (
                                    re.search(r"^\w+\s*:", next_line)
                                    and not re.search(r"mailto:", next_line)
                                ):
                                    break
                                # Accumulate this line
                                contact_text += " " + next_line
                                k += 1

                            # Extract author names (can be separated by "," or "&")
                            # Decode HTML entities first
                            author_text_decoded = author_text.replace("&amp;", "&")
                            # Try splitting by comma first, then by &
                            if "," in author_text_decoded:
                                authors = [
                                    name.strip()
                                    for name in author_text_decoded.split(",")
                                    if name.strip()
                                ]
                            else:
                                authors = [
                                    name.strip()
                                    for name in author_text_decoded.split("&")
                                    if name.strip()
                                ]

                            # Extract contact emails (regular pattern)
                            contacts = email_pattern.findall(contact_text)

                            # Also check for obfuscated pattern 4: "username -> domain dot tld"
                            obf4_matches = obfuscated_pattern4.findall(contact_text)
                            for user, domain, tld in obf4_matches:
                                # Replace "dot" with "." in both username and domain
                                user_clean = re.sub(
                                    r"\s+dot\s+", ".", user, flags=re.IGNORECASE
                                )
                                domain_clean = re.sub(
                                    r"\s+dot\s+", ".", domain, flags=re.IGNORECASE
                                )
                                real_email = f"{user_clean}@{domain_clean}.{tld}"
                                contacts.append(real_email)

                            # Match them up in order
                            for idx, author in enumerate(authors):
                                if idx < len(contacts):
                                    cleaned_author = clean_name(author)
                                    if (
                                        cleaned_author
                                        and cleaned_author not in name_email_dict
                                    ):
                                        name_email_dict[cleaned_author] = contacts[idx]
                            break

        # Try to extract name-email pairs from the text
        for i, line in enumerate(lines):
            # Check for regular email
            email_match = email_pattern.search(line)
            if email_match:
                email = email_match.group()
                name = extract_name_from_context(lines, i, email)
                if name and name not in name_email_dict:
                    name_email_dict[name] = email

            # Check for obfuscated email pattern 1
            obf_match1 = obfuscated_pattern1.search(line)
            if obf_match1:
                user, domain, tld = obf_match1.groups()
                real_email = f"{user}@{domain}.{tld}"
                name_pattern = re.compile(
                    r"(?:Reply-to:|From:|Author:)?\s*([A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+)*)\s*[<\.,\s]",
                    re.IGNORECASE,
                )
                name_match = name_pattern.search(line)
                if name_match:
                    name = clean_name(name_match.group(1))
                    if name and name not in name_email_dict:
                        name_email_dict[name] = real_email

            # Check for obfuscated email pattern 2
            obf_match2 = obfuscated_pattern2.search(line)
            if obf_match2:
                user, domain_with_tld = obf_match2.groups()
                real_email = f"{user}@{domain_with_tld}"
                name_pattern = re.compile(
                    r"(?:Reply-to:|From:|Author:)?\s*([A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+)*)\s*[<\.,\s]",
                    re.IGNORECASE,
                )
                name_match = name_pattern.search(line)
                if name_match:
                    name = clean_name(name_match.group(1))
                    if name and name not in name_email_dict:
                        name_email_dict[name] = real_email

            # Check for obfuscated email pattern 3: "Name (user-at-domain.com)"
            obf_match3 = obfuscated_pattern3.search(line)
            if obf_match3:
                user, domain_with_tld = obf_match3.groups()
                real_email = f"{user}@{domain_with_tld}"
                # Try to find name before the obfuscated email (often in parentheses)
                # Pattern: "Name (user-at-domain.com)" or "Name user-at-domain.com"
                name_pattern = re.compile(
                    r"([A-Z][a-zA-Z\-\.]+(?:\s+[A-Z][a-zA-Z\-\.]+)+)\s*\([^)]*"
                    + re.escape(f"{user}-at-{domain_with_tld}"),
                    re.IGNORECASE,
                )
                name_match = name_pattern.search(line)
                if name_match:
                    name = clean_name(name_match.group(1))
                    if name and name not in name_email_dict:
                        name_email_dict[name] = real_email
                else:
                    # Try alternative pattern: "Author: Name" before the email
                    name_pattern2 = re.compile(
                        r"(?:Reply-to:|From:|Author:)?\s*([A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+)*)\s*[<\(\.,\s]",
                        re.IGNORECASE,
                    )
                    name_match2 = name_pattern2.search(line)
                    if name_match2:
                        name = clean_name(name_match2.group(1))
                        if name and name not in name_email_dict:
                            name_email_dict[name] = real_email

            # Check for obfuscated email pattern 4: "username -> domain dot tld"
            obf_match4 = obfuscated_pattern4.search(line)
            if obf_match4:
                user, domain, tld = obf_match4.groups()
                # Replace "dot" with "." in both username and domain
                user_clean = re.sub(r"\s+dot\s+", ".", user, flags=re.IGNORECASE)
                domain_clean = re.sub(r"\s+dot\s+", ".", domain, flags=re.IGNORECASE)
                real_email = f"{user_clean}@{domain_clean}.{tld}"
                # Try to find name before the arrow pattern
                # Look for "Author:" or name on same/previous line
                name_pattern = re.compile(
                    r"(?:Author|Reply-?to|From)\s*:\s*([A-Za-z\s\.\-&;]+?)(?:\s*&\s*[A-Za-z\s\.\-]+)?\s*Contact",
                    re.IGNORECASE | re.DOTALL,
                )
                # Search in multi-line context (combine current and previous lines)
                context = ""
                if i > 0:
                    context = lines[i - 1] + " " + line
                else:
                    context = line

                name_match = name_pattern.search(context)
                if name_match:
                    # Multiple authors may be present, separated by &
                    authors_text = name_match.group(1).strip()
                    # Decode HTML entities in authors text
                    authors_text = authors_text.replace("&amp;", "&")
                    authors = [a.strip() for a in authors_text.split("&")]
                    # Match first author with first email (pattern 4)
                    if authors:
                        name = clean_name(authors[0])
                        if name and name not in name_email_dict:
                            name_email_dict[name] = real_email

            # Check for curly brace pattern: "{user1,user2}@domain.com"
            curly_match = curly_brace_pattern.search(line)
            if curly_match:
                users, domain_with_tld = curly_match.groups()
                usernames = [u.strip() for u in users.split(",")]

                # Look for names before the curly brace pattern
                # Pattern: "Name1; Name2 {user1,user2}@domain" or "Name1, Name2 {user1,user2}@domain"
                text_before_curly = line[: line.find("{")]

                # Try to extract names (separated by semicolon or comma)
                # Remove common prefixes
                text_before_curly = re.sub(
                    r"(?:Author|Reply-?to|From)\s*:\s*",
                    "",
                    text_before_curly,
                    flags=re.IGNORECASE,
                )

                # Split by semicolon or comma
                if ";" in text_before_curly:
                    names = [
                        n.strip() for n in text_before_curly.split(";") if n.strip()
                    ]
                else:
                    names = [
                        n.strip() for n in text_before_curly.split(",") if n.strip()
                    ]

                # Match names with emails in order
                for idx, username in enumerate(usernames):
                    real_email = f"{username}@{domain_with_tld}"
                    if idx < len(names):
                        cleaned_name = clean_name(names[idx])
                        if cleaned_name and cleaned_name not in name_email_dict:
                            name_email_dict[cleaned_name] = real_email

        return {
            "name_email_pairs": name_email_dict,
            "emails": unique_emails,
            "file_path": str(html_file_path),
        }

    except Exception as e:
        print(f"[ERROR] Error processing {html_file_path}: {e}")
        return None


def extract_name_from_context(lines, email_line_idx, email):
    """
    Extract name from the context around the email.

    Args:
        lines: List of text lines
        email_line_idx: Index of the line containing the email
        email: The email address to match

    Returns:
        str: Extracted name or None
    """
    line = lines[email_line_idx]

    # Pattern 1: "Author: Name <email>" or "Author: Name, email"
    author_match = re.search(
        r"(?:Author|Reply-?to|From|Contact)\s*:\s*([A-Za-z][a-zA-Z\s\.\-]+?)(?:\s*[<,]|\s+at\s+)",
        line,
        re.IGNORECASE,
    )
    if author_match:
        name = author_match.group(1).strip()
        cleaned = clean_name(name)
        if cleaned:
            return cleaned

    # Pattern 2: "Name <email>" or "Name, <email>" format
    name_match = re.search(
        r"([A-Z][a-zA-Z\-\.]+(?:\s+[A-Z][a-zA-Z\-\.]+)+)\s*,?\s*<[^>]*"
        + re.escape(email),
        line,
    )
    if name_match:
        name = name_match.group(1).strip()
        return clean_name(name)

    # Pattern 3: "Name - email" format (with hyphen)
    hyphen_match = re.search(
        r"([A-Z][a-zA-Z\-\.]+(?:\s+[A-Z][a-zA-Z\-\.]+)+)\s*-\s*" + re.escape(email),
        line,
    )
    if hyphen_match:
        name = hyphen_match.group(1).strip()
        return clean_name(name)

    # Pattern 4: Email standalone - look at previous lines
    if not re.search(r"[A-Za-z].*" + re.escape(email), line):
        for offset in [1, 2, 3]:
            if email_line_idx - offset >= 0:
                check_line = lines[email_line_idx - offset].strip()
                if not check_line:
                    continue

                # Look for name pattern (with optional trailing comma or punctuation)
                name_match = re.search(
                    r"^([A-Z][a-zA-Z]*\.?\s+)?([A-Z]\.?\s+)?([A-Z][a-zA-Z\-]+)[,.]?$",
                    check_line,
                )
                # Clean up punctuation for word count
                clean_check = check_line.rstrip(",.")
                if name_match and len(clean_check.split()) >= 2:
                    # Skip if it looks like an organization
                    if not re.search(
                        r"\b(Ltd|LLC|Inc|Corp|Corporation|Company|Group|Association|Foundation|Institute)\b",
                        clean_check,
                        re.IGNORECASE,
                    ):
                        cleaned = clean_name(clean_check)
                        if cleaned:
                            return cleaned

    # Pattern 5: Email in the text, name before it
    text_before_email = line[: line.find(email)] if email in line else ""
    if text_before_email:
        # Look for name pattern before email
        name_match = re.search(
            r"([A-Z][a-zA-Z\-\.]+(?:\s+[A-Z][a-zA-Z\-\.]+)+)\s*[,:\s]*$",
            text_before_email,
        )
        if name_match:
            name = name_match.group(1).strip()
            # Skip common non-name words
            if not re.match(
                r"(By|From|Contact|Email|Author|Reply|To|Submitted|Date)",
                name,
                re.IGNORECASE,
            ):
                cleaned = clean_name(name)
                if cleaned:
                    return cleaned

    return None


def clean_name(name):
    """
    Clean up extracted name by removing organizational suffixes and extra text.

    Args:
        name: The extracted name string

    Returns:
        str: Cleaned name or None if invalid
    """
    if not name:
        return None

    cleaned = name.strip()

    # Skip all-caps (usually acronyms or organizations)
    if cleaned.isupper():
        return None

    # Skip if contains organizational indicators (using word boundaries to avoid false positives)
    org_indicators = [
        "Ltd",
        "LLC",
        "Inc",
        "Corp",
        "Corporation",
        "Company",
        "Location",
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
        # Use word boundary to avoid matching "Inn" in "Hinnant", etc.
        if re.search(r"\b" + re.escape(indicator) + r"\b", cleaned, re.IGNORECASE):
            return None

    # Remove organizational suffixes
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

    # Limit to max 3 words (typically first, middle, last name)
    words = cleaned.split()
    if len(words) > 3:
        cleaned = " ".join(words[:3])

    # Validate: at least 2 words, each word should start with capital letter
    words = cleaned.split()
    if len(words) >= 2:
        valid_words = 0
        for word in words:
            if not word:
                continue
            # Handle compound initials like "P.J." or "A.B."
            if re.match(r"^([A-Z]\.)+$", word):  # Handles P.J., A.B., etc.
                valid_words += 1
                continue
            # Regular name word: starts with capital, rest lowercase or has hyphen
            if word[0].isupper() and (word[1:].islower() or "-" in word):
                valid_words += 1
            else:
                return None

        if valid_words >= 2:
            return cleaned

    return None


def extract_email_name_pairs_per_file():
    """
    Extract email-name pairs from all HTML files in the output folder.
    Returns per-file results with name-email pairs and all emails.
    """
    output_dir = Path("output")

    # Find all .htm and .html files
    html_files = sorted(
        list(output_dir.rglob("*.htm")) + list(output_dir.rglob("*.html"))
    )

    print("Extracting email-name pairs from HTML files (per-file extraction)...\n")
    print(f"Found {len(html_files)} HTML files to process\n")

    per_file_results = {}
    global_name_email_dict = {}
    global_emails_set = set()

    for html_file in html_files:
        result = extract_email_name_pairs_from_file(html_file)

        if result:
            # Get relative path from output folder
            relative_path = html_file.relative_to(output_dir)

            per_file_results[str(relative_path)] = {
                "name_email_pairs": result["name_email_pairs"],
                "emails": result["emails"],
            }

            # Update global tracking
            for name, email in result["name_email_pairs"].items():
                if name not in global_name_email_dict:
                    global_name_email_dict[name] = email

            global_emails_set.update(result["emails"])

            print(
                f"[OK] {relative_path}\n"
                f"     - {len(result['name_email_pairs'])} name-email pairs\n"
                f"     - {len(result['emails'])} emails found"
            )

    # Sort results
    sorted_name_email_pairs = dict(sorted(global_name_email_dict.items()))
    sorted_emails = sorted(list(global_emails_set))

    # Print global summary
    print("\n" + "=" * 70)
    print("GLOBAL SUMMARY")
    print("=" * 70)

    print(f"\nName-Email Pairs ({len(sorted_name_email_pairs)} unique pairs):")
    print("-" * 70)
    for name, email in sorted_name_email_pairs.items():
        print(f"{name:<45} -> {email}")

    print("\n" + "=" * 70)

    print(f"\nAll Emails Found ({len(sorted_emails)} unique emails):")
    print("-" * 70)
    for email in sorted_emails:
        print(f"  - {email}")

    print("\n" + "=" * 70)

    # Statistics
    print("\nPer-File Statistics:")
    print("-" * 70)
    print("\nFiles with most name-email pairs (top 10):")
    files_by_pairs = sorted(
        per_file_results.items(),
        key=lambda x: len(x[1]["name_email_pairs"]),
        reverse=True,
    )
    for file_path, data in files_by_pairs[:10]:
        if len(data["name_email_pairs"]) > 0:
            print(f"   {len(data['name_email_pairs'])} pairs - {file_path}")

    # Save to JSON
    output_data = {
        "summary": {
            "total_files": len(html_files),
            "total_unique_emails": len(sorted_emails),
            "total_unique_pairs": len(sorted_name_email_pairs),
        },
        "name_email_pairs": sorted_name_email_pairs,
        "all_emails": sorted_emails,
        "per_file_results": per_file_results,
    }

    output_file = "email_name_pairs_per_file_html.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print(f"Results saved to: {output_file}")
    print("=" * 70)

    return output_data


if __name__ == "__main__":
    extract_email_name_pairs_per_file()
