from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from app.core.database import get_db
from app.models.client import Client
from app.models.law_firm import LawFirm
from app.schemas.client import ClientResponse, ClientCreate
from app.api.routes.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    law_firm = db.scalar(select(LawFirm).where(LawFirm.id == data.law_firm_id))
    if law_firm is None:
        raise HTTPException(status_code=404, detail="law firm not found")

    client = Client(
        name=data.name,
        email=data.email,
        phone=data.phone,
        law_firm_id=data.law_firm_id,
    )
    db.add(client)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="client with this email or phone already exists",
        )
    db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = db.scalar(select(Client).where(Client.id == client_id))
    if client is None:
        raise HTTPException(status_code=404, detail="client not found")
    return client