import os
import re

from bs4 import BeautifulSoup

base_url = "https://www.open-std.org/jtc1/sc22/wg21/docs/papers/"


def parse_1989_html(html_file):
    """Parse 1989 format - Apache directory listing with just filenames"""
    results = []
    with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # Extract links to PDF files
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.endswith(".pdf"):
            # Use filename as paper title, no author info in this format
            paper_title = link.get_text(strip=True)
            # Extract paper ID from filename if possible
            paper_id = os.path.splitext(href)[0]
            results.append(
                {
                    "paper_id": paper_id,
                    "title": paper_title,
                    "authors": [],
                    "filename": href.replace("%20", " "),
                }
            )

    return results


def parse_1990_1991_html(html_file):
    """Parse 1990-1991 format - Apache directory listing with folders"""
    results = []
    # These years have subdirectories, would need additional processing
    # For now, return empty as files might be in subdirectories
    return results


def parse_1992_1999_html(year: int, html_file: str):
    """Parse 1992-1999 format - UL/LI format with <B>title</B> and <I>authors</I>
    Note: LI tags are not closed in these files, so we need to handle this specially."""
    results = []
    with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Split content by <li> tags (case insensitive) to get each entry
    # Since <li> tags are not closed, each <li> marks the start of a new entry
    li_pattern = re.compile(r"<li>", re.IGNORECASE)
    parts = li_pattern.split(content)

    # Skip the first part (before first <li>)
    for part in parts[1:]:
        # Parse this part as HTML
        soup = BeautifulSoup(f"<li>{part}", "html.parser")
        li = soup.find("li")

        if not li:
            continue

        # Extract paper ID and link
        text = li.get_text()
        links = li.find_all("a")

        # Get paper ID from the beginning of the text
        # Prioritize N-numbers (including WG21/N format) over X3J16 format
        match = re.search(r"WG21/([^ ]+)", text, re.IGNORECASE)

        if match:
            paper_id = match.group(1)
        else:
            # Fallback to X3J16 format if WG21 not found
            match = re.search(r"X3J16/([^ ]+)", text, re.IGNORECASE)
            paper_id = match.group(1) if match else ""

        # Extract all URLs from links and categorize them
        urls = []

        for link in links:
            href = link.get("href", "")
            if href:
                urls.append(f"{year}/{href}")

        # Get title from <B> tag
        title_tag = li.find("b")
        title = title_tag.get_text(strip=True) if title_tag else ""

        # Get authors from <I> tag
        authors_tag = li.find("i")
        authors_text = authors_tag.get_text(strip=True) if authors_tag else ""

        # Split authors by comma, semicolon, or "and"
        authors = []
        if authors_text:
            authors = re.split(r"[,;]\s*(?:and\s+)?|\s+and\s+", authors_text)
            authors = [a.strip() for a in authors if a.strip()]

        if paper_id:
            results.append(
                {
                    "paper_id": paper_id,
                    "title": title,
                    "authors": authors,
                    "urls": urls,
                }
            )

    return results


def parse_2000_2001_html(year: int, html_file: str):
    """Parse 2000-2001 format - PRE formatted text with embedded HTML links"""
    results = []
    with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        soup = BeautifulSoup(content, "html.parser")

    # Find all PRE tags
    for pre in soup.find_all("pre"):
        # Get HTML content of pre tag to preserve links
        html_content = str(pre)
        # Split by newlines while keeping track of line content
        lines = html_content.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]
            line_text = BeautifulSoup(line, "html.parser").get_text()

            # Look for paper ID pattern (e.g., "00-0045   N1268" or "99-0032   N1208")
            match = re.match(r"(\d{2}-\d{4}\w*)\s+", line_text)
            if match:
                paper_num = match.group(1)

                # Parse line as HTML to extract links and paper ID
                line_soup = BeautifulSoup(line, "html.parser")
                urls = []
                paper_id = ""

                # Extract all links
                for link in line_soup.find_all("a"):
                    href = link.get("href", "")
                    if href:
                        # Extract filename from href
                        filename = href.split("/")[-1]
                        urls.append(f"{year}/{filename}")

                        # Get paper ID from link text if not already set
                        if not paper_id:
                            paper_id = link.get_text(strip=True)

                # If no link found, try to extract paper ID from text
                if not paper_id:
                    id_match = re.search(r"(N\d+|SD-\d+)", line_text)
                    if id_match:
                        paper_id = id_match.group(1)

                # Extract title and authors from the line
                # Remove paper number and paper ID from the beginning
                remaining = re.sub(r"^\d{2}-\d{4}\w*\s+", "", line_text)
                remaining = re.sub(r"^(N\d+|SD-\d+)\s+", "", remaining)

                # Split remaining text into parts by multiple spaces (typically 2+ spaces separate fields)
                parts = re.split(r"\s{2,}", remaining.strip())

                title = ""
                authors_text = ""

                if len(parts) >= 2:
                    title = parts[0].strip()
                    authors_text = parts[1].strip()
                elif len(parts) == 1:
                    # Might be title only, or need to check next lines
                    title = parts[0].strip()

                # Collect authors from current and subsequent lines
                authors = []
                if authors_text:
                    authors.append(authors_text)

                # Check following lines for continuation (authors or title continuation)
                j = i + 1
                title_parts = []
                while j < len(lines) and j < i + 5:
                    next_line = lines[j]
                    next_text = (
                        BeautifulSoup(next_line, "html.parser").get_text().strip()
                    )

                    # Stop if we hit a new entry
                    if re.match(r"\d{2}-\d{4}", next_text):
                        break

                    # Skip empty lines
                    if not next_text:
                        j += 1
                        continue

                    # If line has content and doesn't look like a new entry
                    if not next_text.startswith("00-") and not next_text.startswith(
                        "99-"
                    ):
                        # Get the original line to check indentation
                        original_line_text = BeautifulSoup(
                            next_line, "html.parser"
                        ).get_text()
                        leading_spaces = len(original_line_text) - len(
                            original_line_text.lstrip()
                        )

                        # Check if it's a title continuation
                        # Priority 1: Has parentheses or specific keywords
                        if re.search(r"\(.*\)", next_text) or re.match(
                            r"(Revision|Version|Part|Vol\.|Volume)",
                            next_text,
                            re.IGNORECASE,
                        ):
                            title_parts.append(next_text)
                            j += 1
                        # Priority 2: If we already have an author and line starts with less indentation (title column ~18 chars)
                        # or doesn't have typical name pattern
                        elif authors_text and (
                            leading_spaces < 40
                            or not re.search(r"[A-Z][a-z]+\s+[A-Z][a-z]+", next_text)
                        ):
                            # If we have author already, and it's not clearly a name, it's likely title
                            if not re.match(r"and\s+[A-Z][a-z]+", next_text):
                                title_parts.append(next_text)
                                j += 1
                            else:
                                # It's an "and Name" pattern - author continuation
                                authors.append(next_text)
                                j += 1
                        # Priority 3: Check if it looks like author continuation (starts with "and")
                        elif re.match(r"and\s+", next_text):
                            authors.append(next_text)
                            j += 1
                        # Priority 4: If no author yet and has name pattern
                        elif not authors_text and re.search(r"[A-Z][a-z]+", next_text):
                            authors.append(next_text)
                            j += 1
                        else:
                            break
                    else:
                        break

                    j += 1

                # Append title parts to title
                if title_parts:
                    title = title + " " + " ".join(title_parts)

                # Clean up authors list - join and split properly
                if authors:
                    authors_combined = " ".join(authors)
                    # Remove extra "and" connectors and split by comma or semicolon
                    authors_combined = re.sub(r"\s+and\s+", ", ", authors_combined)
                    authors_list = re.split(r"[,;]\s*", authors_combined)
                    authors = [a.strip() for a in authors_list if a.strip()]

                if paper_id:
                    results.append(
                        {
                            "paper_id": paper_id,
                            "title": title,
                            "authors": authors,
                            "urls": urls,
                        }
                    )

            i += 1

    return results


