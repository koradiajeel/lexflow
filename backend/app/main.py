from fastapi import FastAPI
from app.api.routes import law_firm
from app.api.routes import lawyer
from app.api.routes import client
from app.api.routes import case
from app.api.routes import user
from app.api.routes import auth


app = FastAPI()

app.include_router(
    law_firm.router,
    prefix="/law-firms",
    tags=["law firms"]
)
app.include_router(
    lawyer.router,
    prefix="/Lawyers",
    tags= ["Lawyer"]
)

app.include_router(
    client.router,
    prefix="/clients",
    tags=["clients"]
)

app.include_router(
    case.router,
    prefix="/cases", 
    tags=["cases"]
    )

app.include_router(
    user.router,
      prefix="/users", 
      tags=["users"])

app.include_router(
    auth.router,
      prefix="/auth",
        tags=["auth"]
    )