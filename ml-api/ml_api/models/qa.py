from pydantic import BaseModel, Field


class QuestionAnsweringResponse(BaseModel):
    """
    Represents the response to a question answering request.
    """

    answer: str = Field(description="The answer to the question.")


class SummarizeDocumentResponse(BaseModel):
    """
    Represents the response to a document summarization request.
    """

    summary: str = Field(description="The summary of the document.")
