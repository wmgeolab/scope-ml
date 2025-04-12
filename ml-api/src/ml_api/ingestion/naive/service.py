"""
This service is responsible for ingesting data (pdf, docx, etc) into the Qdrant database.

This includes parsing the raw document to text, chunking the text with metadata,
and indexing the chunks into the Qdrant database to be used in inference.
"""

import logging
from pathlib import Path

from llama_index.core.readers import SimpleDirectoryReader
from llama_index.core.vector_stores.types import BasePydanticVectorStore
from ml_api.config import settings
from ml_api.utils.qdrant import get_qdrant_vector_store

from ..base import BaseIngestionService
from .metadata import file_metadata
from .pipeline import get_pipeline

logger = logging.getLogger(__name__)


class NaiveIngestionService(BaseIngestionService):
    """Service to ingest data into the Qdrant database and manage state."""

    def __init__(self, vector_store: BasePydanticVectorStore | None = None):
        self.vector_store = (
            get_qdrant_vector_store() if vector_store is None else vector_store
        )

        self._pipeline = get_pipeline()

    def ingest_file(self, file: Path) -> bool:
        """Ingest a specific file into the qdrant database.

        Args:
            file (Path): the path to the file to ingest
        """

        try:
            # Try to ingest the file
            reader = SimpleDirectoryReader(
                input_files=[file], file_metadata=file_metadata
            )

            docs = reader.load_data(num_workers=settings.READER_NUM_WORKERS_SINGLE)
            logger.info(f"Loaded {len(docs)} documents from {file}")

            # Pipeline includes embeddings and vector db, so this is all we need to run
            processed_nodes = self._pipeline.run(
                show_progress=True,
                documents=docs,
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
            return False

    def ingest_file_batch(self, file_batch: list[Path]) -> bool:
        """
        Ingests a group of files into the vector database. Expects a pre-batched list of file paths.

        Args:
            file_paths (list[Path]): A list of file paths to be ingested.

        Raises:
            Exception: If any error occurs during the ingestion process, it will be logged.
        """
        try:
            reader = SimpleDirectoryReader(
                input_files=file_batch, file_metadata=file_metadata
            )

            docs = reader.load_data(num_workers=settings.READER_NUM_WORKERS_BATCH)
            logger.info(f"Loaded {len(docs)} documents from {len(file_batch)} files.")

            processed_nodes = self._pipeline.run(
                show_progress=True,
                documents=docs,
                num_workers=settings.PIPELINE_NUM_WORKERS_BATCH,
            )
            logger.info(
                f"Processed & ingested {len(processed_nodes)} nodes from {len(file_batch)} files."
            )

        except Exception as e:
            logger.error(f"Batch ingestion failed: {e}", exc_info=True)
            return False

        return True

    def generate_file_batches(
        self, files: list[Path], batch_size: int = settings.INGEST_BATCH_SIZE
    ):
        """Batch files into groups of a certain size.

        Args:
            files (list[Path]): The list of files to be batched.
            batch_size (int, optional): The size of each batch. Defaults to settings.INGEST_BATCH_SIZE.

        Yields:
            list[Path]: A batch of files.
        """
        for i in range(0, len(files), batch_size):
            yield files[i : i + batch_size]

    def ingest_directory(self, directory: Path = settings.DATA_BASE_DIR) -> bool:
        """Ingest all files in a directory.

        This method will enumerate all files in the given directory and its subdirectories,
        and ingest them in batches.

        TODO: Make this check the database for existing files and only ingest new ones.
        """

        all_files = list(
            directory.glob("**/*")
        )  # Gives all files in the directory and subdirectories

        if not all_files:
            logger.warning(
                f"No files found in directory {directory}, aborting ingestion."
            )
            return False

        batches = list(self.generate_file_batches(all_files))

        num_processed_files = 0
        for i, batch in enumerate(batches):
            self.ingest_file_batch(batch)
            num_processed_files += len(batch)
            logger.info(
                f"Progress: Batch #{i} | {num_processed_files}/{len(all_files)} files processed."
            )

        return True
