import asyncio
import logging

from fastapi import APIRouter, BackgroundTasks
from ml_api.api.tasks import generate_rag_response_and_post
from ml_api.rag_inference.rag_service import generate_rag_response

from .schemas import GEFRagRequest, GEFRagRequestBatch, GEFRagResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@router.get("/healthcheck/{sleep_time}")
async def healthcheck_sleep(sleep_time: int):
    await asyncio.sleep(sleep_time)
    return {"status": "ok"}


@router.post("/generate_rag_response_batch")
async def generate_rag_response_request(request: GEFRagRequestBatch) -> GEFRagResponse:
    """Generates a RAG response for a single question in a specific GEF project."""

    # TODO: This will most likely timeout an HTTP request.

    questions = request.questions
    project_id = request.project_id

    responses = await asyncio.gather(
        *[generate_rag_response(question, project_id) for question in questions]
    )

    response_dict = {
        question: response for question, response in zip(questions, responses)
    }

    return GEFRagResponse(answers=response_dict)


@router.post("/generate_rag_response")
async def generate_rag_response_single(
    request: GEFRagRequest,
    background_tasks: BackgroundTasks,
):
    """Generates a RAG response for a single question and posts it to an external API in the background."""

    background_tasks.add_task(
        generate_rag_response_and_post,
        request.question,
        "9467",
        request.source,
        request.workspace,
    )

    return {
        "message": "RAG response generation and posting to external API initiated in the background."
    }
