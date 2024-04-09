import logging

from sqlmodel import create_engine

from ..config import Config

logger = logging.getLogger(__name__)

MYSQL_URL_TEMPLATE = "mysql+mysqldb://{user}:{password}@{host}:3306/{database}"

# Make mysql url using Config.user, etc...
_mysql_url = MYSQL_URL_TEMPLATE.format(
    user=Config.MYSQL_USER,
    password=Config.MYSQL_PASSWORD,
    host=Config.MYSQL_HOST,
    database=Config.MYSQL_DB,
)

engine = create_engine(_mysql_url)
