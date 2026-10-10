from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.enums import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    role: UserRole = UserRole.STAFF

    @field_validator("role")
    @classmethod
    def role_cannot_be_owner(cls, value: UserRole) -> UserRole:
        if value == UserRole.OWNER:
            raise ValueError("Only Lawyer or Staff users can be created")
        return value


class UserResponse(BaseModel):
    id: UUID
    law_firm_id: UUID
    email: str
    role: UserRole
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)