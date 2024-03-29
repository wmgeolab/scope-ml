from pydantic.v1 import BaseModel, Field


class QuestionAnsweringResponse(BaseModel):
    """
    Represents the response to a question answering request.
    """

    answer: str = Field(description="The answer to the question.")
