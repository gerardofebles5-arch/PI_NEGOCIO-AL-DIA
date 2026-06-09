from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    role: str
    is_verified: bool
    created_at: datetime


class AuthResponse(BaseModel):
    token: str
    user: UserOut


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = ""


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class VerifyIn(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=12)


class ResendIn(BaseModel):
    email: EmailStr


class RegisterOut(BaseModel):
    email: str
    email_sent: bool
    message: str


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
