from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # vLLM / TEI
    VLLM_URL: str = ""
    VLLM_LLM_MODEL_NAME: str = ""
    TEI_URL: str = ""
    TEI_EMBEDDING_MODEL_NAME: str = "TODO"

    # LLM
    LLM_CONTEXT_WINDOW: int = 32768
    LLM_NUM_OUTPUT: int = 8192

    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION_NAME: str = "TODO"
    EMBEDDING_SIZE: int = 768

    # Retrieval
    RETRIEVAL_TOP_K: int = 20
    RETRIEVAL_MMR_THRESHOLD: float = 0.7

    # RAG Config
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64

    # Ingestion
    DATA_BASE_DIR: Path = Path(
        "/scope/scope-data/gef/output"
    )  # then /{project_id}/{document_id}.{extension}
    INGEST_BATCH_SIZE: int = 10
    # Single file
    READER_NUM_WORKERS_SINGLE: int = 4
    PIPELINE_NUM_WORKERS_SINGLE: int = 1
    PIPELINE_PERSIST: bool = False
    PIPELINE_PERSIST_PATH: str = ""  # Only used if PIPELINE_PERSIST is True

    # Multi-File
    READER_NUM_WORKERS_BATCH: int = 4
    PIPELINE_NUM_WORKERS_BATCH: int = 4


settings = Settings()
