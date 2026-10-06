from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID

from app.core.database import get_db
from app.models.case import Case
from app.models.client import Client
from app.models.lawyer import Lawyer
from app.schemas.case import CaseResponse, CaseCreate, CaseUpdate
from app.api.routes.auth import require_role, get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(
    data: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Lawyer")),
):
    client = db.scalar(select(Client).where(Client.id == data.client_id))
    if client is None:
        raise HTTPException(status_code=404, detail="client not found")

    lawyer = db.scalar(select(Lawyer).where(Lawyer.id == data.lawyer_id))
    if lawyer is None:
        raise HTTPException(status_code=404, detail="lawyer not found")

    case = Case(
        title=data.title,
        description=data.description,
        client_id=data.client_id,
        lawyer_id=data.lawyer_id,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(
    case_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = db.scalar(select(Case).where(Case.id == case_id))
    if case is None:
        raise HTTPException(status_code=404, detail="case not found")
    return case


@router.patch("/{case_id}", response_model=CaseResponse)
def update_case(
    case_id: UUID,
    data: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Lawyer")),
):
    case = db.scalar(select(Case).where(Case.id == case_id))
    if case is None:
        raise HTTPException(status_code=404, detail="case not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(case, field, value)

    db.commit()
    db.refresh(case)
    return case