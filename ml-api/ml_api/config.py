import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()


class Config:
    TOGETHER_LLM_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"

    # Secrets
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_DB = os.getenv("MYSQL_DB")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

    @staticmethod
    def validate():
        required_vars = [
            "TOGETHER_API_KEY",
            "MYSQL_HOST",
            "MYSQL_DB",
            "MYSQL_USER",
            "MYSQL_PASSWORD",
        ]
        missing_vars = [var for var in required_vars if getattr(Config, var) is None]

        if missing_vars:
            logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
            raise ValueError(
                f"Missing environment variables: {', '.join(missing_vars)}"
            )

        logger.info("Config validated")
