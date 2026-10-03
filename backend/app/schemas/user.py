from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import UserRole


class UserCreate(BaseModel):
    law_firm_id: UUID
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole = UserRole.STAFF


class UserResponse(BaseModel):
    id: UUID
    law_firm_id: UUID
    email: str
    role: UserRole
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)