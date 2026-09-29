import uuid
from datetime import datetime

from sqlalchemy import String,DateTime,func,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship

from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.law_firm import LawFirm

class Lawyer(Base):
    __tablename__="lawyers"

    id: Mapped[uuid.UUID] = mapped_column(
    primary_key=True,
    default=uuid.uuid4
    )
    law_firm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("law_firms.id"),
        nullable=False
    )
    law_firm:Mapped["LawFirm"]=relationship(
        back_populates="lawyers"
    )
    name: Mapped[str] = mapped_column(
    String(255),
    nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
