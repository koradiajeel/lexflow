import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from sqlalchemy import Enum
from app.models.enums import CaseStatus

if TYPE_CHECKING:
    from app.models.client import client
    from app.models.lawyer import lawyer


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id"),
        nullable=False
    )

    lawyer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lawyers.id"),
        nullable=False
    )

    title: Mapped[str] = mapped_column(
    String(255),
    nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )

    status: Mapped[CaseStatus] = mapped_column(
    Enum(CaseStatus),
    nullable=False,
    default=CaseStatus.OPEN
)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )