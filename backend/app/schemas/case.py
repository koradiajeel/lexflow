from datetime import datetime
from uuid import UUID
from pydantic import BaseModel,ConfigDict,Field
from app.models.enums import CaseStatus

class CaseBase(BaseModel):
    title:str=Field(min_length=2,max_length=255)
    description :str =Field(min_length=1,max_length=1000)

class CaseCreate(CaseBase):
    client_id:UUID
    lawyer_id:UUID

class CaseUpdate(BaseModel):
    title:str | None=Field(default=None,min_length=2,max_length=255)
    description:str |None =Field(default=None,min_length=1,max_length=1000)
    status:CaseStatus|None=None

class CaseResponse(CaseBase):
    id: UUID
    client_id: UUID
    lawyer_id: UUID
    status: CaseStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)