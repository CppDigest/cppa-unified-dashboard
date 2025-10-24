import os
import json
import csv
from urllib.parse import urljoin

from first_process import (
    parse_1989_html,
    parse_1990_1991_html,
    parse_1992_1999_html,
    parse_2000_2001_html,
    parse_2002_2012_html,
    parse_2013_2025_html,
)

from download import download
from progress import (
    process_pdf,
    process_ps,
    process_html,
    process_text,
    process_asc,
    process_md,
)


def process_wg21():
    wg21_folder = "wg21"
    years_data = {}

    for year in range(1992, 2000):
        years_data[year] = parse_1992_1999_html

    for year in range(2000, 2002):
        years_data[year] = parse_2000_2001_html
    for year in range(2002, 2013):
        years_data[year] = parse_2002_2012_html
    for year in range(2013, 2026):
        years_data[year] = parse_2013_2025_html

    csv_data_v1 = []
    processed_file_ids = []
    not_processed_file_ids = []
    # Read existing processed data from JSON
    if os.path.exists("processed_data_v1.json"):
        with open("processed_data_v1.json", "r", encoding="utf-8") as f:
            csv_data_v1 = json.load(f)
            for row in csv_data_v1:
                processed_file_ids.append(f"{row['year']}/{row['file_name']}")

    for year in range(1992, 2026):
        html_file = f"{wg21_folder}/{year}.html"
        cnt = 0
        if os.path.exists(html_file):
            parse_func = years_data[year]
            results = parse_func(year, html_file)
            for result in results:
                for url in result["urls"]:
                    file_name = url.split("/")[-1]
                    if f"{year}/{url.split('/')[-1]}" in processed_file_ids:
                        continue
                    if not os.path.exists(os.path.join(f"output/{year}", file_name)):
                        for author in result["authors"]:
                            csv_data_v1.append(
                                {
                                    "year": year,
                                    "paper_id": result["paper_id"],
                                    "title": result["title"],
                                    "author": author,
                                    "url": url,
                                    "file_name": file_name,
                                    "email": "No File",
                                }
                            )
                    else:
                        emails = []
                        author_mapping = {}

                        if file_name.endswith(".md"):
                            emails, name_email_dict = process_md(
                                os.path.join(f"output/{year}", file_name), False
                            )
                        elif file_name.endswith(".txt"):
                            emails, name_email_dict = process_text(
                                os.path.join(f"output/{year}", file_name), False
                            )
                        elif file_name.endswith(".ps"):
                            emails = process_ps(
                                os.path.join(f"output/{year}", file_name), False
                            )
                        elif file_name.endswith(".pdf"):
                            emails = process_pdf(
                                os.path.join(f"output/{year}", file_name), False
                            )
                        elif file_name.endswith(".asc"):
                            emails = process_asc(
                                os.path.join(f"output/{year}", file_name), False
                            )
                        # elif :
                        #     emails, name_email_dict = process_html(
                        #         os.path.join(f"output/{year}", file_name), False
                        #     )
                        elif file_name.endswith(".pdf"):
                            emails, name_email_dict = process_pdf(year, file_name)
                        elif (
                            file_name.endswith(".asc")
                            or file_name.endswith(".ps")
                            or file_name.endswith(".html")
                            or file_name.endswith(".htm")
                        ):
                            emails, name_email_dict = process_asc(year, file_name)
                        else:
                            not_processed_file_ids.append(f"{year}/{file_name}")
                            continue
                        if len(emails) == 0:
                            not_processed_file_ids.append(f"{year}/{file_name}")
                            continue
                            # for author in result["authors"]:

                            # csv_data_v1.append(
                            #     {
                            #         "year": year,
                            #         "paper_id": result["paper_id"],
                            #         "title": result["title"],
                            #         "author": author,
                            #         "url": url,
                            #         "file_name": file_name,
                            #         "email": "No Email",
                            #     }
                            # )

                        elif file_name.endswith(".txt") or file_name.endswith(".md"):
                            pass
                        elif (
                            file_name.endswith(".html")
                            or file_name.endswith(".htm")
                            or file_name.endswith(".pdf")
                            or file_name.endswith(".asc")
                            or file_name.endswith(".ps")
                        ):
                            if len(name_email_dict) > 0:
                                for name, email in name_email_dict.items():
                                    csv_data_v1.append(
                                        {
                                            "year": year,
                                            "paper_id": result["paper_id"],
                                            "title": result["title"],
                                            "author": name,
                                            "url": url,
                                            "file_name": file_name,
                                            "email": email,
                                        }
                                    )
                                    if email in emails:
                                        emails.remove(email)
                            for author in result["authors"]:
                                if author not in name_email_dict:
                                    if len(emails) > 0:
                                        csv_data_v1.append(
                                            {
                                                "year": year,
                                                "paper_id": result["paper_id"],
                                                "title": result["title"],
                                                "author": author,
                                                "url": url,
                                                "file_name": file_name,
                                                "email": "Estimated Email List: "
                                                + ",".join(emails),
                                            }
                                        )
                                    else:
                                        csv_data_v1.append(
                                            {
                                                "year": year,
                                                "paper_id": result["paper_id"],
                                                "title": result["title"],
                                                "author": author,
                                                "url": url,
                                                "file_name": file_name,
                                                "email": "No Email",
                                            }
                                        )
                        else:
                            not_processed_file_ids.append(f"{year}/{file_name}")

    # Write processed data to JSON (for reading)
    with open("processed_data_v1.json", "w", encoding="utf-8") as f:
        json.dump(csv_data_v1, f, indent=2, ensure_ascii=False)

    # Write processed data to CSV (for printing/viewing)
    if csv_data_v1:
        with open("csv_data_v1.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=csv_data_v1[0].keys())
            writer.writeheader()
            for row in csv_data_v1:
                writer.writerow(row)

    with open("not_processed_file_ids.json", "w", encoding="utf-8") as f:
        json.dump(not_processed_file_ids, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    process_wg21()
