from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # vLLM
    VLLM_URL: str = ""
    DEFAULT_LLM_NAME: str = ""
    DEFAULT_EMBEDDING_MODEL: str = "TODO"

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


settings = Settings()
