"""This file is responsible for providing utilities to interact with the LLMs."""

from llama_index.llms.openai_like import OpenAILike
from ml_api.config import settings


def get_llm(model_name: str = settings.VLLM_LLM_MODEL_NAME):
    return OpenAILike(
        model=model_name,
        api_base=settings.VLLM_URL,
        api_key=settings.VLLM_API_KEY,
    )  # type: ignore
