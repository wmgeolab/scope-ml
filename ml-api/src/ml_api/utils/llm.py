"""This file is responsible for providing utilities to interact with the LLMs."""

from llama_index.llms.openai_like import OpenAILike
from ml_api.config import settings


def get_llm(model_name: str = settings.VLLM_LLM_MODEL_NAME):
    return OpenAILike(
        model=model_name,
        api_base=settings.VLLM_URL,
        api_key=settings.VLLM_API_KEY,
        context_window=settings.LLM_CONTEXT_WINDOW,
        max_tokens=settings.LLM_MAX_OUTPUT_TOKENS,
        temperature=settings.LLM_TEMPERATURE,
        additional_kwargs={
            "top_p": 0.8,
            "repetition_penalty": 1.05,
        },
    )  # type: ignore
