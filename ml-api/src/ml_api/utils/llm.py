"""This file is responsible for providing utilities to interact with the LLMs."""

from llama_index.llms.openai_like import OpenAILike
from ml_api.config import settings


def get_llm(model_name: str = settings.VLLM_LLM_MODEL_NAME):
    return OpenAILike(
        model=model_name,
        api_base=f"{settings.VLLM_LLM_URL}/v1",
        api_key=settings.VLLM_API_KEY,
        context_window=settings.LLM_CONTEXT_WINDOW,
        max_tokens=settings.LLM_MAX_OUTPUT_TOKENS,
        temperature=settings.LLM_TEMPERATURE,
        timeout=settings.LLM_TIMEOUT,
    )  # type: ignore
