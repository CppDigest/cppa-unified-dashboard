import os
from urllib.parse import urljoin
from dotenv import load_dotenv

from wg21_utils.first_process import (
    parse_1989_html,
    parse_1990_1991_html,
    parse_1992_1999_html,
    parse_2000_2001_html,
    parse_2002_2012_html,
    parse_2013_2025_html,
)

from wg21_utils.download import download
from wg21_utils.data import process_wg21

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
if not BASE_URL:
    raise ValueError("BASE_URL is not set")


def download_paper(result, output_folder: str):
    cnt = 0
    for url in result["urls"]:
        if download(urljoin(BASE_URL, url), output_folder):
            cnt += 1
    return cnt


def download_wg21():
    wg21_folder = "wg21"
    years_data = {
        1989: parse_1989_html,
        1990: parse_1990_1991_html,
        1991: parse_1990_1991_html,
    }

    for year in range(1992, 2000):
        years_data[year] = parse_1992_1999_html

    for year in range(2000, 2002):
        years_data[year] = parse_2000_2001_html
    for year in range(2002, 2013):
        years_data[year] = parse_2002_2012_html
    for year in range(2013, 2026):
        years_data[year] = parse_2013_2025_html

    for year in range(2022, 2026):
        html_file = f"{wg21_folder}/{year}.html"
        cnt = 0
        if os.path.exists(html_file):
            parse_func = years_data[year]
            results = parse_func(year, html_file)
            for result in results:
                cnt += download_paper(result, f"output/{year}")
        print(f"Downloaded {cnt} papers for {year}")

    pass


if __name__ == "__main__":
    download_wg21()
    process_wg21()
