from ..config import Config
from llama_index.llms.together import TogetherLLM


def get_llm() -> TogetherLLM:
    return TogetherLLM(model=Config.TOGETHER_LLM_MODEL)
