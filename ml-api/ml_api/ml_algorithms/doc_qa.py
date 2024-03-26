"""
This file is for interacting with models to answer questions about documents.
"""

import logging
from llama_index.llms.together import TogetherLLM
from ..scope_db.crud import get_document, get_sourcing_source

from ..models.extraction import ExtractedActors, ExtractedLocations
from ..prompts import EXTRACT_ACTORS_TEMPLATE, EXTRACT_LOCATIONS_TEMPLATE

logger = logging.getLogger(__name__)


llm = TogetherLLM(model="mistralai/Mixtral-8x7B-Instruct-v0.1")


def answer_question(document_id: int, question: str) -> str:
    """Answer a question about a document."""
    # document = get_document(document_id)
    source = get_sourcing_source(document_id)

    return (
        f"Answering the question '{question}' about the document with id {document_id}."
    )


def extract_locations(document_id: int) -> ExtractedLocations:

    # document = get_document(document_id)
    source = get_sourcing_source(document_id)

    response = llm.structured_predict(
        ExtractedLocations, EXTRACT_LOCATIONS_TEMPLATE, document_text=source.source_text  # type: ignore this is because the library is using pydantic v1
    )

    valid_response = ExtractedLocations.model_validate(response)

    return valid_response


def extract_actors(document_id: int):
    pass
