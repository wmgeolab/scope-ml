import logging
from pathlib import Path

from llama_index.core.vector_stores.types import BasePydanticVectorStore
from ml_api.config import settings
from ml_api.ingestion.base import BaseIngestionService
from ml_api.utils.qdrant import get_qdrant_vector_store
from openai import OpenAI

from .rolmocr_utils import do_ocr_on_image, document_to_base64_images

logger = logging.getLogger(__name__)


class VLMIngestionService(BaseIngestionService):
    def __init__(self, vector_store: BasePydanticVectorStore | None = None):
        super().__init__()

        self.vector_store = (
            get_qdrant_vector_store() if vector_store is None else vector_store
        )

        self.oai_client_vlm = OpenAI(
            base_url=settings.VLLM_VLM_URL, api_key=settings.VLLM_API_KEY
        )

    def ingest_file(self, file: Path) -> bool:
        """Ingest a specific file into the qdrant database using a VLM model.

        Args:
            file (Path): the path to the file to ingest

        Returns:
            bool: True if ingestion was successful, False otherwise
        """

        """
        steps:
        1. get the file and convert it to images
        2. parse the images to text using the VLM model
        3. make LlamaIndex documents from the text
        4. use a pipeline to ingest the documents into the vector store
        """

        if not file.suffix.lower() == ".pdf":
            logger.info(f"Skipping file since it isn't a pdf: {file}")
            return True

        images = document_to_base64_images(file)

        for image in images:
            text = do_ocr_on_image(image, self.oai_client_vlm)
            print(text)  # TODO incomplete

        return False

    def ingest_directory(self, directory: Path) -> bool:
        """Ingest all files in a directory into the qdrant database using a VLM model.

        Args:
            directory (Path): the path to the directory to ingest

        Returns:
            bool: True if ingestion was successful, False otherwise
        """

        for file in directory.iterdir():
            if file.is_file():
                success = self.ingest_file(file)
                if not success:
                    logger.error(f"Failed to ingest file: {file}")
                    return False

        logger.info(f"Ingestion completed for directory: {directory}")

        return True
