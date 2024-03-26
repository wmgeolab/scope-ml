"""
This file is for interacting with models to answer questions about documents.
"""

import logging
from llama_index.llms.together import TogetherLLM
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.output_parsers import PydanticOutputParser
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
    source = get_sourcing_source(document_id)

    program = LLMTextCompletionProgram.from_defaults(
        llm=llm,
        output_parser=PydanticOutputParser(output_cls=ExtractedLocations),
        prompt=EXTRACT_LOCATIONS_TEMPLATE,
        verbose=True,
    )

    output = program(document_text=source.source_text)

    valid_response = ExtractedLocations.parse_obj(output)

    return valid_response


def extract_actors(document_id: int):
    source = get_sourcing_source(document_id)

    program = LLMTextCompletionProgram.from_defaults(
        llm=llm,
        output_parser=PydanticOutputParser(output_cls=ExtractedActors),
        prompt=EXTRACT_ACTORS_TEMPLATE,
        verbose=True,
    )

    output = program(document_text=source.source_text)

    valid_response = ExtractedActors.parse_obj(output)

    return valid_response
