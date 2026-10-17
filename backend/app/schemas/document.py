import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

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



class DocumentEmailRequest(BaseModel):
    """Body of POST /documents/{id}/email."""

    to: EmailStr
    message: str = Field(default="", max_length=2000)


class DocumentEmailResponse(BaseModel):
    """What the API answers after sending."""

    sent_to: str
    filename: str