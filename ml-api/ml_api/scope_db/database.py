from sqlmodel import create_engine

import os

if not os.environ.get("MYSQL_USER"):
    print("ENV WASN'T LOADED IN DATABASE.PY")
    from dotenv import load_dotenv

    load_dotenv()

_user = os.environ.get("MYSQL_USER")
_password = os.environ.get("MYSQL_PASSWORD")
_host = os.environ.get("MYSQL_HOST")
_database = os.environ.get("MYSQL_DB")

_mysql_url = f"mysql+mysqldb://{_user}:{_password}@{_host}:3306/{_database}"

engine = create_engine(_mysql_url)
