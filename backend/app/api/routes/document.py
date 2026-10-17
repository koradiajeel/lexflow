import smtplib
import uuid
from pathlib import Path
from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user, require_role
from app.core.database import get_db
from app.models.case import Case
from app.models.document import Document
from app.models.document_email import DocumentEmail
from app.models.law_firm import LawFirm
from app.models.lawyer import Lawyer
from app.models.user import User
from app.schemas.document import (
    DocumentCreate,
    DocumentEmailRequest,
    DocumentEmailResponse,
    DocumentResponse,
)
from app.services import email as email_service
from app.services import storage
from app.services.case_access import user_can_see_case
from app.services.file_validation import content_matches_type

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


router = APIRouter()


def get_case_for_user(db: Session, case_id: UUID, current_user: User) -> Case:
    """Return the case if this user may see it (same firm; a Lawyer only their own cases), else 404."""
    case = db.scalar(select(Case).where(Case.id == case_id))
    if case is None or not user_can_see_case(db, case, current_user):
        raise HTTPException(status_code=404, detail="case not found")
    return case


@router.post(
    "/cases/{case_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    case_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = get_case_for_user(db, case_id, current_user)

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="only PDF, PNG, JPEG and Word files are allowed",
        )

    content = file.file.read(MAX_FILE_SIZE + 1)
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="file is empty")
    if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="file is larger than 20 MB",
        )

    # NEW: check the real bytes match the claimed type
    if not content_matches_type(content, file.content_type):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="file content does not match its type",
        )

    storage_key = f"cases/{case.id}/{uuid.uuid4()}"
    storage.save_file(storage_key, content)

    document = Document(
        case_id=case.id,
        uploaded_by=current_user.id,
        filename=Path(file.filename or "unnamed").name[:255],
        content_type=file.content_type,
        size=len(content),
        storage_key=storage_key,
    )
    db.add(document)
    try:
        db.commit()
    except Exception:
        db.rollback()
        storage.delete_file(storage_key)
        raise
    db.refresh(document)
    return document

@router.get(
    "/cases/{case_id}/documents",
    response_model=list[DocumentResponse],
)
def list_case_documents(
    case_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = get_case_for_user(db, case_id, current_user)

    documents = db.scalars(
        select(Document)
        .where(Document.case_id == case.id)
        .order_by(Document.created_at.desc())
    ).all()
    return documents


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = db.scalar(select(Document).where(Document.id == document_id))
    if document is None:
        raise HTTPException(status_code=404, detail="document not found")

    get_case_for_user(db, document.case_id, current_user)
    return document


@router.get("/documents/{document_id}/download")
def download_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.execute(select(Document).where(Document.id == document_id)).scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # firm check: reuses your helper, which 404s on a cross-firm case
    get_case_for_user(db, doc.case_id, current_user)

    # Works the same for local files and S3: the backend reads the file and sends it on,
    # so the bucket stays private and the frontend keeps using its login token.
    content = storage.read_file(doc.storage_key)
    if content is None:
        raise HTTPException(status_code=404, detail="File missing from storage")

    return Response(
        content=content,
        media_type=doc.content_type,
        headers={"Content-Disposition": f"attachment; filename*=utf-8''{quote(doc.filename)}"},
    )



@router.delete("/documents/{document_id}", status_code=204)
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Lawyer")),
):
    doc = db.execute(select(Document).where(Document.id == document_id)).scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    get_case_for_user(db, doc.case_id, current_user)

    storage_key = doc.storage_key
    db.delete(doc)
    db.commit()
    storage.delete_file(storage_key)



def _one_line(text: str) -> str:
    """Remove line breaks and extra spaces (names go into email headers)."""
    return " ".join(text.split())


@router.post("/documents/{document_id}/email", response_model=DocumentEmailResponse)
def email_document(
    document_id: uuid.UUID,
    data: DocumentEmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Lawyer")),
):
    doc = db.scalar(select(Document).where(Document.id == document_id))
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Same rule as viewing/downloading: own firm, and a Lawyer only their own cases.
    get_case_for_user(db, doc.case_id, current_user)

    if doc.size > email_service.MAX_ATTACHMENT_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="This file is too large to email (max 18 MB). Download it and share it another way.",
        )

    content = storage.read_file(doc.storage_key)
    if content is None:
        raise HTTPException(status_code=404, detail="File missing from storage")

    # Who is sending: their lawyer name if they have one, otherwise their login email.
    lawyer = db.scalar(select(Lawyer).where(Lawyer.user_id == current_user.id))
    firm = db.scalar(select(LawFirm).where(LawFirm.id == current_user.law_firm_id))
    sender = _one_line(lawyer.name if lawyer else current_user.email)
    firm_name = _one_line(firm.name)
    filename = _one_line(doc.filename)

    note = data.message.strip()
    body = (
        (note + "\n\n" if note else "")
        + f"{sender}\n{firm_name}\n\n"
        + f"Attached: {filename}\n"
        + f"To reply, just answer this email - it goes to {current_user.email}.\n\n"
        + "Sent with LexFlow"
    )

    msg = email_service.build_message(
        to=str(data.to),
        subject=f'{sender} shared "{filename}" with you',
        body=body,
        from_name=f"{sender} ({firm_name}) via LexFlow",
        reply_to=current_user.email,
        attachment=(filename, content, doc.content_type),
    )

    try:
        email_service.send_message(msg)
    except email_service.EmailNotConfigured:
        raise HTTPException(status_code=503, detail="Email is not set up on this server")
    except (smtplib.SMTPException, OSError):
        raise HTTPException(status_code=502, detail="Could not send the email. Please try again.")

    # Sent: write it in the sent log.
    db.add(DocumentEmail(
        document_id=doc.id,
        case_id=doc.case_id,
        sent_by=current_user.id,
        to_email=str(data.to),
        filename=doc.filename,
    ))
    db.commit()

    return DocumentEmailResponse(sent_to=str(data.to), filename=doc.filename)