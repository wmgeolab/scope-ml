"""
This file is responsible for providing utilities to send requests to Qdrant.
"""

from llama_index.vector_stores.qdrant import QdrantVectorStore
from ml_api.config import settings
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.models import Distance, VectorParams


def get_qdrant_vector_store(
    collection_name: str = settings.QDRANT_COLLECTION_NAME,
    qdrant_client: QdrantClient | None = None,
    recreate_existing_collection=False,
    create_missing_collection=True,
) -> QdrantVectorStore:
    """Get the Qdrant vector store."""

    if qdrant_client is None:
        qdrant_client = QdrantClient(url=settings.QDRANT_URL)

    # Create collection if it doesn't exist
    try:
        qdrant_client.get_collection(collection_name)
    except Exception:
        if create_missing_collection:
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_SIZE, distance=Distance.COSINE
                ),
            )
        else:
            raise

    vector_store = QdrantVectorStore(
        collection_name=collection_name, qdrant_client=qdrant_client
    )

    return vector_store


def get_qdrant_project_id_filter(project_id: str):
    qdrant_filters = qdrant_models.Filter(
        must=[
            qdrant_models.FieldCondition(
                key="project_id", match=qdrant_models.MatchValue(value=str(project_id))
            )
        ],
        # should=[
        #     qdrant_models.FieldCondition(
        #         key="doc_type",
        #         match=qdrant_models.MatchAny(
        #             any=[document_type.value for document_type in document_types]
        #         ),
        #     )
        # ],
    )

    return qdrant_filters
