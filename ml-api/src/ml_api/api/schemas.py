from pydantic import BaseModel


class GEFRagRequestBatch(BaseModel):
    questions: list[str]
    project_id: str
    
class GEFRagRequest(BaseModel):
    question: str
    source: str
    workspace: str
    project_id: str = "9467"


class GEFRagResponse(BaseModel):
    answers: dict[str, str]


class IngestionRequest(BaseModel):
    project_ids: list[str]
