import logging

from dotenv import load_dotenv
from fastapi import FastAPI

from .ml_algorithms.extract import doc_extract_actors, doc_extract_locations
from .ml_algorithms.summarize import summarize_document
from .models.extraction import ExtractedActors, ExtractedLocations

# from .models.requests import DocumentQABulkRequest

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/document_summary")
def document_summary(document_id: int):
    summary = summarize_document(document_id)

    return {"summary": summary}


# @app.post("/document_qa_bulk")
# def document_qa(request: DocumentQABulkRequest):
#     return {"DocumentQA": request}


@app.post("/api/extract/locations")
def extract_locations_from_document(document_id: int) -> ExtractedLocations:
    return doc_extract_locations(document_id)


@app.post("/api/extract/actors")
def extract_actors_from_document(document_id: int) -> ExtractedActors:
    return doc_extract_actors(document_id)
