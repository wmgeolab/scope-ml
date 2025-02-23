from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TransformComponent

from ml_api.config import settings
from ml_api.utils.qdrant import get_qdrant_vector_store
from ml_api.utils.embeddings import get_embed_model


def get_pipeline(
    persist=settings.PIPELINE_PERSIST,
    persist_path: str = settings.PIPELINE_PERSIST_PATH,
) -> IngestionPipeline:
    qdrant = get_qdrant_vector_store()
    embed_model = get_embed_model()

    transformations: list[TransformComponent] = [
        SentenceSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            include_metadata=True,
        ),
        embed_model,
    ]

    pipeline = IngestionPipeline(transformations=transformations, vector_store=qdrant)

    if persist and persist_path:
        pipeline.persist(persist_dir=persist_path)

    return pipeline