def parse_2002_2012_html(year: int, html_file: str):
    """Parse 2002-2012 format - TABLE format with paper_id, paper_num, title, author"""
    results = []
    with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # Find all tables
    for table in soup.find_all("table"):
        rows = table.find_all("tr")

        for row in rows:
            cells = row.find_all("td")

            # Format: paper_id (link), paper_num, title, author, [date]
            if len(cells) >= 3:
                # First cell has the link and paper ID
                link = cells[0].find("a")
                urls = []
                paper_id = ""
                if link:
                    # Extract filename from href
                    urls.append(f"{year}/{link.get("href", "")}")
                    paper_id = link.get_text(strip=True)

                # Second cell might be paper number (e.g., "02-0000", "10-0005")
                paper_num = cells[1].get_text(strip=True) if len(cells) > 1 else ""

                # Third cell is usually the title
                title = cells[2].get_text(strip=True) if len(cells) > 2 else ""

                # Fourth cell is usually the author(s)
                authors_text = cells[3].get_text(strip=True) if len(cells) > 3 else ""

                # Parse authors - split by common delimiters
                authors = []
                if authors_text:
                    # Handle various author separators
                    authors_text = (
                        authors_text.replace("&amp;", ",")
                        .replace("<br />", ",")
                        .replace("<br/>", ",")
                    )
                    authors = re.split(
                        r"[,;]\s*(?:and\s+)?|\s+and\s+|<br\s*/?\s*>|\n", authors_text
                    )
                    authors = [
                        a.strip()
                        for a in authors
                        if a.strip() and not re.match(r"\d{2}-\d{2}-\d{2}", a)
                    ]

                if paper_id:
                    results.append(
                        {
                            "paper_id": paper_id if paper_id else paper_num,
                            "title": title,
                            "authors": authors,
                            "urls": urls,
                        }
                    )

    return results


def parse_2013_2025_html(year: int, html_file: str):
    """Parse 2013-2025 format - TABLE format with paper_id, title, author, dates, etc."""
    results = []
    with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # Find all tables
    for table in soup.find_all("table"):
        rows = table.find_all("tr")

        for row in rows:
            cells = row.find_all("td")

            # Format: paper_id, title, author, document_date, mailing_date, previous_version, subgroup, disposition
            if len(cells) >= 3:
                # First cell has the link and paper ID
                link = cells[0].find("a")
                urls = []
                paper_id = ""
                if link:
                    urls.append(f"{year}/{link.get('href', '')}")
                    paper_id = link.get_text(strip=True)

                # Second cell is the title
                title = cells[1].get_text(strip=True) if len(cells) > 1 else ""

                # Third cell is the author(s)
                authors_text = cells[2].get_text(strip=True) if len(cells) > 2 else ""

                # Parse authors - split by common delimiters
                authors = []
                if authors_text:
                    # Handle various author separators
                    authors_text = (
                        authors_text.replace("&amp;", ",")
                        .replace("<br />", ",")
                        .replace("<br/>", ",")
                    )
                    authors = re.split(
                        r"[,;]\s*(?:and\s+)?|\s+and\s+|<br\s*/?\s*>|\n", authors_text
                    )
                    authors = [
                        a.strip()
                        for a in authors
                        if a.strip() and not re.match(r"\d{2}-\d{2}-\d{2}", a)
                    ]

                if paper_id:
                    results.append(
                        {
                            "paper_id": paper_id,
                            "title": title,
                            "authors": authors,
                            "urls": urls,
                        }
                    )

    return results
