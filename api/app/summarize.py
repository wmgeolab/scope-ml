"""
This file is for interacting with models to compute document summaries.
"""

from .scope_db import get_document


def summarize_document(document_id: str) -> str:
    """Summarize a document."""
    document = get_document(document_id)
    summary = document["text"][:100]
    return summary
