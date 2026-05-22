"""Application configuration loaded via pydantic-settings."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Central settings class.

    Values can be overridden via environment variables.
    """

    _project_root = Path(__file__).resolve().parents[2]
    database_url: str = f"sqlite:///{(_project_root / 'books.db').as_posix()}"
    app_title: str = "FastAPI Book Management"
    app_version: str = "0.1.0"


# Module-level singleton – import this instance everywhere
settings = Settings()
