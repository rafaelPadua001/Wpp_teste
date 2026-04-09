from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "WhatsApp SaaS"
    app_env: str = "development"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    database_url: str = "sqlite:///./app.db"
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    rate_limit_enabled: bool = False
    default_message_limit: int = 1000
    whatsapp_access_token: str = "your_access_token_here"
    whatsapp_phone_number_id: str = "your_phone_number_id_here"
    whatsapp_api_version: str = "v19.0"
    whatsapp_base_url: str = "https://graph.facebook.com"
    whatsapp_test_mode: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
