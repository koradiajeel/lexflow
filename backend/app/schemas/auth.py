from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    # Law firm details
    firm_name: str = Field(min_length=1, max_length=225)
    firm_email: str = Field(min_length=3, max_length=226)
    firm_phone: str = Field(min_length=5, max_length=20)
    firm_address: str = Field(min_length=1, max_length=500)

    # First user of the firm (becomes Owner)
    owner_email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=72)
