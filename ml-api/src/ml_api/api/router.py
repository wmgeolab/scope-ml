import asyncio
import logging

from fastapi import APIRouter, BackgroundTasks
from ml_api.ingestion.ingestion_service import IngestionService
from ml_api.rag_inference.rag_service import generate_rag_response

from .schemas import GEFRagRequest, GEFRagResponse, IngestionRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@router.get("/healthcheck/{sleep_time}")
async def healthcheck_sleep(sleep_time: int):
    await asyncio.sleep(sleep_time)
    return {"status": "ok"}


@router.post("/generate_rag_response")
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


def ingest_projects_background(project_ids: list[str], service: IngestionService):
    """Ingests data into the system in the background."""

    project_base_dir = service.data_base_dir
    project_dirs = [project_base_dir / project_id for project_id in project_ids]

    for project_dir in project_dirs:
        service.ingest_directory(project_dir)

    logger.info("Ingestion task completed. Projects ingested: %s", project_ids)


@router.post("/ingestion/projects")
async def ingest_data(request: IngestionRequest, background_tasks: BackgroundTasks):
    """Ingests data into the system."""

    service = IngestionService()

    background_tasks.add_task(
        ingest_projects_background,
        request.project_ids,
        service,
    )

    return {
        "message": f"Ingestion service initialized and running in the background. Project IDs: {request.project_ids}"
    }
