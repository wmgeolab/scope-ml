import asyncio
import logging
import os
from datetime import datetime

import aiohttp
import backoff

# import ujson as json
import json
from aiolimiter import AsyncLimiter
from bs4 import BeautifulSoup
from pydantic_settings import BaseSettings
from tqdm.asyncio import tqdm


class Settings(BaseSettings):
    BASE_URL: str = "https://www.thegef.org/projects-operations/projects/{project_id}"
    DATABASE_URL: str = "https://www.thegef.org/projects-operations/database"
    OUTPUT_DIR: str = "/app/data/"
    JSON_FILENAME: str = "project_ids.json"
    ID_START: int = 1
    RATE_LIMIT: int = 125
    BATCH_SIZE: int = 999999
    RESPONSE_CODES_LOGGED: list[int] = [429]
    USE_RATE_LIMITER: bool = True
    USE_TQDM: bool = True
    USE_FILE_TIMESTAMPS: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Settings()

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set up rate limiter
rate_limiter = AsyncLimiter(config.RATE_LIMIT, 1)


async def get_highest_project_id(session) -> int | None:
    """Gets the highest project ID from the GEF website."""
    async with session.get(config.DATABASE_URL) as response:
        html = await response.text()
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", class_="table-hover")
        if table and (rows := table.find("tbody").find_all("tr")):  # type: ignore
            return int(rows[0].find_all("td")[1].text.strip())
    logging.error("Could not find the project ID table or data.")
    return None


@backoff.on_predicate(backoff.expo, lambda x: x == -429, max_time=60)
async def check_project_id(session, project_id) -> int | None:
    """Check if a project ID exists in the GEF database."""
    url = config.BASE_URL.format(project_id=project_id)

    async def make_request():
        async with session.head(url, allow_redirects=False) as response:
            if response.status in config.RESPONSE_CODES_LOGGED:
                logging.error(
                    f"Failed to access website: {url}. Status code: {response.status}"
                )
                return -response.status
            return project_id if response.status == 200 else None

    try:
        if config.USE_RATE_LIMITER:
            async with rate_limiter:
                return await make_request()
        else:
            return await make_request()
    except aiohttp.ClientError as e:
        logging.error(f"Failed to access website: {url}")
        raise e
    except Exception as e:
        logging.error(f"Failed to access website: {url}. Exception type: {type(e)}")
        raise e


async def check_project_ids(session, start_id: int, end_id: int) -> list[int]:
    """Check all project IDs in a given range."""
    logging.info(f"Checking project IDs from {start_id} to {end_id}")
    tasks = [check_project_id(session, id) for id in range(start_id, end_id + 1)]

    if config.USE_TQDM:
        results = await tqdm.gather(
            *tasks, desc=f"Checking Project IDs: {start_id}-{end_id}", total=len(tasks)
        )
    else:
        results = await asyncio.gather(*tasks)

    valid_ids = [id for id in results if id is not None]
    logging.info(f"Found {len(valid_ids)} valid IDs in range {start_id}-{end_id}")
    return valid_ids


def save_to_json(data: list[int], filename: str = config.JSON_FILENAME):
    """Save the valid project IDs to a JSON file."""
    if config.USE_FILE_TIMESTAMPS:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filename.replace(".json", f"_{timestamp}.json")

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(config.OUTPUT_DIR, filename), "w") as f:
        json.dump({"valid_project_ids": data}, f, indent=2)

    logging.info(f"Saved {len(data)} project IDs to JSON file: {filename}")


async def main():
    async with aiohttp.ClientSession() as session:
        highest_id = await get_highest_project_id(session)
        if highest_id is None:
            logging.error("Could not get the highest project ID. Exiting.")
            return

        logging.info(f"Highest project ID: {highest_id}")
        all_valid_ids = []

        batches = [
            (start_id, min(start_id + config.BATCH_SIZE - 1, highest_id))
            for start_id in range(config.ID_START, highest_id + 1, config.BATCH_SIZE)
        ]

        for start_id, end_id in batches:
            valid_ids = await check_project_ids(session, start_id, end_id)
            all_valid_ids.extend(valid_ids)

        logging.info(
            f"Found {len(all_valid_ids)} valid IDs in range {config.ID_START}-{highest_id}"
        )
        save_to_json(all_valid_ids)


if __name__ == "__main__":
    asyncio.run(main())
