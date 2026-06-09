from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import (
    create_session_token,
    get_current_user,
    hash_password,
    new_verification_code,
    role_for_email,
    verification_expiry,
    verify_password,
)
from ..config import get_settings
from ..database import get_db
from ..email_utils import send_verification_email
from ..models import User
from ..schemas import (
    AuthResponse,
    LoginIn,
    RegisterIn,
    RegisterOut,
    ResendIn,
    UserOut,
    VerifyIn,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()


def _issue_code(db: Session, user: User) -> bool:
    """Generate a fresh verification code, persist it and email it."""
    user.verification_code = new_verification_code()
    user.verification_expires = verification_expiry()
    db.commit()
    return send_verification_email(user.email, user.verification_code)


@router.post("/register", response_model=RegisterOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if user and user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta verificada con este correo. Inicia sesión.",
        )

    if user is None:
        user = User(
            email=email,
            name=payload.name.strip() or email.split("@")[0],
            password_hash=hash_password(payload.password),
            role=role_for_email(email),
            is_verified=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Cuenta sin verificar: actualiza datos y reenvía un código nuevo.
        user.name = payload.name.strip() or user.name
        user.password_hash = hash_password(payload.password)
        user.role = role_for_email(email)
        db.commit()

    sent = _issue_code(db, user)
    message = (
        "Te enviamos un código de verificación a tu correo."
        if sent
        else "Cuenta creada. (SMTP no configurado: revisa los logs del servidor "
        "para el código de verificación.)"
    )
    return RegisterOut(email=user.email, email_sent=sent, message=message)


@router.post("/verify", response_model=AuthResponse)
def verify(payload: VerifyIn, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="No existe una cuenta con este correo.")
    if user.is_verified:
        # Ya verificada: deja iniciar sesión de nuevo emitiendo token.
        return AuthResponse(
            token=create_session_token(user), user=UserOut.model_validate(user)
        )
    if not user.verification_code or user.verification_code != payload.code.strip():
        raise HTTPException(status_code=400, detail="Código incorrecto.")
    if user.verification_expires is None or _expired(user.verification_expires):
        raise HTTPException(
            status_code=400, detail="El código caducó. Solicita uno nuevo."
        )

    user.is_verified = True
    user.verification_code = ""
    user.verification_expires = None
    user.role = role_for_email(email)
    db.commit()
    db.refresh(user)
    return AuthResponse(token=create_session_token(user), user=UserOut.model_validate(user))


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")
    if not user.is_verified:
        _issue_code(db, user)
        raise HTTPException(
            status_code=403,
            detail="Debes verificar tu correo. Te reenviamos un código nuevo.",
        )
    # Mantén el rol alineado con la lista de admins por si cambió.
    new_role = role_for_email(email)
    if user.role != new_role:
        user.role = new_role
        db.commit()
        db.refresh(user)
    return AuthResponse(token=create_session_token(user), user=UserOut.model_validate(user))


@router.post("/resend", response_model=RegisterOut)
def resend(payload: ResendIn, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="No existe una cuenta con este correo.")
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Esta cuenta ya está verificada.")
    sent = _issue_code(db, user)
    message = (
        "Reenviamos el código a tu correo."
        if sent
        else "Código regenerado. Revisa los logs del servidor (SMTP no configurado)."
    )
    return RegisterOut(email=user.email, email_sent=sent, message=message)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)


def _expired(when: datetime) -> bool:
    # Las fechas en SQLite pueden venir sin tzinfo; asume UTC en ese caso.
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) > when
