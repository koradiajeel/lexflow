from fastapi import APIRouter, Depends, HTTPException, status , Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.routes.auth import require_role
from app.core.database import get_db
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.get("/", response_model=list[UserResponse])
def list_users(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner")),
):
    stmt = (
        select(User)
        .where(User.law_firm_id == current_user.law_firm_id)
        .order_by(User.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return db.scalars(stmt).all()



@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner")),
):
    email = data.email.strip().lower()

    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user with this email already exists",
        )

    user = User(
        law_firm_id=current_user.law_firm_id,
        email=email,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user with this email already exists",
        )

    db.refresh(user)
    return user
