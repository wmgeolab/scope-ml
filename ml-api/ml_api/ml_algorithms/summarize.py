"""
This file is for interacting with models to compute document summaries.
"""

import logging

from dotenv import load_dotenv
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.program import LLMTextCompletionProgram

from ..models.qa import SummarizeDocumentResponse
from ..prompts import SUMMARY_TEMPLATE
from ..scope_db.crud import get_sourcing_source
from ..utils import get_llm

load_dotenv()

logger = logging.getLogger(__name__)


llm = get_llm()


def generate_summary(text: str) -> SummarizeDocumentResponse:
    program = LLMTextCompletionProgram.from_defaults(
        llm=llm,
        output_parser=PydanticOutputParser(output_cls=SummarizeDocumentResponse),
        prompt=SUMMARY_TEMPLATE,
        verbose=True,
    )

    output = program(document_text=text)

    valid_response = SummarizeDocumentResponse.parse_obj(output)

    return valid_response


def doc_generate_summary(document_id: int) -> SummarizeDocumentResponse:
    """Summarize a document."""
    document = get_sourcing_source(document_id)

    return generate_summary(document.source_text)
