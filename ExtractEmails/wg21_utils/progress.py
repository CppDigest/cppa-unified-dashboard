import re
import PyPDF2
from extract_emails_md import extract_email_name_pairs_from_file as extract_md
from extract_emails_txt import extract_email_name_pairs_from_file as extract_txt
from extract_emails_html import extract_email_name_pairs_from_file as extract_html


def extract_emails_from_text(text):
    # Handles patterns like "user at sub.domain dot com"
    try:
        message_all_list = []
        if "@" in text:
            message_all_list.append("exists")
        pattern = r"\b([\w\.\-_]+)\s+at\s+([\w\.\-_]+)\s+dot\s+(\w+)\b"
        matches = re.findall(pattern, text)
        for match in matches:
            message_all_list.append(f"{match[0]}@{match[1]}.{match[2]}")
        return message_all_list
    except Exception as e:
        print(f"Error extracting emails from text: {e}")
        return ["error"]


def clean_pdf_text(text):
    text = text.replace("/n40", "@")
    text = re.sub(r"/n([0-7]{2})", lambda m: chr(int(m.group(1), 8)), text)
    return text


def extract_text_from_postscript(ps_content):
    """Extract readable text from PostScript file

    PostScript files can use different formats:
    1. FrameMaker format: (text) X Y T
    2. Windows PSCRIPT format: (text) show/ashow/widthshow/awidthshow
    """

    # Try FrameMaker format first: (text) X Y T
    pattern_framemaker = r"\(([^)]+)\)\s+([\d.]+)\s+([\d.]+)\s+T"
    matches_fm = re.findall(pattern_framemaker, ps_content)

    # Try Windows PSCRIPT format: (text) ...show commands
    # This pattern matches text in parentheses before show commands
    pattern_show = r"\(([^)]+)\)"

    lines_dict = {}

    if matches_fm:
        # Use FrameMaker format with coordinates
        for text, x, y in matches_fm:
            # Clean up PostScript escape sequences
            text = text.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")

            # Round Y coordinate to group text on same line
            y_rounded = round(float(y))

            if y_rounded not in lines_dict:
                lines_dict[y_rounded] = []

            lines_dict[y_rounded].append((float(x), text))

        # Sort lines by Y coordinate (descending - top to bottom)
        sorted_y = sorted(lines_dict.keys(), reverse=True)

        # Build text lines
        text_lines = []
        for y in sorted_y:
            # Sort text fragments by X coordinate (left to right)
            fragments = sorted(lines_dict[y], key=lambda item: item[0])
            line_text = " ".join([text for x, text in fragments])
            text_lines.append(line_text)

        return "\n".join(text_lines)
    else:
        # Fall back to simpler extraction for Windows PSCRIPT format
        # Just extract all text in parentheses and join with spaces
        matches_show = re.findall(pattern_show, ps_content)

        text_fragments = []
        for text in matches_show:
            # Clean up PostScript escape sequences
            text = text.replace("\\(", "(").replace("\\)", ")").replace("\\\\", "\\")

            # Skip empty or very short fragments (likely formatting)
            if len(text.strip()) > 0:
                text_fragments.append(text)

        # Join fragments with spaces, add newlines on certain patterns
        result = []
        current_line = []

        for text in text_fragments:
            # Check if this looks like start of new line
            if (
                text.startswith("X3J16")
                or text.startswith("Doc ")
                or text.startswith("Date:")
                or text.startswith("Reply")
                or text.startswith("Author")
                or len(current_line) > 15
            ):
                if current_line:
                    result.append(" ".join(current_line))
                    current_line = []

            current_line.append(text)

        # Add remaining line
        if current_line:
            result.append(" ".join(current_line))

        return "\n".join(result)


def process_pdf(pdf_path, use_ai_fallback=True):
    try:

        with open(pdf_path, "rb") as f:
            pdf = PyPDF2.PdfReader(f)
            text = ""
            page_num = min(len(pdf.pages), 5)
            for page in pdf.pages[:page_num]:
                text += page.extract_text()
            return extract_emails_from_text(clean_pdf_text(text))
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return ["error"]


def process_html(html_path, use_ai_fallback=True):
    try:
        results = extract_html(html_path)
        emails = results["emails"]
        name_email_dict = results["name_email_pairs"]
        return emails, name_email_dict
    except Exception as e:
        print(f"Error processing HTML: {e}")
        return ["error"], {}


def process_text(text_path, use_ai_fallback=True):
    try:

        results = extract_txt(text_path)
        emails = results["emails"]
        name_email_dict = results["name_email_pairs"]
        return emails, name_email_dict
    except Exception as e:
        print(f"Error processing Text: {e}")
        return ["error"], {}


def process_asc(asc_path, use_ai_fallback=True):
    try:
        with open(asc_path, "r", encoding="utf-8", errors="ignore") as f:
            asc = f.read()
            return extract_emails_from_text(asc)
    except Exception as e:
        print(f"Error processing ASC: {e}")
        return ["error"]


def process_md(md_path, use_ai_fallback=True):
    try:
        results = extract_md(md_path)
        emails = results["emails"]
        name_email_dict = results["name_email_pairs"]
        return emails, name_email_dict
    except Exception as e:
        print(f"Error processing MD: {e}")
        return ["error"], {}, []


def process_ps(ps_path, use_ai_fallback=True):
    """Extract email addresses and author-email mappings from a PostScript file"""
    all_emails = []

    try:
        with open(ps_path, "r", encoding="utf-8", errors="ignore") as f:
            ps_content = f.read()

            # Extract readable text from PostScript
            text = extract_text_from_postscript(ps_content)

            # Only process first ~500 lines of PS for performance
            # (author info is typically at the beginning)
            ps_lines = ps_content.split("\n")[:500]
            ps_header = "\n".join(ps_lines)

            # Also extract text directly from PS header
            header_text = extract_text_from_postscript(ps_header)

            # Extract emails from both
            all_emails_text = extract_emails_from_text(text)
            all_emails_header = extract_emails_from_text(header_text)
            all_emails = list(set(all_emails_text + all_emails_header))

            return all_emails
    except Exception as e:
        print(f"Error processing PostScript: {e}")
        return [], {}
