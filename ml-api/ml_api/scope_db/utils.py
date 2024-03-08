from sqlmodel import Session, select

from .database import engine
from .models import ScopeSource


def get_document(document_id: int) -> ScopeSource:
    """Get a document from the database."""
    with Session(engine) as session:
        statement = select(ScopeSource).where(ScopeSource.id == document_id)
        document = session.exec(statement).one()

        return document
