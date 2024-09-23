""" 
This service is responsible for taking a query and generating an answer using Retrieval Augmented Generation (RAG)

This includes interacting with the retrieval service to get relevant information and interacting with the
vLLM service to generate an answer. 
"""

from llama_index.core import PromptHelper
from llama_index.core.response_synthesizers import TreeSummarize
from ml_api.config import settings
from ml_api.retrieval.retrieval_service import retrieve_points_by_project_id
from ml_api.utils.llm import get_llm

from .exceptions import RAGNodesNotFoundException


async def generate_rag_response(query: str, project_id: str) -> str:
    """Generates a RAG response for a single question in a specific GEF project."""

    # Steps:
    # 1. Use the retrieval service to get relevant information
    # 2. Use the vLLM service to generate an answer
    # 3. Return the answer

    llm = get_llm()

    nodes = retrieve_points_by_project_id(query, project_id)

    if not nodes:
        raise RAGNodesNotFoundException(f"No nodes found for project id {project_id}")

    prompt_helper = PromptHelper(
        context_window=settings.LLM_CONTEXT_WINDOW, num_output=settings.LLM_NUM_OUTPUT
    )

    summarize = TreeSummarize(
        llm=llm, prompt_helper=prompt_helper, verbose=True
    )  # Can also pass a pydantic object to this

    response = await summarize.asynthesize(query=query, nodes=nodes)

    return response
