from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import (
    create_session_token,
    get_current_user,
    upsert_user,
    verify_google_credential,
)
from ..config import get_settings
from ..database import get_db
from ..models import User
from ..schemas import AuthResponse, DevLoginIn, GoogleLoginIn, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()


@router.get("/config")
def auth_config():
    """Public config the frontend needs to render the login screen."""
    return {
        "google_client_id": settings.google_client_id,
        "google_enabled": bool(settings.google_client_id),
        "dev_login_enabled": settings.allow_dev_login,
    }


@router.post("/google", response_model=AuthResponse)
def google_login(payload: GoogleLoginIn, db: Session = Depends(get_db)):
    claims = verify_google_credential(payload.credential)
    user = upsert_user(
        db,
        email=claims["email"],
        name=claims.get("name", ""),
        picture=claims.get("picture", ""),
        google_sub=claims.get("sub"),
    )
    return AuthResponse(token=create_session_token(user), user=UserOut.model_validate(user))


@router.post("/dev", response_model=AuthResponse)
def dev_login(payload: DevLoginIn, db: Session = Depends(get_db)):
    """Development-only login so the app is usable before Google is configured."""
    if not settings.allow_dev_login:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El login de desarrollo esta deshabilitado.",
        )
    email = payload.email.strip().lower()
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Correo invalido.")
    user = upsert_user(db, email=email, name=payload.name or email.split("@")[0])
    return AuthResponse(token=create_session_token(user), user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)
