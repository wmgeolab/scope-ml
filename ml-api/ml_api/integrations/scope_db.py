"""This module contains the logic used to connect to and access data from the scope SQL database."""

import logging

from MySQLdb import _mysql
from MySQLdb.constants import FIELD_TYPE

logger = logging.getLogger(__name__)

my_conv = { FIELD_TYPE.LONG: int }


def get_document(document_id: str) -> dict:
    """Get a document from the database."""
    # Should a new connection made everytime the function is called?
    # Proper path to config file?
    db=_mysql.connect(conv=my_conv, read_default_file="db_config.cnf")
    # TODO logic for getting url from id
    db.query("""SELECT * FROM scopesql.scopeBackend_source""")
    r = db.store_result()

    data = r.fetch_row(maxrows=1)
    return {
        "id": document_id,
        "data": data,
        "text": "This is the text of the document.",
    }


def _get_sample_document(document_id: str = "sample_id") -> dict:
    sample_file = open("app/integrations/sample_doc.txt", "r")
    sample_text = sample_file.read()
    sample_file.close()

    return {
        "id": document_id,
        "text": sample_text,
    }


print(get_document("id")["data"])