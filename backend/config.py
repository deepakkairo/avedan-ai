"""
config.py – AVEDAN AI Application Configuration
================================================
Loads all environment variables via Pydantic Settings.
Import `settings` from this module throughout the app.

CRITICAL POLICIES ENFORCED:
  1. DigiLocker Direct API Integration is OPTIONAL and DISABLED by default
     until official partner credentials and MeitY approval are configured.
  2. Zero Payment Gateway Policy: AVEDAN never routes government fees through
     its own accounts. No third-party payment gateways (e.g. Razorpay) are configured.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central settings object loaded from .env file with safe defaults.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────────────────────
    app_name: str = "AVEDAN AI"
    app_version: str = "1.0.0"
    environment: str = "development"
    log_level: str = "INFO"

    # ── OpenAI / LLM (Optional for RAG / Chat) ───────────────────────────────
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    # ── DigiLocker Direct API Integration (OPTIONAL & DISABLED BY DEFAULT) ───
    # In accordance with compliance requirements, direct DigiLocker integration
    # must remain disabled until official partner approval, credentials, consent
    # handling, and secure backend implementation are formally certified.
    digilocker_integration_enabled: bool = False
    digilocker_partner_status: str = "pending_approval"  # 'pending_approval' | 'active' | 'disabled'
    digilocker_client_id: str = ""
    digilocker_client_secret: str = ""
    digilocker_redirect_uri: str = "http://localhost:8000/api/digilocker/callback"

    # Official DigiLocker API endpoints
    digilocker_auth_url: str = "https://api.digitallocker.gov.in/public/oauth2/1/authorize"
    digilocker_token_url: str = "https://api.digitallocker.gov.in/public/oauth2/1/token"
    digilocker_profile_url: str = "https://api.digitallocker.gov.in/public/oauth2/1/userinfo"
    digilocker_files_url: str = "https://api.digitallocker.gov.in/public/oauth2/1/files"

    # ── Database ─────────────────────────────────────────────────────────────
    # Default to local SQLite for rapid, lightweight setup; supports PostgreSQL in production
    database_url: str = "sqlite:///./avedan.db"

    # ── Security & Authentication ─────────────────────────────────────────────
    secret_key: str = "avedan_development_secret_key_must_be_overridden_in_production_32chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # ── CORS / Frontend ───────────────────────────────────────────────────────
    frontend_url: str = "http://localhost:5173"

    # ── PDF Storage ───────────────────────────────────────────────────────────
    pdf_storage_dir: str = "./tmp/applications"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    """
    return Settings()


# Module-level convenience alias
settings = get_settings()
