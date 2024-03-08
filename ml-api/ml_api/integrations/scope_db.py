"""This module contains the logic used to connect to and access data from the scope SQL database."""

import logging

import MySQLdb
from MySQLdb.constants import FIELD_TYPE

logger = logging.getLogger(__name__)


def get_document(document_id: str) -> dict:
    """Get a document from the database."""

    # Specifies what types certain fields in the database should be converted to (not currently needed)
    my_conv = { FIELD_TYPE.LONG: int }

    # Should a new connection made everytime the function is called?
    db=MySQLdb.connect(conv=my_conv, read_default_file="db_config.cnf")

    c=db.cursor()
    # Security (could any string be harmful here?)
    c.execute("""SELECT url FROM scopesql.scopeBackend_source WHERE id = %s""", (document_id,))
    
    # fetchone() returns a 1-tuple containing the url
    document_url = c.fetchone()
    if document_url is None:
        document_url = ""
    else:
        document_url = document_url[0]

    c.close()
    db.close()

    # pass document_url to text extractor

    return {
        "id": document_id,
        "url": document_url,
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
