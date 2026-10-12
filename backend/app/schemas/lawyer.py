from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LawyerBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=3, max_length=255)
    phone: str = Field(min_length=5, max_length=20)


class LawyerCreate(LawyerBase):
    pass  # law_firm_id comes from the logged-in user's token


class LawyerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = Field(default=None, min_length=3, max_length=255)
    phone: str | None = Field(default=None, min_length=5, max_length=20)


class LawyerLoginCreate(BaseModel):
    # Temporary password the Owner gives the lawyer; they can change it later.
    password: str = Field(min_length=8, max_length=72)


class LawyerResponse(LawyerBase):
    id: UUID
    law_firm_id: UUID
    user_id: UUID | None = None  # set when the lawyer has a login account
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)