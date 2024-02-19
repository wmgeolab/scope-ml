from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class DocumentQARequest(BaseModel):
    question: str
    document_id: str


class DocumentQABulkRequest(BaseModel):
    questions: list[DocumentQARequest]


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/document_qa_bulk")
def document_qa(request: DocumentQABulkRequest):
    return {"DocumentQA": request}
