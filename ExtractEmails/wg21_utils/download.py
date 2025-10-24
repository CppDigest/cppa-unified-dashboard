import requests
import os


def download(url: str, output_folder: str) -> bool:
    file_name = url.split("/")[-1]
    file_path = os.path.join(output_folder, file_name)

    if os.path.exists(file_path):
        return False

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False
