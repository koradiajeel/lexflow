from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user, require_role
from app.core.database import get_db
from app.models.case import Case
from app.models.client import Client
from app.models.enums import CaseStatus
from app.models.lawyer import Lawyer
from app.models.user import User
from app.schemas.case import CaseCreate, CaseResponse, CaseUpdate
from app.services.case_access import sees_only_own_cases, user_can_see_case

router = APIRouter()


def get_case_in_firm(db: Session, case_id: UUID, current_user: User) -> Case:
    """Return the case if this user may see it (same firm; a Lawyer only their own cases), else 404."""
    case = db.scalar(select(Case).where(Case.id == case_id))
    if case is None or not user_can_see_case(db, case, current_user):
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.get("/", response_model=list[CaseResponse])
def list_cases(
    status_filter: CaseStatus | None = Query(default=None, alias="status"),
    client_id: UUID | None = None,
    lawyer_id: UUID | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Case)
        .join(Lawyer, Case.lawyer_id == Lawyer.id)
        .where(Lawyer.law_firm_id == current_user.law_firm_id)
    )
    # A Lawyer only sees cases assigned to their own lawyer profile.
    if sees_only_own_cases(current_user):
        stmt = stmt.where(Lawyer.user_id == current_user.id)

    if status_filter is not None:
        stmt = stmt.where(Case.status == status_filter)
    if client_id is not None:
        stmt = stmt.where(Case.client_id == client_id)
    if lawyer_id is not None:
        stmt = stmt.where(Case.lawyer_id == lawyer_id)

    stmt = stmt.order_by(Case.created_at.desc()).limit(limit).offset(offset)
    return db.scalars(stmt).all()


@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(
    data: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Lawyer")),
):
    client = db.scalar(select(Client).where(Client.id == data.client_id))
    if client is None or client.law_firm_id != current_user.law_firm_id:
        raise HTTPException(status_code=404, detail="Client not found")

    lawyer = db.scalar(select(Lawyer).where(Lawyer.id == data.lawyer_id))
    if lawyer is None or lawyer.law_firm_id != current_user.law_firm_id:
        raise HTTPException(status_code=404, detail="Lawyer not found")

    if sees_only_own_cases(current_user) and lawyer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Lawyers can only create cases assigned to themselves",
        )

    case = Case(
        title=data.title.strip(),
        description=data.description.strip(),
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
    return get_case_in_firm(db, case_id, current_user)


@router.patch("/{case_id}", response_model=CaseResponse)
def update_case(
    case_id: UUID,
    data: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Lawyer")),
):
    case = get_case_in_firm(db, case_id, current_user)

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(case, field, value)

    db.commit()
    db.refresh(case)
    return case