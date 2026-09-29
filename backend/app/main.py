from fastapi import FastAPI
from app.api.routes import law_firm
from app.api.routes import lawyer
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