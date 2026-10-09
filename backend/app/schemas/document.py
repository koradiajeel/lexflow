import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=1, max_length=100)
    size: int = Field(gt=0)


class DocumentResponse(BaseModel):
    id: uuid.UUID
    case_id: uuid.UUID
    uploaded_by: uuid.UUID
    filename: str
    content_type: str
    size: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)