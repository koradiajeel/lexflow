from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user, require_role
from app.core.database import get_db
from app.models.case import Case
from app.models.lawyer import Lawyer
from app.models.user import User
from app.schemas.lawyer import LawyerCreate, LawyerResponse, LawyerUpdate

router = APIRouter()


def get_lawyer_for_user(db: Session, lawyer_id: UUID, current_user: User) -> Lawyer:
    """Return the lawyer if it exists AND belongs to the user's firm, else 404."""
    lawyer = db.scalar(select(Lawyer).where(Lawyer.id == lawyer_id))
    if lawyer is None or lawyer.law_firm_id != current_user.law_firm_id:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    return lawyer


@router.post("/", response_model=LawyerResponse, status_code=status.HTTP_201_CREATED)
def create_lawyer(
    data: LawyerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner")),
):
    lawyer = Lawyer(
        name=data.name.strip(),
        email=data.email.strip().lower(),
        phone=data.phone.strip(),
        law_firm_id=current_user.law_firm_id,
    )
    db.add(lawyer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A lawyer with this email or phone already exists",
        )
    db.refresh(lawyer)
    return lawyer

@router.get("/", response_model=list[LawyerResponse])
def list_lawyers(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Lawyer)
        .where(Lawyer.law_firm_id == current_user.law_firm_id)
        .order_by(Lawyer.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return db.scalars(stmt).all()

@router.get("/{lawyer_id}", response_model=LawyerResponse)
def get_lawyer(
    lawyer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_lawyer_for_user(db, lawyer_id, current_user)


@router.patch("/{lawyer_id}", response_model=LawyerResponse)
def update_lawyer(
    lawyer_id: UUID,
    data: LawyerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner")),
):
    lawyer = get_lawyer_for_user(db, lawyer_id, current_user)

    changes = data.model_dump(exclude_unset=True)
    if "email" in changes and changes["email"] is not None:
        changes["email"] = changes["email"].strip().lower()

    for field, value in changes.items():
        if value is not None:
            setattr(lawyer, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A lawyer with this email or phone already exists",
        )
    db.refresh(lawyer)
    return lawyer


@router.delete("/{lawyer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lawyer(
    lawyer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner")),
):
    lawyer = get_lawyer_for_user(db, lawyer_id, current_user)

    has_cases = db.scalar(select(Case.id).where(Case.lawyer_id == lawyer_id)) is not None
    if has_cases:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete lawyer: existing cases reference this lawyer",
        )

    db.delete(lawyer)
    db.commit()