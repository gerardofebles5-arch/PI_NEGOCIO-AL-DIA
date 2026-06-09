from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Auth
    google_client_id: str = ""
    jwt_secret: str = "dev-insecure-secret-change-me"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Allow a development login when no Google client id is configured.
    allow_dev_login: bool = True

    # Comma separated list of admin emails. These users get the ADMIN role.
    admin_emails: str = "gerardofebles5@gmail.com,gfebles@negocioaldia.app"

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
