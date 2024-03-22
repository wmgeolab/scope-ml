import logging

from fastapi import FastAPI

from .ml_algorithms.summarize import summarize_document
from .scope_db.crud import get_document
from .scope_db.models import ScopeSource
from .types import DocumentQABulkRequest

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv

load_dotenv()


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/document_summary")
def document_summary(document_id: int):
    summary = summarize_document(document_id)

    return {"summary": summary}


@app.post("/document_qa_bulk")
def document_qa(request: DocumentQABulkRequest):
    return {"DocumentQA": request}


@app.get("/together")
def together():

    return summarize_document(12)


# @app.get("/test_sqlmodel", response_model=list[ScopeSource])
# def test_sqlmodel():

#     with Session(engine) as session:
#         statement = select(ScopeSource)
#         results = session.exec(statement)

#         results = results.all()

#         print(f"Successfully retrieved {len(results)} results from the database.")
#         return results


# @app.post("/test_get_doc")
# def test_get_doc(document_id: int):
#     return get_document(document_id)
