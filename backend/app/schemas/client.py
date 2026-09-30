from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ClientBase(BaseModel):
    name: str = Field(min_length=2, max_length=225)
    email: str = Field(max_length=255)
    phone: str = Field(max_length=20)


class ClientCreate(ClientBase):
    law_firm_id: UUID


class ClientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=225)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)


class ClientResponse(ClientBase):
    id: UUID
    law_firm_id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)