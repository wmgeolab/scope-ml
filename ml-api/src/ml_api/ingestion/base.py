from pathlib import Path


class BaseIngestionService:
    def __init__(self):
        pass

    def ingest_file(self, file: Path) -> bool:
        raise NotImplementedError("This method should be overridden by subclasses")

    def ingest_file_batch(self, file_batch: list[Path]) -> bool:
        raise NotImplementedError("This method should be overridden by subclasses")

    def ingest_directory(self, directory: Path) -> bool:
        raise NotImplementedError("This method should be overridden by subclasses")
