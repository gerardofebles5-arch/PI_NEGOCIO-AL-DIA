from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import require_admin
from ..database import get_db
from ..models import Document, User
from ..schemas import DocumentDetailOut, DocumentOut, ExtractionOut, UserOut

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    result = []
    for u in users:
        doc_count = db.query(Document).filter(Document.owner_id == u.id).count()
        item = UserOut.model_validate(u).model_dump()
        item["document_count"] = doc_count
        result.append(item)
    return result


@router.get("/documents", response_model=list[DocumentDetailOut])
def list_all_documents(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    out: list[DocumentDetailOut] = []
    for doc in docs:
        item = DocumentDetailOut.model_validate(doc)
        if doc.extraction is not None:
            item.extraction = ExtractionOut.model_validate(doc.extraction)
        item.owner_email = doc.owner.email if doc.owner else None
        out.append(item)
    return out


@router.get("/stats")
def admin_stats(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    users = db.query(User).all()
    docs = db.query(Document).all()
    total_amount = 0.0
    for d in docs:
        if d.extraction is not None:
            total_amount += float((d.extraction.fields or {}).get("total_amount") or 0.0)
    return {
        "total_users": len(users),
        "total_admins": sum(1 for u in users if u.role == "admin"),
        "total_documents": len(docs),
        "total_amount": round(total_amount, 2),
    }


@router.get("/users/{user_id}/documents", response_model=list[DocumentOut])
def list_user_documents(
    user_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    docs = (
        db.query(Document)
        .filter(Document.owner_id == user_id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return [DocumentOut.model_validate(d) for d in docs]
