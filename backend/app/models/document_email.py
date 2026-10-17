import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DocumentEmail(Base):
    """One row each time someone emails a document out of LexFlow (the 'sent log')."""

    __tablename__ = "document_emails"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    # Which document. Kept even if the document is deleted later (then it becomes NULL),
    # so the firm can still see that it was sent.
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True
    )

    case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cases.id"),
        nullable=False
    )

    sent_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    to_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Copy of the file name at sending time (the document itself may be deleted later)
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )