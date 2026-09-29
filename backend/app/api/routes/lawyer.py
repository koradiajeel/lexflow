from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID

from app.core.database import get_db
from app.models.lawyer import Lawyer
from app.schemas.lawyer import LawyerResponse, LawyerCreate,LawyerUpdate
router =APIRouter()

@router.post("/",
             response_model=LawyerResponse,
             status_code=status.HTTP_201_CREATED,
             )
def create_lawyer(
    data:LawyerCreate,
    db:Session=Depends(get_db),
):
    lawyer=Lawyer(
        name=data.name,
        email=data.email,
        phone=data.phone,
        law_firm_id=data.law_firm_id,

    )
    db.add(lawyer)
    db.commit()
    db.refresh(lawyer)

    return lawyer

@router.get("/{lawyer_id}",response_model=LawyerResponse)
def get_lawyer(
    lawyer_id:UUID,
    db:Session=Depends(get_db),

):
    stmt=select(Lawyer).where(Lawyer.id==lawyer_id)
    lawyer=db.scalar(stmt)
    if lawyer is None:
        raise HTTPException(
            status_code=404,
            detail="laywer not found"
        )
    return lawyer

@router.patch("/{lawyer_id}",response_model=LawyerResponse)
def update_lawyer(
    lawyer_id: UUID,
    data:LawyerUpdate,
    db:Session=Depends(get_db),

):
    stmt=select(Lawyer).where(Lawyer.id == lawyer_id)
    lawyer=db.scalar(stmt)

    if lawyer is None:
        raise HTTPException(
            status_code=404,
            detail="lawyer not found"
        )
    if data.name is not None:
        lawyer.name=data.name

    if data.email is not None:
        lawyer.email=data.email

    if data.phone is not None:
        lawyer.phone=data.phone

    db.commit()
    db.refresh(lawyer)

    return lawyer

@router.delete("/{lawyer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lawyer(
    lawyer_id: UUID,
    db: Session = Depends(get_db),
):
        stmt = select(Lawyer).where(Lawyer.id == lawyer_id)
        lawyer = db.scalar(stmt)

        if lawyer is None:
            raise HTTPException(
                status_code=404,
                detail="Lawyer not found"
            )

        db.delete(lawyer)
        db.commit()

        return