"""Application configuration loaded via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Central settings class.

    Values can be overridden via environment variables.
    """

    database_url: str = "sqlite:///./books.db"
    app_title: str = "FastAPI Book Management"
    app_version: str = "0.1.0"


# Module-level singleton – import this instance everywhere
settings = Settings()
