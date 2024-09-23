"""
This service is responsible for retrieving chunks from the Qdrant database.

This includes filtering Qdrant queries by metadata, possibly reranking the results,
possibly rewriting the query to something more suitable for knowledge retrieval, and
returning the results.
"""

from llama_index.core.schema import NodeWithScore
from llama_index.core.vector_stores.types import VectorStoreQuery, VectorStoreQueryMode
from ml_api.utils.embeddings import get_embed_model
from ml_api.utils.qdrant import get_qdrant_project_id_filter, get_qdrant_vector_store

from ml_api.config import settings


def retrieve_points_by_project_id(query: str, project_id: str) -> list[NodeWithScore]:
    """Get relevant information from the Qdrant database."""

    # Steps:
    # 1. Get embedding for the query
    # 2. Query the Qdrant database with a project id filter
    # 3. Rerank the results (possibly)
    # 4. Return the results

    embed_model = get_embed_model()
    vector_store = get_qdrant_vector_store()

    query_embedding = embed_model.get_query_embedding(query)

    qdrant_filters = get_qdrant_project_id_filter(project_id=project_id)

    qdrant_query = VectorStoreQuery(
        query_embedding=query_embedding,
        similarity_top_k=settings.RETRIEVAL_TOP_K,
        mode=VectorStoreQueryMode.MMR,
        mmr_threshold=settings.RETRIEVAL_MMR_THRESHOLD,
    )

    query_results = vector_store.query(qdrant_query, qdrant_filters=qdrant_filters)

    if not query_results.nodes:
        # TODO log this, No nodes found for project id x
        return []

    nodes_with_scores = [
        NodeWithScore(node=node, score=score)
        for node, score in zip(query_results.nodes, query_results.similarities or [])
    ]

    return nodes_with_scores


def ensemble_retrieval(query: str):
    """Ensemble retrieval results using BM25 and embeddings."""

    # This is a placeholder for possible future implementation.

    pass
