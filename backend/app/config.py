from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Auth
    jwt_secret: str = "dev-insecure-secret-change-me"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Comma separated list of admin emails. These users get the ADMIN role.
    admin_emails: str = "gerardofebles5@gmail.com,gfebles@negocioaldia.app"

    # Email verification
    verification_code_ttl_minutes: int = 15

    # SMTP (envío de correos de verificación). 100% gratis con un Gmail
    # y una "contraseña de aplicación". Si se deja vacío, el código de
    # verificación se imprime en los logs (solo útil en desarrollo).
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""  # por defecto usa smtp_user
    smtp_use_tls: bool = True  # STARTTLS (puerto 587). Para 465 ponlo en false.

    # Storage / DB
    database_url: str = "sqlite:///./data/pinad.db"
    upload_dir: str = "./data/uploads"
    max_upload_mb: int = 25

    # CORS (comma separated). "*" allows all origins.
    cors_origins: str = "*"

    @property
    def admin_email_set(self) -> set[str]:
        return {e.strip().lower() for e in self.admin_emails.split(",") if e.strip()}

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def email_sender(self) -> str:
        return self.smtp_from or self.smtp_user

    @property
    def smtp_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_user and self.smtp_password)


@lru_cache
def get_settings() -> Settings:
    return Settings()
