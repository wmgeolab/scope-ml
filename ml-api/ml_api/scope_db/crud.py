from sqlmodel import Session, select

from .database import engine
from .models import ScopeSource, SourcingSource


def get_document(document_id: int) -> ScopeSource:
    """Get a document from the database."""
    with Session(engine) as session:
        statement = select(ScopeSource).where(ScopeSource.id == document_id)
        document = session.exec(statement).one()

        return document


def get_sourcing_source(source_id: int) -> SourcingSource:
    with Session(engine) as session:
        statement = select(SourcingSource).where(SourcingSource.id == source_id)
        source = session.exec(statement).one()

        return source


def get_sourcing_sources():
    with Session(engine) as session:
        statement = select(SourcingSource)
        sources = session.exec(statement).all()

        return sources
