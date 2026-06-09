import logging
import smtplib
import ssl
from email.message import EmailMessage

from .config import get_settings

logger = logging.getLogger("pinad.email")
settings = get_settings()


def _build_message(to_email: str, code: str) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = f"Tu código de verificación (π)NAD: {code}"
    msg["From"] = settings.email_sender
    msg["To"] = to_email
    ttl = settings.verification_code_ttl_minutes
    msg.set_content(
        f"Tu código de verificación para (π)NAD es: {code}\n\n"
        f"Caduca en {ttl} minutos. Si no creaste esta cuenta, ignora este correo."
    )
    msg.add_alternative(
        f"""\
<div style="font-family:Arial,Helvetica,sans-serif;max-width:480px;margin:auto">
  <h2 style="color:#512509;margin-bottom:4px">(π)NAD</h2>
  <p style="color:#3e403d">Tu código de verificación es:</p>
  <div style="font-size:32px;font-weight:700;letter-spacing:8px;color:#936a31;
              background:#f4e0ab;border-radius:12px;padding:16px;text-align:center">
    {code}
  </div>
  <p style="color:#6b6b6b;font-size:13px;margin-top:16px">
    Caduca en {ttl} minutos. Si no creaste esta cuenta, ignora este correo.
  </p>
</div>""",
        subtype="html",
    )
    return msg


def send_verification_email(to_email: str, code: str) -> bool:
    """Send the verification code by email.

    Returns True if the email was actually sent over SMTP. When SMTP is not
    configured, the code is logged instead (handy for local development) and
    this returns False.
    """
    if not settings.smtp_configured:
        logger.warning(
            "SMTP no configurado. Código de verificación para %s: %s", to_email, code
        )
        return False

    msg = _build_message(to_email, code)
    try:
        if settings.smtp_use_tls:
            context = ssl.create_default_context()
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as s:
                s.starttls(context=context)
                s.login(settings.smtp_user, settings.smtp_password)
                s.send_message(msg)
        else:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                settings.smtp_host, settings.smtp_port, context=context, timeout=20
            ) as s:
                s.login(settings.smtp_user, settings.smtp_password)
                s.send_message(msg)
        return True
    except Exception:  # noqa: BLE001 - surface as a logged failure, never crash
        logger.exception("Fallo enviando el correo de verificación a %s", to_email)
        return False
