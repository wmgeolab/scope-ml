from pydantic import BaseModel


class GEFRagRequestBatch(BaseModel):
    questions: list[str]
    project_id: str


class GEFRagResponse(BaseModel):
    answers: dict[str, str]


class IngestionRequest(BaseModel):
    project_ids: list[str]
