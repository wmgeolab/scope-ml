import pytest
from ml_api.ml_algorithms.summarize import doc_generate_summary
from ml_api.models.qa import SummarizeDocumentResponse

from .config import VALID_DOCUMENT_IDS


@pytest.mark.parametrize("document_id", VALID_DOCUMENT_IDS)
def test_generate_summary(document_id: int):
    """Test that the generate_summary function runs without errors and returns a SummarizeDocumentResponse object."""
    generated_summary = doc_generate_summary(document_id)
    assert isinstance(generated_summary, SummarizeDocumentResponse)
