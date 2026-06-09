from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    picture: str
    role: str
    created_at: datetime


class AuthResponse(BaseModel):
    token: str
    user: UserOut


class GoogleLoginIn(BaseModel):
    credential: str  # Google ID token (JWT) from Google Identity Services


class DevLoginIn(BaseModel):
    email: str
    name: str = ""


class ExtractionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    raw_text: str
    word_count: int
    fields: dict


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    content_type: str
    kind: str
    size_bytes: int
    status: str
    source: str
    error: str
    created_at: datetime


class DocumentDetailOut(DocumentOut):
    extraction: ExtractionOut | None = None
    owner_email: str | None = None


class DashboardOut(BaseModel):
    total_documents: int
    by_kind: dict[str, int]
    total_amount: float
    currencies: dict[str, float]
    total_words: int
    recent: list[DocumentOut]
    insights: list[str]
    top_keywords: list[list]  # [keyword, count]
