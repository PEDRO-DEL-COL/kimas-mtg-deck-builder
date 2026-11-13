from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = "development"
    # Local dev uses SQLite. Production uses Supabase Postgres, e.g.
    # postgresql+psycopg://USER:PASSWORD@HOST:5432/postgres
    DATABASE_URL: str = "sqlite:///./kimas.db"
    # Dev-only default; always override via environment in production.
    JWT_SECRET: str = "change-me"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    SCRYFALL_BULK_TYPE: str = "oracle_cards"
    LIGAMAGIC_USER_AGENT: str = (
        "KimasMTGDeckBuilder/0.1 (+https://github.com/PEDRO-DEL-COL/kimas-mtg-deck-builder)"
    )
    LIGAMAGIC_MIN_DELAY_SECONDS: float = 5.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
