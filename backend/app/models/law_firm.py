import uuid
from sqlalchemy import String,DateTime,func
from sqlalchemy.orm import Mapped, mapped_column,relationship
from app.core.database import Base
from datetime import datetime
from typing import List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.lawyer import Lawyer

if TYPE_CHECKING:
    from app.models.client import Client

class LawFirm(Base):
    __tablename__ = "law_firms"

    id:Mapped[uuid.UUID]=mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    name:Mapped[str]=mapped_column(
        String(225),
        nullable=False
    )

    email:Mapped[str]=mapped_column(
        String(226),
        unique=True,
        nullable=False
    )

    phone: Mapped[str] = mapped_column(
    String(20),
    nullable=False
    )

    address: Mapped[str] = mapped_column(
    String(500),
    nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
    DateTime,
    server_default=func.now(),
    nullable=False
    )

    lawyers: Mapped[List["Lawyer"]] = relationship(
    back_populates="law_firm",
    cascade="all, delete-orphan"
    )
    clients: Mapped[list["Client"]] = relationship(
    back_populates="law_firm",
    cascade="all, delete-orphan"
    )



