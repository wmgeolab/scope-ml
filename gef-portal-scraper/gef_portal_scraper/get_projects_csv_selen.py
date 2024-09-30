import os
import logging
import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
BASE_URL = "https://www.thegef.org"
EXPORT_URL = f"{BASE_URL}/projects-operations/database/export?page&_format=csv"
CSV_PATH = os.getenv("PROJECTS_CSV_PATH", "/app/data/projects.csv")
DEBUG_DIR = "/app/data/debug"


def random_delay(min_seconds=2, max_seconds=5):
    time.sleep(random.uniform(min_seconds, max_seconds))


def save_debug_info(driver, step):
    os.makedirs(DEBUG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save screenshot
    screenshot_path = os.path.join(DEBUG_DIR, f"{step}_{timestamp}.png")
    driver.save_screenshot(screenshot_path)
    logging.info(f"Screenshot saved: {screenshot_path}")

    # Save page source
    source_path = os.path.join(DEBUG_DIR, f"{step}_{timestamp}.html")
    with open(source_path, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    logging.info(f"Page source saved: {source_path}")


def fetch_csv():
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Firefox()

    try:
        # Step 1: Visit the main page
        logging.info("Visiting the main page...")
        driver.get(BASE_URL)
        save_debug_info(driver, "main_page")
        random_delay()

        # Step 2: Initiate the export
        logging.info("Initiating the export...")
        driver.get(EXPORT_URL)
        save_debug_info(driver, "export_page")

        random_delay(5, 10)
        save_debug_info(driver, "export_page_2")

        current_url = driver.current_url
        logging.info(f"Export URL: {current_url}")

        random_delay(5, 10)

        # Step 3: Wait for the export to complete
        logging.info("Waiting for export to complete...")
        start_time = time.time()
        while True:
            try:
                progress = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "progress__description")
                    )
                )
                # percent = progress.get_attribute("style").split("%")[0]
                percent = progress.text.split("%")[0]
                logging.info(f"Export progress: {percent}%")
                save_debug_info(driver, f"progress_{percent}")
            except:
                logging.info("Progress bar not found, checking for download link...")
                save_debug_info(driver, "progress_not_found")

            if "Download the file" in driver.page_source:
                logging.info("Export completed.")
                save_debug_info(driver, "export_complete")
                break

            if time.time() - start_time > 600:  # 10 minutes timeout
                raise TimeoutError("Export process timed out after 10 minutes")

            random_delay(10, 15)
            driver.refresh()

        # Step 4: Find and click the download link
        download_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "here"))
        )
        download_url = download_link.get_attribute("href")
        logging.info(f"Download URL found: {download_url}")
        save_debug_info(driver, "download_page")

        # Step 5: Download the file
        driver.get(download_url)

        # Wait for download to complete (this part might need adjustment based on your setup)
        download_wait = 0
        while (
            not os.path.exists("/home/seluser/Downloads/projects.csv")
            and download_wait < 60
        ):
            time.sleep(1)
            download_wait += 1

        if os.path.exists("/home/seluser/Downloads/projects.csv"):
            os.rename("/home/seluser/Downloads/projects.csv", CSV_PATH)
            logging.info(f"CSV file successfully downloaded and saved to {CSV_PATH}")
        else:
            raise Exception("CSV file not found after download attempt")

        # Update last fetched timestamp
        with open("/app/data/last_csv_update.txt", "w") as f:
            f.write(datetime.now().isoformat())

    except Exception as e:
        logging.error(f"Error fetching CSV: {e}")
        save_debug_info(driver, "error")
    finally:
        driver.quit()


if __name__ == "__main__":
    fetch_csv()
