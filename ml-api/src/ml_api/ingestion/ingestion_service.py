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

from .metadata import file_metadata
from .pipeline import get_pipeline

logger = logging.getLogger(__name__)


class IngestionService:
    """Service to ingest data into the Qdrant database and manage state."""

    def __init__(self, vector_store: BasePydanticVectorStore | None = None):
        self.vector_store = (
            get_qdrant_vector_store() if vector_store is None else vector_store
        )
        self.data_base_dir = settings.DATA_BASE_DIR
        self.pipeline = get_pipeline()

    def ingest_single_file(self, file_path: Path) -> bool:
        """Ingest a specific file into the qdrant database.

        Args:
            file_path (Path): the path to the file to ingest
        """

        try:
            # Try to ingest the file
            reader = SimpleDirectoryReader(
                input_files=[file_path], file_metadata=file_metadata
            )

            docs = reader.load_data(num_workers=settings.READER_NUM_WORKERS_SINGLE)
            logger.info(f"Loaded {len(docs)} documents from {file_path}")

            # Pipeline includes embeddings and vector db, so this is all we need to run
            processed_nodes = self.pipeline.run(
                show_progress=True,
                documents=docs,
                num_workers=settings.PIPELINE_NUM_WORKERS_SINGLE,
            )

            logger.info(
                f"Processed & ingested {len(processed_nodes)} nodes from {file_path}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to ingest file {file_path}: {e}")
            return False

    def ingest_files(self, file_paths: list[Path]):
        """
        Ingests a group of files into the vector database. Expects a pre-batched list of file paths.

        Args:
            file_paths (list[Path]): A list of file paths to be ingested.

        Raises:
            Exception: If any error occurs during the ingestion process, it will be logged.
        """
        try:
            reader = SimpleDirectoryReader(
                input_files=file_paths, file_metadata=file_metadata
            )

            docs = reader.load_data(num_workers=settings.READER_NUM_WORKERS_BATCH)
            logger.info(f"Loaded {len(docs)} documents from {len(file_paths)} files.")

            processed_nodes = self.pipeline.run(
                show_progress=True,
                documents=docs,
                num_workers=settings.PIPELINE_NUM_WORKERS_BATCH,
            )
            logger.info(
                f"Processed & ingested {len(processed_nodes)} nodes from {len(file_paths)} files."
            )

        except Exception as e:
            logger.error(f"Batch ingestion failed: {e}", exc_info=True)

    def _batch_files(
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

    def ingest_directory(self, directory: Path = settings.DATA_BASE_DIR):
        """Ingest all files in a directory.

        TODO: Make this check the database for existing files and only ingest new ones.
        """

        all_files = list(
            directory.glob("**/*")
        )  # Gives all files in the directory and subdirectories

        if not all_files:
            logger.warning(
                f"No files found in directory {directory}, aborting ingestion."
            )
            return

        batches = list(self._batch_files(all_files))

        num_processed_files = 0
        for i, batch in enumerate(batches):
            self.ingest_files(batch)
            num_processed_files += len(batch)
            logger.info(
                f"Progress: Batch #{i} | {num_processed_files}/{len(all_files)} files processed."
            )
