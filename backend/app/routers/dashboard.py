from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import Document, User
from ..schemas import DashboardOut, DocumentOut

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

KIND_LABELS = {
    "pdf": "PDF",
    "image": "Imagenes",
    "docx": "Word",
    "pptx": "Presentaciones",
    "sheet": "Hojas de calculo",
    "text": "Texto",
    "other": "Otros",
}


def _build_dashboard(docs: list[Document]) -> DashboardOut:
    by_kind: Counter[str] = Counter()
    currencies: Counter[str] = Counter()
    keyword_counter: Counter[str] = Counter()
    total_amount = 0.0
    total_words = 0
    failed = 0

    for doc in docs:
        by_kind[doc.kind] += 1
        if doc.status == "failed":
            failed += 1
        ext = doc.extraction
        if ext is None:
            continue
        total_words += ext.word_count
        fields = ext.fields or {}
        total_amount += float(fields.get("total_amount") or 0.0)
        for cur, val in (fields.get("currencies") or {}).items():
            currencies[cur] += float(val)
        for kw, count in fields.get("keywords") or []:
            keyword_counter[kw] += count

    recent = sorted(docs, key=lambda d: d.created_at, reverse=True)[:5]

    insights: list[str] = []
    total = len(docs)
    if total == 0:
        insights.append(
            "Aun no has subido documentos. Sube o escanea uno para activar tu dashboard."
        )
    else:
        insights.append(f"Has procesado {total} documento(s) en total.")
        if by_kind:
            top_kind, top_count = by_kind.most_common(1)[0]
            insights.append(
                f"El tipo mas frecuente es {KIND_LABELS.get(top_kind, top_kind)} "
                f"({top_count})."
            )
        if total_amount > 0:
            if currencies:
                detail = ", ".join(
                    f"{round(v, 2):,.2f} {c}" for c, v in currencies.most_common()
                )
                insights.append(f"Montos detectados por moneda: {detail}.")
            else:
                insights.append(
                    f"Suma de montos detectados: {round(total_amount, 2):,.2f}."
                )
        if keyword_counter:
            top_words = ", ".join(w for w, _ in keyword_counter.most_common(5))
            insights.append(f"Temas recurrentes: {top_words}.")
        if failed:
            insights.append(
                f"{failed} documento(s) no se pudieron procesar; revisa el formato."
            )

    return DashboardOut(
        total_documents=total,
        by_kind={KIND_LABELS.get(k, k): v for k, v in by_kind.items()},
        total_amount=round(total_amount, 2),
        currencies={k: round(v, 2) for k, v in currencies.items()},
        total_words=total_words,
        recent=[DocumentOut.model_validate(d) for d in recent],
        insights=insights,
        top_keywords=[[w, c] for w, c in keyword_counter.most_common(10)],
    )


@router.get("", response_model=DashboardOut)
def my_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    docs = db.query(Document).filter(Document.owner_id == user.id).all()
    return _build_dashboard(docs)
