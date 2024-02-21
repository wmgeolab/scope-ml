"""
This file is for interacting with models to answer questions about documents.
"""

import logging

from .integrations.scope_db import get_document

logger = logging.getLogger(__name__)


def answer_question(document_id: str, question: str) -> str:
    """Answer a question about a document."""
    document = get_document(document_id)
    return (
        f"Answering the question '{question}' about the document with id {document_id}."
    )
