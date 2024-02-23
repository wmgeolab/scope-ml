import logging

from fastapi import FastAPI

from .ml_algorithms.summarize import summarize_document
from .types import DocumentQABulkRequest

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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


@app.get("/together")
def together():

    return summarize_document("sample_id")
