"""
This file is for interacting with models to answer questions about documents.
"""

import logging

from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.program import LLMTextCompletionProgram

from ..models.qa import QuestionAnsweringResponse
from ..prompts import QA_TEMPLATE
from ..scope_db.crud import get_sourcing_source
from ..utils import get_llm

logger = logging.getLogger(__name__)


llm = get_llm()


def answer_question(text: str, question: str) -> QuestionAnsweringResponse:
    """Answer a question using some text."""
    program = LLMTextCompletionProgram.from_defaults(
        llm=llm,
        output_parser=PydanticOutputParser(output_cls=QuestionAnsweringResponse),
        prompt=QA_TEMPLATE,
        verbose=True,
    )

    output = program(document_text=text, question=question)

    valid_response = QuestionAnsweringResponse.parse_obj(output)

    return valid_response


def doc_answer_question(document_id: int, question: str) -> QuestionAnsweringResponse:
    """Answer a question about a document."""
    source = get_sourcing_source(document_id)

    return answer_question(source.source_text, question)
