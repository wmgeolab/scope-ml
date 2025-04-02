"""Put background task functions here"""

import asyncio
import logging
import aiohttp

from ml_api.config import settings
from ml_api.ingestion.ingestion_service import IngestionService
from ml_api.rag_inference.rag_service import generate_rag_response

logger = logging.getLogger(__name__)


async def generate_rag_response_and_post(
    question: str, project_id: str, source: str, workspace: str
):
    """Generates a RAG response and posts it to an external API."""

    try:
        response = await generate_rag_response(question, project_id)

        logger.info(f"RAG response generated: {response}")

    except Exception as e:
        logger.error(f"Error generating RAG response: {e}", stack_info=True)
        return

    try:
        payload = {
            "source": source,
            "workspace": workspace,
            "summary": response,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.SCOPE_BACKEND_URL}/api/ai_responses/", json=payload
            ) as resp:
                if resp.status == 200:
                    logger.info("Successfully posted response to external API.")
                else:
                    logger.error(
                        f"Failed to post response to external API. Status: {resp.status}"
                    )

    except Exception as e:
        logger.error(f"Error posting to external API: {e}", stack_info=True)


def ingest_projects_background(project_ids: list[str], service: IngestionService):
    """Ingests data into the system in the background."""

    project_base_dir = service.data_base_dir
    project_dirs = [project_base_dir / project_id for project_id in project_ids]

    for project_dir in project_dirs:
        service.ingest_directory(project_dir)

    logger.info("Ingestion task completed. Projects ingested: %s", project_ids)
