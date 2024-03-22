import os
import logging

from sqlmodel import create_engine

logger = logging.getLogger(__name__)


if not os.environ.get("MYSQL_USER"):
    logger.info("Loading environment variables from .env file")
    from dotenv import load_dotenv

    load_dotenv()

_user = os.environ.get("MYSQL_USER")
_password = os.environ.get("MYSQL_PASSWORD")
_host = os.environ.get("MYSQL_HOST")
_database = os.environ.get("MYSQL_DB")

if any(map(lambda x: x is None, [_user, _password, _host, _database])):
    logger.error(
        "Missing environment variable MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST or MYSQL_DB"
    )
    raise Exception(
        "Missing environment variable MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST or MYSQL_DB"
    )

_mysql_url = f"mysql+mysqldb://{_user}:{_password}@{_host}:3306/{_database}"

engine = create_engine(_mysql_url)
