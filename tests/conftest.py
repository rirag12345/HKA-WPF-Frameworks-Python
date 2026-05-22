"""Shared pytest fixtures for the test suite."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from book.database import Base, get_session
from book.main import app

# StaticPool forces SQLAlchemy to reuse the same underlying DBAPI connection
# for every checkout.  This is essential for SQLite :memory: databases, where
# every new connection would otherwise get its own isolated, empty database.
_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestingSessionLocal = sessionmaker(
    bind=_test_engine, autocommit=False, autoflush=False
)


def _override_get_session() -> Generator[Session]:
    """Dependency override that provides a test-scoped database session."""
    with _TestingSessionLocal() as session:
        yield session


# Replace the real session dependency with the test one for all tests
app.dependency_overrides[get_session] = _override_get_session


@pytest.fixture
def client() -> Generator[TestClient]:
    """Create all tables, yield a TestClient, then tear down the schema."""
    Base.metadata.create_all(bind=_test_engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture
def db_session(client: TestClient) -> Generator[Session]:  # noqa: ARG001
    """Yield a raw session against the test database (tables already exist)."""
    with _TestingSessionLocal() as session:
        yield session
