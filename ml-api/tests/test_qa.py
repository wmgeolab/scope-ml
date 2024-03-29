import pytest

from ml_api.ml_algorithms import doc_answer_question
from ml_api.models.qa import QuestionAnsweringResponse


VALID_DOCUMENT_IDS = [1, 2, 3]


@pytest.mark.parametrize("document_id", VALID_DOCUMENT_IDS)
def test_answer_question(document_id: int):
    """Test that the doc_answer_question function runs without errors and returns a QuestionAnsweringResponse object."""
    response = doc_answer_question(
        document_id, "What is the main topic of this document?"
    )
    assert isinstance(response, QuestionAnsweringResponse)
    assert response.answer != ""
