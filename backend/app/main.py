from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import law_firm
from app.api.routes import lawyer
from app.api.routes import client
from app.api.routes import case
from app.api.routes import user
from app.api.routes import auth
from app.api.routes import document


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    law_firm.router,
    prefix="/law-firms",
    tags=["law firms"]
)
app.include_router(
    lawyer.router,
    prefix="/lawyers",
    tags=["lawyers"]
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

app.include_router(\
    document.router, 
    tags=["documents"]
    )