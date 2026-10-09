from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    POSTGRES_PASSWORD: str
    JWT_SECRET: str
    ENVIRONMENT: str = "development"

    DATABASE_URL: str
    REDIS_URL: str

    MONTE_CARLO_SCENARIOS: int = 1000
    MONTE_CARLO_HORIZON_DAYS: int = 90

    SHADOW_MODE: bool = True

    CONFIDENCE_CEILING_CRITICAL: float = 0.75
    CONFIDENCE_CEILING_NOTIFY: float = 0.50

    MIN_OBSERVATIONS_FOR_HYBRID: int = 3
    MIN_OBSERVATIONS_FOR_OBSERVED: int = 8

    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    max_failed_logins: int = 5
    lockout_minutes: int = 15


@lru_cache
def get_settings() -> Settings:
    return Settings()
