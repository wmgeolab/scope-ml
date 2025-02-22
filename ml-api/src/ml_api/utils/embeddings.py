"""This file is responsible for providing utilities to interact with embeddings."""

from llama_index.embeddings.text_embeddings_inference import TextEmbeddingsInference
from ml_api.config import settings


def get_embed_model():
    return TextEmbeddingsInference(
        model_name=settings.TEI_EMBEDDING_MODEL_NAME, base_url=settings.TEI_URL
    )


def generate_embedding(text: str):
    """Generate an embedding for a text."""

    # TODO: Maybe get rid of this? I don't think its used at all.

    model: TextEmbeddingsInference = get_embed_model()

    return model.get_text_embedding(text)
