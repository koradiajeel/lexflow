from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import create_access_token, hash_password
from app.models.enums import UserRole
from app.models.law_firm import LawFirm
from app.models.user import User
from app.schemas.auth import RegisterRequest


from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_password, create_access_token, decode_access_token

router = APIRouter()

@router.post("/login",response_model=TokenResponse)
def login(
    data:LoginRequest,
    db:Session=Depends(get_db),
):
    user=db.scalar(select(User).where(User.email == data.email))

    if user is None or not verify_password(data.password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect email or password",
        )
    token = create_access_token({
        "sub": str(user.id),
        "law_firm_id": str(user.law_firm_id),
        "role": user.role.value,
    })

    return TokenResponse(access_token=token)

oauth2_scheme = HTTPBearer()
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise credentials_exception

    return user
@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value,
        "law_firm_id": current_user.law_firm_id,
    }
def require_role(*allowed_roles:str):
      def role_checker(current_user:User=Depends(get_current_user))->User:
          if current_user.role.value not in allowed_roles:
              raise HTTPException(
                  status_code=status.HTTP_403_FORBIDDEN,
                  detail="you do not have permission to perform this action",
              )  
          return current_user
      return role_checker

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    firm_email = data.firm_email.strip().lower()
    owner_email = data.owner_email.strip().lower()

    # 1. Friendly 409 if an email is already taken
    if db.execute(select(LawFirm).where(LawFirm.email == firm_email)).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="A firm with this email already exists")
    if db.execute(select(User).where(User.email == owner_email)).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="A user with this email already exists")

    try:
        # 2. Create the firm
        firm = LawFirm(
            name=data.firm_name.strip(),
            email=firm_email,
            phone=data.firm_phone.strip(),
            address=data.firm_address.strip(),
        )
        db.add(firm)
        db.flush()  # sends the INSERT now so firm.id exists, but doesn't commit yet

        # 3. Create the Owner user for that firm
        owner = User(
            law_firm_id=firm.id,
            email=owner_email,
            hashed_password=hash_password(data.password),
            role=UserRole.OWNER,
        )
        db.add(owner)

        # 4. Save both together, or neither
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")

    db.refresh(owner)

    # 5. Log them in straight away
    token = create_access_token({
        "sub": str(owner.id),
        "law_firm_id": str(firm.id),
        "role": owner.role.value,
    })
    return {"access_token": token, "token_type": "bearer"}