import logging

from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.program import LLMTextCompletionProgram

from ..models.extraction import ExtractedActors, ExtractedLocations
from ..prompts import EXTRACT_ACTORS_TEMPLATE, EXTRACT_LOCATIONS_TEMPLATE
from ..scope_db.crud import get_sourcing_source
from ..utils import get_llm

logger = logging.getLogger(__name__)

llm = get_llm()


def extract_actors(text: str) -> ExtractedActors:
    program = LLMTextCompletionProgram.from_defaults(
        llm=llm,
        output_parser=PydanticOutputParser(output_cls=ExtractedActors),
        prompt=EXTRACT_ACTORS_TEMPLATE,
        verbose=True,
    )

    output = program(document_text=text)

    valid_response = ExtractedActors.parse_obj(output)

    return valid_response


def extract_locations(text: str) -> ExtractedLocations:
    program = LLMTextCompletionProgram.from_defaults(
        llm=llm,
        output_parser=PydanticOutputParser(output_cls=ExtractedLocations),
        prompt=EXTRACT_LOCATIONS_TEMPLATE,
        verbose=True,
    )

    output = program(document_text=text)

    valid_response = ExtractedLocations.parse_obj(output)

    return valid_response


def doc_extract_locations(document_id: int) -> ExtractedLocations:
    source = get_sourcing_source(document_id)

    return extract_locations(source.source_text)


def doc_extract_actors(document_id: int):
    source = get_sourcing_source(document_id)

    return extract_actors(source.source_text)
