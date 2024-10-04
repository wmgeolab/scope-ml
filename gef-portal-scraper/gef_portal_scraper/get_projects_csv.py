import csv
import json
import logging
from datetime import datetime

import requests
from dask import compute, delayed
from dask.distributed import Client

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
ID_START = 1
ID_END = 10000


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
    # Set up logging

    # Set up Dask client
    client = Client()  # This will use all available cores by default
    logging.info(f"Dask dashboard available at: {client.dashboard_link}")

    logging.info(f"Checking project IDs from {ID_START} to {ID_END}...")

    # Create delayed objects for each project ID check
    delayed_results = [
        delayed(check_project_id)(i) for i in range(ID_START, ID_END + 1)
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
