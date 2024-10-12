import asyncio
import logging
from datetime import datetime

import aiohttp
import backoff
import ujson as json
from aiolimiter import AsyncLimiter
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Switches
USE_RATE_LIMITER = True
USE_TQDM = True
USE_FILE_TIMESTAMPS = True


# Constants
BASE_URL = "https://www.thegef.org/projects-operations/projects/{project_id}"
OUTPUT_DIR = "../data/"
JSON_FILENAME = "project_ids.json"
ID_START = 1
RATE_LIMIT = 125
BATCH_SIZE = 99999
RESPONSE_CODES_LOGGED = [429]

# Set up limiter
rate_limiter = AsyncLimiter(RATE_LIMIT, 1)  # 25 requests per second


async def get_highest_project_id():
    """
    Gets the highest project ID from the GEF website.

    Returns:
        int: the highest project ID, or None if the table or data could not be found.
    """
    url = "https://www.thegef.org/projects-operations/database"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            table = soup.find("table", class_="table-hover")
            if table:
                rows = table.find("tbody").find_all("tr")  # type: ignore
                if rows:
                    return int(rows[0].find_all("td")[1].text.strip())

    logging.error("Could not find the project ID table or data.")
    return None


@backoff.on_predicate(backoff.expo, lambda value: value == -429, max_time=60)
async def check_project_id(session, project_id):
    """
    Check if a project ID exists in the GEF database.
    Args:
    session (aiohttp.ClientSession): The aiohttp client session to use for the request.
    project_id (int): The project ID to check.
    Returns:
    int: The project ID if it exists, otherwise None.
    """

    url = BASE_URL.format(project_id=project_id)

    async def make_request():
        async with session.head(url, allow_redirects=False) as response:
            global total_retry_after
            if response.status in RESPONSE_CODES_LOGGED:
                logging.error(
                    f"Failed to access website: {url}. Status code: {response.status}"
                )

                return int(response.status) * -1  # trigger backoff w/ status

            return project_id if response.status == 200 else None

    try:
        if USE_RATE_LIMITER:
            async with rate_limiter:
                return await make_request()
        else:
            return await make_request()

    except aiohttp.ClientError as e:
        logging.error(f"Failed to access website: {url}")
        raise e  # Re-raise the exception to trigger backoff
    except Exception as e:
        # Log status code and exception type
        logging.error(f"Failed to access website: {url}. Exception type: {type(e)}")
        raise e
    return None


async def check_project_ids(start_id, end_id):
    """
    Check all project IDs in a given range.

    Args:
        start_id (int): The lowest project ID to check.
        end_id (int): The highest project ID to check (inclusive).

    Returns:
        list[int]: A list of valid project IDs in the given range.
    """

    logging.info(f"Checking project IDs from {start_id} to {end_id}")
    async with aiohttp.ClientSession() as session:
        tasks = [check_project_id(session, id) for id in range(start_id, end_id + 1)]

        if USE_TQDM:
            results = await tqdm.gather(
                *tasks,
                desc=f"Checking Project IDs: {start_id}-{end_id}",
                total=len(tasks),
            )
        else:
            results = await asyncio.gather(*tasks)

        valid_ids = [id for id in results if id is not None]
        logging.info(f"Found {len(valid_ids)} valid IDs in range {start_id}-{end_id}")
        return valid_ids


def save_to_json(data, filename=JSON_FILENAME):
    if USE_FILE_TIMESTAMPS:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filename.replace(".json", f"_{timestamp}.json")

    with open(OUTPUT_DIR + filename, "w") as f:
        json.dump({"valid_project_ids": data}, f, indent=2)

    logging.info(f"Saved {len(data)} project IDs to JSON file: {filename}")


async def main():
    highest_id = await get_highest_project_id()

    if highest_id is None:
        logging.error("Could not get the highest project ID. Exiting.")
        return

    logging.info(f"Highest project ID: {highest_id}")

    all_valid_ids: list[int] = []

    # Batched check
    batches = [
        (start_id, min(start_id + BATCH_SIZE - 1, highest_id))
        for start_id in range(ID_START, highest_id + 1, BATCH_SIZE)
    ]

    for start_id, end_id in batches:
        valid_ids = await check_project_ids(start_id, end_id)
        all_valid_ids.extend(valid_ids)

    logging.info(
        f"Found {len(all_valid_ids)} valid IDs in range {ID_START}-{highest_id}"
    )

    save_to_json(all_valid_ids)


if __name__ == "__main__":
    asyncio.run(main())
