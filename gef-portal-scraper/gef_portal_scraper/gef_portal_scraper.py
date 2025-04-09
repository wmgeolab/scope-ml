import csv
import json
import logging
import os
import sys
import glob
from urllib.parse import unquote, urlparse
import document_db_manager

import requests
from bs4 import BeautifulSoup
from dask.base import compute
from dask.delayed import delayed

# Constants
PROJECTS_CSV_PATH = os.getenv("PROJECTS_CSV_PATH", "/app/data/projects.csv")
PROJECTS_JSON_PATTERN = os.getenv("PROJECTS_JSON_PATTERN", "/app/data/project_ids*.json")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "/app/data/output")

BASE_URL = os.getenv("BASE_URL", "https://www.thegef.org/projects-operations/projects/")

VALID_EXTENSIONS = [".pdf", ".doc", ".docx", ".txt"]
# INTERESTED_YEARS = [i for i in range(2012, 2024)]
INTERESTED_YEARS = None


# Set up logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    #logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO) # Uncomment to enable detailed sql logs

def get_project_ids_from_csv(path, interested_years=None) -> list[str]:
    project_ids = []
    try:
        with open(path, "r") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip the header row
            for row in reader:
                try:
                    year = int(row[9])
                    if interested_years and year not in interested_years:
                        continue
                    project_id = row[1]
                    project_ids.append(project_id)
                except ValueError:
                    logging.warning(f"Invalid year value: {row[9]}")
    except FileNotFoundError:
        logging.error(f"CSV file not found at path: {path}")
    return project_ids

def get_project_ids_from_json(pattern) -> list[str]:
    # Because the json file may have a timestamp we use a pattern to try and find the correct file
    try:
        path = glob.glob(pattern)[0]
    except IndexError:
        logging.error(f"No JSON file found that matches the pattern: {pattern}")
    
    project_ids = []
    try:
        with open(path, "r") as file:
            data = json.load(file)
            project_ids = data['valid_project_ids']
    except FileNotFoundError:
        logging.error(f"JSON file not found at path: {path}")
    return project_ids


def create_directory(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
    os.chmod(path, 0o777)  # Ensure the directory is writable


def download_file(href, project_id, idx):
    try:
        parsed_url = urlparse(href)
        if parsed_url.scheme == "" or parsed_url.netloc == "":
            logging.warning(f"Skipping invalid URL: {href}")
            return None

        original_filename = os.path.basename(unquote(parsed_url.path))
        file_response = requests.get(href)
        file_response.raise_for_status()  # Raise an error for bad status codes

        project_dir = os.path.join(OUTPUT_PATH, str(project_id))
        create_directory(project_dir)

        file_path = os.path.join(
            project_dir, f"p{project_id}_doc{idx}__{original_filename}"
        )
        with open(file_path, "wb") as file:
            file.write(file_response.content)
        os.chmod(file_path, 0o666)  # Ensure the file is writable
        logging.info(f"Downloaded file: {file_path}")
        # store document info in db
        filename, extension = os.path.splitext(href)
        document_db_manager.add_document(original_filename, href, extension, project_id)
        return file_path
    except requests.RequestException as e:
        logging.error(f"Failed to download file from: {href}. Error: {e}")
        return None


def download_files_from_project_page(project_id):
    url = BASE_URL + str(project_id)
    response = requests.get(url)
    if response.status_code != 200:
        logging.warning(f"Failed to access website: {url}")
        return [], []

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")

    downloaded_files = []
    skipped_extensions = set()
    idx = 0

    for link in links:
        href = link.get("href")
        if href:
            file_extension = os.path.splitext(href)[1]
            if file_extension in VALID_EXTENSIONS:
                # An updated version of a document would be skipped if it uses the same url as the old version
                # Should not be a problem as the gef does not seem to update documents in this way
                if document_db_manager.document_exists(href):
                    logging.info(f"Document already in database, skipping: {href}")
                    continue
                downloaded_file = download_file(href, project_id, idx)
                if downloaded_file:
                    downloaded_files.append(downloaded_file)
                    idx += 1
            else:
                skipped_extensions.add(file_extension)

    if skipped_extensions:
        logging.warning(f"Skipped extensions: {skipped_extensions}")

    return downloaded_files, skipped_extensions


def download_project_ids(project_ids: list[str]):
    tasks = [delayed(download_files_from_project_page)(pid) for pid in project_ids]
    _ = compute(*tasks)


def main():
    setup_logging()

    document_db_manager.create_db_and_tables()

    create_directory(OUTPUT_PATH)

    # project_ids = get_project_ids_from_csv(PROJECTS_CSV_PATH, INTERESTED_YEARS)
    # project_ids = gef6_project_ids

    project_ids = get_project_ids_from_json(PROJECTS_JSON_PATTERN)

    # project_ids = get_ids_from_json("gef_7_project_ids")
    
    logging.info(f"Collected {len(project_ids)} project IDs from json file")

    download_project_ids(project_ids)


if __name__ == "__main__":
    main()
