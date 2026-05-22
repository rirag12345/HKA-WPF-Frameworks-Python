"""SQLAlchemy engine, session factory and declarative base."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from book.config import settings


class Base(DeclarativeBase):
    """Declarative base class shared by all SQLAlchemy entities."""


# allow multithreaded access from the same connection (SQLite-specific)
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session; auto-closes after the request finishes."""
    with SessionLocal() as session:
        yield session


def create_tables() -> None:
    """Create all tables registered with Base if they do not yet exist."""
    Base.metadata.create_all(bind=engine)
