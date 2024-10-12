import csv
import json
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dask import compute, delayed  # type: ignore
from dask.distributed import Client

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
ID_START = 1
ID_END = 10000


def get_highest_project_id():
    url = "https://www.thegef.org/projects-operations/database"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the table with project data
        table = soup.find("table", class_="table-hover")

        if table:
            # Find all rows in the table body
            rows = table.find("tbody").find_all("tr")  # type: ignore

            if rows:
                # Get the ID from the second column of the first row
                highest_id = int(rows[0].find_all("td")[1].text.strip())
                return highest_id

        logging.error("Could not find the project ID table or data.")
        return None
    except requests.RequestException as e:
        logging.error(f"Error fetching the webpage: {e}")
        return None
    except Exception as e:
        logging.error(f"Error parsing the webpage: {e}")
        return None


def check_project_id(project_id):
    url = f"https://www.thegef.org/projects-operations/projects/{project_id}"
    try:
        response = requests.head(url, allow_redirects=False)
        return project_id if response.status_code == 200 else None
    except requests.RequestException:
        return None


def save_to_json(data, filename):
    with open(filename, "w") as f:
        json.dump({"valid_project_ids": data}, f, indent=2)


def save_to_csv(data, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["project_id"])
        for project_id in data:
            writer.writerow([project_id])


def main():
    # Get the highest project ID
    highest_id = get_highest_project_id()
    if highest_id is None:
        logging.error("Could not get the highest project ID.")
        return

    logging.info(f"Highest project ID: {highest_id}")

    # Set up Dask client
    client = Client()  # This will use all available cores by default
    logging.info(f"Dask dashboard available at: {client.dashboard_link}")

    logging.info(f"Checking project IDs from {ID_START} to {highest_id}...")

    # Create delayed objects for each project ID check
    delayed_results = [
        delayed(check_project_id)(i) for i in range(ID_START, highest_id + 1)
    ]

    # Compute all results
    results = compute(*delayed_results)

    # Filter out None values (invalid project IDs)
    valid_ids = [id for id in results if id is not None]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"valid_project_ids_{timestamp}.json"
    csv_filename = f"valid_project_ids_{timestamp}.csv"

    save_to_json(valid_ids, json_filename)
    save_to_csv(valid_ids, csv_filename)

    logging.info(f"Found {len(valid_ids)} valid project IDs")
    logging.info(f"Results saved to {json_filename} and {csv_filename}")

    client.close()


if __name__ == "__main__":
    main()
