from pydantic import BaseModel


class DocumentQARequest(BaseModel):
    question: str
    document_id: str


class DocumentQABulkRequest(BaseModel):
    questions: list[DocumentQARequest]
