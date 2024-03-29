import logging

from dotenv import load_dotenv
from fastapi import FastAPI

from .ml_algorithms import (
    doc_answer_question,
    doc_extract_actors,
    doc_extract_locations,
    doc_generate_summary,
)
from .models.extraction import ExtractedActors, ExtractedLocations
from .models.qa import QuestionAnsweringResponse, SummarizeDocumentResponse


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/api/generate_summary")
def generate_summary_from_document(document_id: int) -> SummarizeDocumentResponse:
    return doc_generate_summary(document_id)


@app.post("/api/extract_locations")
def extract_locations_from_document(document_id: int) -> ExtractedLocations:
    return doc_extract_locations(document_id)


@app.post("/api/extract_actors")
def extract_actors_from_document(document_id: int) -> ExtractedActors:
    return doc_extract_actors(document_id)


@app.post("/api/answer_question")
def answer_question_from_document(
    document_id: int, question: str
) -> QuestionAnsweringResponse:
    return doc_answer_question(document_id, question)
