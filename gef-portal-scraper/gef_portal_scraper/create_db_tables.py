from typing import Optional
from datetime import datetime
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_filename: str
    download_url: Optional[str] = None
    document_type: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

# SQLite database URL
sqlite_url = "sqlite:///document_database.db"
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def add_document(original_filename: str, download_url: str = None, document_type: str = None):
    document = Document(
        original_filename=original_filename,
        download_url=download_url,
        document_type=document_type
    )
    with Session(engine) as session:
        session.add(document)
        session.commit()
        session.refresh(document)
    return document

def get_all_documents():
    with Session(engine) as session:
        documents = session.exec(select(Document)).all()
    return documents

def main():
    create_db_and_tables()
    
    # Example: Add a document
    new_doc = add_document(
        "example_doc.pdf",
        "https://example.com/docs/example_doc.pdf",
        "PDF"
    )
    print(f"Added document: {new_doc}")
    
    # Example: Retrieve all documents
    all_docs = get_all_documents()
    print("All documents:")
    for doc in all_docs:
        print(f"- {doc.original_filename} ({doc.document_type})")

if __name__ == "__main__":
    main()