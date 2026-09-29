from pydantic import BaseModel,Field,ConfigDict
from uuid import UUID
from datetime import datetime

class LawFirmBase(BaseModel):
    name: str = Field(min_length=2, max_length=225)
    email: str
    phone: str = Field(max_length=20)
    address: str = Field(max_length=500)

class LawFirmCreate(LawFirmBase):
    pass 

class LawFirmUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

class LawFirmResponse(LawFirmBase):
    id:UUID
    created_at:datetime
    model_config = ConfigDict(from_attributes=True)

