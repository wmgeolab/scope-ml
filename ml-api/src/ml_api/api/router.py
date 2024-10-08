import asyncio

from fastapi import APIRouter
from ml_api.rag_inference.rag_service import generate_rag_response

from .schemas import GEFRagRequest, GEFRagResponse

router = APIRouter()


@router.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@router.get("/healthcheck/{sleep_time}")
async def healthcheck_sleep(sleep_time: int):
    await asyncio.sleep(sleep_time)
    return {"status": "ok"}


@router.get("/generate_rag_response")
async def generate_rag_response_request(request: GEFRagRequest) -> GEFRagResponse:
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
