"""
Closira — Application Configuration

Uses Pydantic BaseSettings to load configuration from environment variables
and the .env file. This provides:
- Type-safe configuration values
- Automatic validation on startup
- A single source of truth for all settings

Why Pydantic BaseSettings instead of raw os.getenv()?
- Validated at startup (fail fast if config is wrong)
- Type coercion (strings become bools, ints, etc.)
- Clean defaults
- Centralized — no scattered os.getenv() calls
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # Application metadata
    APP_NAME: str = "Closira"
    DEBUG: bool = False

    # Database configuration
    # SQLite is file-based, so the URL points to a local file.
    # This can later be swapped to PostgreSQL by changing this single value.
    DATABASE_URL: str = "sqlite:///./closira.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# ---------------------------------------------------------------------------
# Singleton instance
# ---------------------------------------------------------------------------
# We create a single Settings instance that the entire app imports.
# This avoids reading .env multiple times and ensures consistency.
# ---------------------------------------------------------------------------
settings = Settings()
