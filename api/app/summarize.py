"""
This file is for interacting with models to compute document summaries.
"""

import logging

from .integrations.scope_db import get_document

logger = logging.getLogger(__name__)


def summarize_document(document_id: str) -> str:
    """Summarize a document."""
    document = get_document(document_id)
    summary = document["text"][:100]
    return summary
