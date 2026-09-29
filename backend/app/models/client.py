import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String,ForeignKey, func
from sqlalchemy.orm  import mapped_column,Mapped,relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.law_firm import LawFirm

class Client(Base):

    __tablename__="clients"

    id: Mapped[uuid.UUID] = mapped_column(
            primary_key=True,
            default=uuid.uuid4
        )

    law_firm_id:Mapped[uuid.UUID]=mapped_column(
        ForeignKey("law_firms.id"),
        nullable=False
    )

    name:Mapped[str]=mapped_column(
        String(225),
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

    law_firm: Mapped["LawFirm"] = relationship(
        back_populates="clients"
    )

    