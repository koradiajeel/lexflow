import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String,DateTime,Enum,ForeignKey,func
from sqlalchemy.orm import Mapped,mapped_column,relationship

from app.core.database  import Base
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.law_firm import LawFirm

class User(Base):
    __tablename__="users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    law_firm_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("law_firms.id"),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.STAFF
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    law_firm: Mapped["LawFirm"] = relationship()


