"""Put background task functions here"""

import asyncio
import logging
import aiohttp

from ml_api.rag_inference.rag_service import generate_rag_response

logger = logging.getLogger(__name__)


async def generate_rag_response_and_post(
    question: str, project_id: str, source_id: str, workspace_id: str, external_api_url: str
):
    """Generates a RAG response and posts it to an external API."""

    try:
        response = await generate_rag_response(question, project_id)
        payload = {
            "question": question,
            "project_id": project_id,
            "source_id": source_id,
            "workspace_id": workspace_id,
            "response": response,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(external_api_url, json=payload) as resp:
                if resp.status == 200:
                    logger.info("Successfully posted response to external API.")
                else:
                    logger.error(f"Failed to post response to external API. Status: {resp.status}")

    except Exception as e:
        logger.error(f"Error generating RAG response or posting to external API: {e}")
