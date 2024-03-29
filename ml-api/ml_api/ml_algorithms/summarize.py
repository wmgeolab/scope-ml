"""
This file is for interacting with models to compute document summaries.
"""

import logging
import os

from dotenv import load_dotenv
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.llms.together import TogetherLLM

from ..models.qa import SummarizeDocumentResponse
from ..prompts import SUMMARY_TEMPLATE
from ..scope_db.crud import get_document

load_dotenv()

logger = logging.getLogger(__name__)


llm = TogetherLLM(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    api_key=os.environ.get("TOGETHER_API_KEY"),
)


def doc_generate_summary(document_id: int) -> SummarizeDocumentResponse:
    """Summarize a document."""
    document = get_document(document_id)

    program = LLMTextCompletionProgram.from_defaults(
        llm=llm,
        output_parser=PydanticOutputParser(output_cls=SummarizeDocumentResponse),
        prompt=SUMMARY_TEMPLATE,
        verbose=True,
    )

    output = program(document_text=document.text)

    valid_response = SummarizeDocumentResponse.parse_obj(output)

    return valid_response
