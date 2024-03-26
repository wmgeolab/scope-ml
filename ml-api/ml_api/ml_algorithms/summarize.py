"""
This file is for interacting with models to compute document summaries.
"""

import logging
import os

from dotenv import load_dotenv
from llama_index.llms.together import TogetherLLM

from ..prompts import SUMMARY_TEMPLATE
from ..scope_db.crud import get_document

load_dotenv()

logger = logging.getLogger(__name__)


llm = TogetherLLM(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    api_key=os.environ.get("TOGETHER_API_KEY"),
)


def summarize_document(document_id: int) -> str:
    """Summarize a document."""
    document = get_document(document_id)
    messages = SUMMARY_TEMPLATE.format_messages(document_text=document.text)
    logger.info(messages)

    output = llm.chat(messages, max_tokens=2048)

    return str(output)
