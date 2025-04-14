from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ==========================================================================
    # API Server Configuration
    # ==========================================================================

    # Scope Backend Integration
    SCOPE_BACKEND_URL: str = ""
    SCOPE_BACKEND_AUTH_TOKEN: str = ""

    # Logging Configuration
    SUPPRESS_LOGGERS: list[str] = []
    SUPPRESSED_LEVEL: str = "INFO"

    # MLflow Integration
    MLFLOW_LOGGING: bool = True
    MLFLOW_TRACKING_URI: str = "http://mlflow-server-svc:5000"

    # ==========================================================================
    # External Service Connections
    # ==========================================================================

    # vLLM / TEI Configuration - Text Embedding
    TEI_URL: str = ""
    TEI_EMBEDDING_MODEL_NAME: str = "TODO"

    # vLLM - Text Generation
    VLLM_LLM_URL: str = ""
    VLLM_LLM_MODEL_NAME: str = ""
    VLLM_API_KEY: str = "None"
    LLM_TIMEOUT: int = 180  # seconds

    # vLLM - Vision Language Model
    VLLM_VLM_URL: str = ""
    VLLM_VLM_MODEL_NAME: str = ""

    # Qdrant Vector DB
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION_NAME: str = "TODO"
    EMBEDDING_SIZE: int = 768

    # ==========================================================================
    # Model Configuration
    # ==========================================================================

    # LLM Parameters
    LLM_CONTEXT_WINDOW: int = 8192
    LLM_MAX_OUTPUT_TOKENS: int | None = 2048  # Parameter for the OpenAILike llm
    LLM_NUM_OUTPUT: int = 2048  # parameter for the PromptHelper
    LLM_TEMPERATURE: float = 0.7

    # Retrieval Parameters
    RETRIEVAL_TOP_K: int = 20
    RETRIEVAL_MMR_THRESHOLD: float = 0.7

    # RAG Configuration
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64

    # ==========================================================================
    # Data Processing
    # ==========================================================================

    # Ingestion Paths
    DATA_BASE_DIR: Path = Path(
        "/scope/scope-data/gef/output"
    )  # then /{project_id}/{document_id}.{extension}

    # Processing Configuration
    INGEST_BATCH_SIZE: int = 10

    # PDF Processing
    PDF_2_PNG_DPI: int = 300

    # Single File Processing
    READER_NUM_WORKERS_SINGLE: int = 4
    PIPELINE_NUM_WORKERS_SINGLE: int = 1
    PIPELINE_PERSIST: bool = False
    PIPELINE_PERSIST_PATH: str = ""  # Only used if PIPELINE_PERSIST is True

    # Multi-File Processing
    READER_NUM_WORKERS_BATCH: int = 4
    PIPELINE_NUM_WORKERS_BATCH: int = 4


settings = Settings()
