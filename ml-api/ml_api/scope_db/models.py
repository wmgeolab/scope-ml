from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime


class ScopeSource(SQLModel, table=True):
    __tablename__: str = "scopeBackend_source"

    id: int = Field(primary_key=True)
    text: str
    url: str
    sourceType_id: int = Field(index=True)


class SourcingSource(SQLModel, table=True):
    __tablename__: str = "sourcing_m_source"

    id: int = Field(primary_key=True)
    source_url: str
    source_html: str
    source_text: str
    # source_date example from MySQL database: 2015-10-17 00:00:00.000000. this is a datetime(6) (yyyy-MM-dd HH:mm:ss.ffffff)
    # Type the field accordingly
    # source_date: models.DateField(_(""), auto_now=False, auto_now_add=False)
    source_date: str
    date_added: str
    current_status: str
    current_user_id: int | None
