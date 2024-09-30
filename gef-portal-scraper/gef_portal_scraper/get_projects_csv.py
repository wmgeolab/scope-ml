# start export url: https://www.thegef.org/projects-operations/database/export?page&_format=csv

# redirect url (takes ~ 1.5 mins): https://www.thegef.org/batch?id=4237833&op=start

# final download url: https://www.thegef.org/sites/default/files/views_data_export/projects_data_export_1/1727704227/projects.csv

# 4238530

import os
import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Constants
EXPORT_URL = (
    "https://www.thegef.org/projects-operations/database/export?page&_format=csv"
)
CSV_PATH = os.getenv("CSV_PATH", "/app/data/projects.csv")

# User Agents

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
]


def fetch_csv():
    with requests.Session() as session:
        try:
            session.headers.update({"User-Agent": USER_AGENTS[0]})
            response = session.get(EXPORT_URL)
            response.raise_for_status()

            batch_url = response.url
            logging.info(f"Waiting for export to complete at: {batch_url}")

        except requests.RequestException as e:
            logging.error(f"Error fetching CSV: {e}")

        except Exception as e:
            logging.error(f"Unexpected Error: {e}")

        return batch_url


if __name__ == "__main__":
    batch_url = fetch_csv()
