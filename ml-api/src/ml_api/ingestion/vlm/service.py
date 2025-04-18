import logging
from pathlib import Path

from llama_index.core.schema import Document
from llama_index.core.vector_stores.types import BasePydanticVectorStore
from ml_api.config import settings
from ml_api.utils.qdrant import get_qdrant_vector_store
from openai import OpenAI

from ..base import BaseIngestionService
from ..pipeline import get_pipeline
from .rolmocr_utils import do_ocr_on_image, document_to_base64_images

logger = logging.getLogger(__name__)


class VLMIngestionService(BaseIngestionService):
    def __init__(self, vector_store: BasePydanticVectorStore | None = None):
        super().__init__()

        if settings.VLLM_VLM_URL is None:
            raise ValueError("VLLM_VLM_URL is not set in the environment variables.")

        self.vector_store = (
            get_qdrant_vector_store() if vector_store is None else vector_store
        )

        self.oai_client_vlm = OpenAI(
            base_url=settings.VLLM_VLM_URL, api_key=settings.VLLM_API_KEY
        )

        self._pipeline = get_pipeline()

        logger.info(
            f"VLM Ingestion Service initialized with VLM URL: {settings.VLLM_VLM_URL}"
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

        try:
            documents = self._get_parsed_documents_from_file(file)
            if not documents:
                logger.warning(f"No documents parsed from file: {file}")
                return False

            logger.info(f"Parsed {len(documents)} documents from file: {file}")

            # Pipeline includes embeddings and vector db, so this is all we need to run
            processed_nodes = self._pipeline.run(
                show_progress=True,
                documents=documents,
                num_workers=settings.PIPELINE_NUM_WORKERS_SINGLE,
            )
            if settings.PIPELINE_PERSIST:
                self._pipeline.persist(persist_dir=settings.PIPELINE_PERSIST_PATH)

            logger.info(
                f"Processed & ingested {len(processed_nodes)} nodes from {file}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to ingest file {file}: {e}")
            logger.exception("Exception occurred during file ingestion")

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

    def _get_parsed_documents_from_file(self, file: Path) -> list[Document]:
        """
        Converts a document file into a list of parsed LlamaIndex documents by processing the file as images.

        Args:
            file (Path): The path to the document file to be processed.

        Returns:
            list[Document]: A list of LlamaIndex Document objects created from the text extracted from the document.

        The function performs the following steps:
        1. Converts the document to base64 encoded images.
        2. Performs OCR on each image to extract text.
        3. Constructs LlamaIndex Document objects from the extracted text, incorporating metadata such as filename,
        original filename, file extension, page number, and project ID.

        Logs warnings and errors if any step fails or yields no data.
        """

        try:
            images = document_to_base64_images(file)
        except ValueError as e:
            logger.error(f"Failed to convert document to images: {e}")
            return []

        if not images:
            logger.warning(f"No images extracted from file: {file}")
            return []

        # Perform OCR on each image and print the text
        page_texts = []
        for image in images:
            text = do_ocr_on_image(image, self.oai_client_vlm)
            if text is None or text.strip() == "":
                logger.warning("OCR returned no text for an image.")
                continue

            page_texts.append(text)
            logger.debug(
                f"Extracted text from image: {text[:100]}..."
            )  # Log first 100 chars

        # Now that we have the text, we can create LlamaIndex documents
        documents = []
        for i, text in enumerate(page_texts):
            metadata = {
                "filename": file.name,
                "original_filename": "".join(file.name.split("__")[1:]),
                "extension": file.suffix,
                "page_number": i + 1,
                "project_id": file.name.split("_")[0][1:],
            }

            documents.append(Document(text=text, metadata=metadata))

        return documents
