"""
This file is for interacting with models to answer questions about documents.
"""

import logging
from llama_index.llms.together import TogetherLLM
from ..scope_db.crud import get_document

logger = logging.getLogger(__name__)


llm = TogetherLLM(model="mistralai/Mixtral-8x7B-Instruct-v0.1")


def answer_question(document_id: int, question: str) -> str:
    """Answer a question about a document."""
    document = get_document(document_id)

    return (
        f"Answering the question '{question}' about the document with id {document_id}."
    )


def extract_locations(document_id: str):
    pass


def extract_actors(document_id: str):
    pass
