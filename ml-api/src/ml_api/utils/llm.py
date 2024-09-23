"""This file is responsible for providing utilities to interact with the LLMs."""

from ml_api.config import settings
from llama_index.llms.openai_like import OpenAILike


def get_llm(model_name: str = settings.DEFAULT_LLM_NAME):
    return OpenAILike(
        model=model_name,
        api_base=settings.VLLM_URL,
        api_key="",
    )  # type: ignore
