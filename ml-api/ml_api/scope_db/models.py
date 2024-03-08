from sqlmodel import Field, SQLModel


class ScopeSource(SQLModel, table=True):
    __tablename__: str = "scopeBackend_source"

    id: int = Field(primary_key=True)
    text: str
    url: str
    sourceType_id: int = Field(index=True)
