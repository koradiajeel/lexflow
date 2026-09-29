from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class LawyerBase(BaseModel):
    name:str
    email:str
    phone:str

class LawyerCreate(LawyerBase):
    law_firm_id:UUID

class LawyerResponse(LawyerBase):
    id:UUID
    law_firm_id:UUID
    created_at: datetime

class Config:
    from_attributes = True    

class LawyerUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
