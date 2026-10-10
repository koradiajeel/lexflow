import uuid
from uuid import UUID
from pathlib import Path

from fastapi.responses import FileResponse
from fastapi import File, UploadFile
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.auth import get_current_user
from app.core.database import get_db
from app.models.case import Case
from app.models.document import Document
from app.models.lawyer import Lawyer
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentResponse
from app.services import storage

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
    case = db.scalar(select(Case).where(Case.id == case_id))
    if case is None:
        raise HTTPException(status_code=404, detail="case not found")

    lawyer = db.scalar(select(Lawyer).where(Lawyer.id == case.lawyer_id))
    if lawyer is None or lawyer.law_firm_id != current_user.law_firm_id:
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
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="file is larger than 20 MB",
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

    path = storage.get_file_path(doc.storage_key)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File missing from storage")

    return FileResponse(path, media_type=doc.content_type, filename=doc.filename)


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