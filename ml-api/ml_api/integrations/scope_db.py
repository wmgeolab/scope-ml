"""This module contains the logic used to connect to and access data from the scope SQL database."""

import logging

logger = logging.getLogger(__name__)


def get_document(document_id: str) -> dict:
    """Get a document from the database."""
    return {
        "id": document_id,
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
