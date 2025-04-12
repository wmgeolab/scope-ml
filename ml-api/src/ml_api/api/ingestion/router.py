from fastapi import APIRouter, BackgroundTasks
from ml_api.api.schemas import IngestionRequest
from ml_api.api.tasks import ingest_projects_background
from ml_api.ingestion import NaiveIngestionService, VLMIngestionService

router = APIRouter(prefix="/ingestion")


@router.post("/projects")
async def ingest_data(request: IngestionRequest, background_tasks: BackgroundTasks):
    """Ingests data into the system."""

    service = NaiveIngestionService()

    background_tasks.add_task(
        ingest_projects_background,
        request.project_ids,
        service,
    )

    return {
        "message": f"Ingestion service initialized and running in the background. Project IDs: {request.project_ids}"
    }


@router.post("/projects/vlm")
async def ingest_data_vlm(request: IngestionRequest, background_tasks: BackgroundTasks):
    """Ingests data into the system."""

    service = VLMIngestionService()

    background_tasks.add_task(
        ingest_projects_background,
        request.project_ids,
        service,
    )

    return {
        "message": f"Ingestion service initialized and running in the background. Project IDs: {request.project_ids}"
    }
