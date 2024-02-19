from fastapi import FastAPI
from .models import DocumentQABulkRequest


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/document_summary")
def document_summary(document_id: str):
    return {"DocumentSummary": document_id}


@app.post("/document_qa_bulk")
def document_qa(request: DocumentQABulkRequest):
    return {"DocumentQA": request}
