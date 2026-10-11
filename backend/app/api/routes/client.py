from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user, require_role
from app.core.database import get_db
from app.models.case import Case
from app.models.client import Client
from app.models.user import User
from app.schemas.client import ClientCreate, ClientResponse, ClientUpdate

router = APIRouter()


def get_client_for_user(db: Session, client_id: UUID, current_user: User) -> Client:
    """Return the client if it exists AND belongs to the user's firm, else 404."""
    client = db.scalar(select(Client).where(Client.id == client_id))
    if client is None or client.law_firm_id != current_user.law_firm_id:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Lawyer")),
):
    client = Client(
        name=data.name.strip(),
        email=data.email.strip().lower(),
        phone=data.phone.strip(),
        law_firm_id=current_user.law_firm_id,
    )
    db.add(client)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A client with this email or phone already exists",
        )
    db.refresh(client)
    return client


@router.get("/", response_model=list[ClientResponse])
def list_clients(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Client)
        .where(Client.law_firm_id == current_user.law_firm_id)
        .order_by(Client.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return db.scalars(stmt).all()

@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_client_for_user(db, client_id, current_user)


@router.patch("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: UUID,
    data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Lawyer")),
):
    client = get_client_for_user(db, client_id, current_user)

    changes = data.model_dump(exclude_unset=True)
    if changes.get("email") is not None:
        changes["email"] = changes["email"].strip().lower()

    for field, value in changes.items():
        if value is not None:
            setattr(client, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A client with this email or phone already exists",
        )
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner")),
):
    client = get_client_for_user(db, client_id, current_user)

    has_cases = db.scalar(select(Case.id).where(Case.client_id == client_id)) is not None
    if has_cases:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete client: existing cases reference this client",
        )

    db.delete(client)
    db.commit()