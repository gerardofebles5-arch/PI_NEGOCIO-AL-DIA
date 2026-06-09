import os
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..config import get_settings
from ..database import get_db
from ..extraction import detect_fields, extract_text
from ..models import Document, Extraction, User
from ..schemas import DocumentDetailOut, DocumentOut, ExtractionOut

router = APIRouter(prefix="/api/documents", tags=["documents"])
settings = get_settings()


def _doc_detail(doc: Document, include_owner: bool = False) -> DocumentDetailOut:
    out = DocumentDetailOut.model_validate(doc)
    if doc.extraction is not None:
        out.extraction = ExtractionOut.model_validate(doc.extraction)
    if include_owner and doc.owner is not None:
        out.owner_email = doc.owner.email
    return out


@router.post("", response_model=DocumentDetailOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    source: str = Form("upload"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el limite de {settings.max_upload_mb} MB.",
        )
    if not data:
        raise HTTPException(status_code=400, detail="El archivo esta vacio.")

    os.makedirs(settings.upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1]
    stored_name = f"{uuid.uuid4().hex}{ext}"
    stored_path = os.path.join(settings.upload_dir, stored_name)
    with open(stored_path, "wb") as fh:
        fh.write(data)

    doc = Document(
        owner_id=user.id,
        filename=file.filename or stored_name,
        stored_path=stored_path,
        content_type=file.content_type or "",
        size_bytes=len(data),
        source="camera" if source == "camera" else "upload",
    )

    try:
        kind, text = extract_text(file.filename or "", file.content_type or "", data)
        doc.kind = kind
        fields = detect_fields(text)
        doc.status = "processed"
        db.add(doc)
        db.flush()
        extraction = Extraction(
            document_id=doc.id,
            raw_text=text,
            word_count=len(text.split()),
            fields=fields,
        )
        db.add(extraction)
        db.commit()
        db.refresh(doc)
    except Exception as exc:  # noqa: BLE001 - keep the document, record the failure
        doc.status = "failed"
        doc.error = str(exc)[:500]
        db.add(doc)
        db.commit()
        db.refresh(doc)
    return _doc_detail(doc)


@router.get("", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    docs = (
        db.query(Document)
        .filter(Document.owner_id == user.id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return [DocumentOut.model_validate(d) for d in docs]


def _get_owned_or_admin(doc_id: int, db: Session, user: User) -> Document:
    doc = db.get(Document, doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado.")
    if doc.owner_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes acceso a este documento.")
    return doc


@router.get("/{doc_id}", response_model=DocumentDetailOut)
def get_document(
    doc_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    doc = _get_owned_or_admin(doc_id, db, user)
    return _doc_detail(doc, include_owner=user.role == "admin")


@router.get("/{doc_id}/file")
def download_document(
    doc_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    doc = _get_owned_or_admin(doc_id, db, user)
    if not doc.stored_path or not os.path.exists(doc.stored_path):
        raise HTTPException(status_code=404, detail="Archivo no disponible.")
    return FileResponse(
        doc.stored_path,
        media_type=doc.content_type or "application/octet-stream",
        filename=doc.filename,
    )


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    doc_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    doc = _get_owned_or_admin(doc_id, db, user)
    if doc.stored_path and os.path.exists(doc.stored_path):
        try:
            os.remove(doc.stored_path)
        except OSError:
            pass
    db.delete(doc)
    db.commit()
