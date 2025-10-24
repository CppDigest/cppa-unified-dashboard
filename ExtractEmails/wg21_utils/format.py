import csv
from datetime import datetime

input_file = "csv_data_v1_cleaned.csv"
output_file = f"wg21_paper_email_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"

rows = []

with open(input_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        rows.append(row)

final_rows = []

Base_URL = "https://www.open-std.org/jtc1/sc22/wg21/docs/papers/"


def normalize_url(url: str) -> str:
    """
    Normalize URL by removing redundant path segments.

    Examples:
    - "1995/../1995/SD1.htm" -> "1995/SD1.htm"
    - "2000/../2000/n1401.html" -> "2000/n1401.html"
    - "1995/N0714.htm" -> "1995/N0714.htm" (unchanged)
    """
    if not url:
        return url

    # Split by / and process path segments
    parts = url.replace("\\", "/").split("/")

    # Build normalized path
    normalized = []
    for part in parts:
        if part == "..":
            # Go up one level (remove last segment)
            if normalized:
                normalized.pop()
        elif part and part != ".":
            # Add segment (skip empty and current dir)
            normalized.append(part)

    return "/".join(normalized)


for row in rows:
    new_row = {
        "Email": row["email"],
        "Name": row["author"],
        "Source": "wg21_paper",
        "URL": f"{Base_URL}{normalize_url(row['url'])}",
        "Remark": "",
    }
    if new_row["Email"] == "No Email":
        new_row["Remark"] = "No Email in file"
        new_row["Email"] = ""
    elif new_row["Email"] == "No File":
        new_row["Remark"] = "No File"
        new_row["Email"] = ""
    final_rows.append(new_row)

with open(output_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=final_rows[0].keys())
    writer.writeheader()
    writer.writerows(final_rows)
