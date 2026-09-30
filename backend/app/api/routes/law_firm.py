from fastapi import APIRouter, Depends,status,HTTPException

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

    
from app.models.law_firm import LawFirm
from app.models.lawyer import Lawyer
from app.core.database import get_db
from app.schemas.law_firm import LawFirmCreate, LawFirmResponse
from app.models.client import Client
from app.models.case import Case

from uuid import UUID
import uuid

router = APIRouter()

@router.post(
    "/",
    response_model=LawFirmResponse,
    status_code=status.HTTP_201_CREATED,
)
def creat_law_firm(
    data:LawFirmCreate,
    db:Session=Depends(get_db),
):
    law_firm = LawFirm(
    name=data.name,
    email=data.email,
    phone=data.phone,
    address=data.address,
)
    try:
        db.add(law_firm)
        db.commit()
        db.refresh(law_firm)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="lawfarm with this email already exists"
        )

    return law_firm
@router.get("/{law_firm_id}",response_model=LawFirmResponse)
def get_law_firm(
    law_firm_id :UUID,
    db:Session=Depends(get_db),

):
    stmt=select(LawFirm).where(LawFirm.id == law_firm_id)

    law_firm=db.scalar(stmt)

    if law_firm is None:
        raise HTTPException(status_code=404 , detail= "law firm is not found")

    return law_firm 
@router.get("/",response_model=list[LawFirmResponse])   
def get_law_firm(
        db:Session=Depends(get_db)
 ):
    law_firms= db.query(LawFirm).all()

    return  law_firms 

@router.get("/{law_firm_id}/lawyers")
def get_law_firm_lawyers(
    law_firm_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    lawyers = db.query(Lawyer).filter(
        Lawyer.law_firm_id == law_firm_id
    ).all()

    return lawyers

@router.delete("/{law_firm_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_law_firm(
    law_firm_id:UUID,
    db:Session=Depends(get_db),
):
    stmt=select(LawFirm).where(LawFirm.id==law_firm_id)
    law_firm=db.scalar(stmt)

    if law_firm is None:
        raise HTTPException(status_code=404,detail="law firm is not found")

    has_cases=db.scalar(
        select(Case.id)
        .join(Lawyer,Case.lawyer_id ==Lawyer.id)
        .where(Lawyer.law_firm_id==law_firm_id)
    )is not None

    if has_cases:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="cannot delete law firm: it has lawyers or clients with existing cases"
        )
    db.delete(law_firm)
    db.commit()
    return