"""This file is responsible for providing utilities to interact with embeddings."""

from llama_index.embeddings.text_embeddings_inference import TextEmbeddingsInference
from ml_api.config import settings


def get_embed_model():
    return TextEmbeddingsInference(model_name=settings.DEFAULT_EMBEDDING_MODEL)


def generate_embedding(text: str):
    """Generate an embedding for a text."""

    model: TextEmbeddingsInference = get_embed_model()

    return model.get_text_embedding(text)
