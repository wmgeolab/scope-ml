"""Put background task functions here"""

import asyncio
import logging
import aiohttp

from ml_api.config import settings
from ml_api.ingestion import BaseIngestionService
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
            # "source_id": int(source),
            "source": int(source),
            "workspace": int(workspace),
            "summary": response,
        }

        headers = {
            "Authorization": f"Token {settings.SCOPE_BACKEND_AUTH_TOKEN}",
            "Content-Type": "application/json",
        }

        logger.info(f"Posting response to external API: {payload}")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.SCOPE_BACKEND_URL}/api/ai_responses/",
                json=payload,
                headers=headers,
            ) as resp:

                response_text = await resp.text()
                try:
                    response_json = await resp.json()
                    logger.info(f"Response JSON: {response_json}")
                    logger.info(f"Response text: {response_text}")
                except:
                    logger.info(f"Response text: {response_text}")

                if resp.status == 200:
                    logger.info("Successfully posted response to external API.")
                else:
                    logger.error(
                        f"Failed to post response to external API. Status: {resp.status}"
                    )

    except Exception as e:
        logger.error(f"Error posting to external API: {e}", stack_info=True)


def ingest_projects_background(project_ids: list[str], service: BaseIngestionService):
    """Ingests data into the system in the background."""

    project_base_dir = settings.DATA_BASE_DIR
    project_dirs = [project_base_dir / project_id for project_id in project_ids]

    for project_dir in project_dirs:
        service.ingest_directory(project_dir)

    logger.info("Ingestion task completed. Projects ingested: %s", project_ids)
