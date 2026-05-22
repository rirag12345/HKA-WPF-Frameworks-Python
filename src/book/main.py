"""FastAPI application factory and entry point."""

from pathlib import Path

import uvicorn
from fastapi import FastAPI
from loguru import logger

from book.config import settings
from book.database import SessionLocal, create_tables, reset_tables
from book.repository import BookRepository
from book.router import root_router, router
from book.service import BookSeedService


def seed_startup_books() -> None:
    """Seed demo books once on startup when the database is empty."""
    with SessionLocal() as session:
        inserted = BookSeedService(BookRepository(session)).seed_if_empty(
            amount=5
        )

    if inserted > 0:
        logger.info("Seeded {} demo books with Faker.", inserted)
    else:
        logger.info("Skipped startup seeding because books already exist.")


def create_app() -> FastAPI:
    """Create, configure and return the FastAPI application instance."""
    application = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Register routers first so their entity imports populate Base.metadata
    application.include_router(root_router)
    application.include_router(router)

    # Either reset (drop + recreate) or just ensure tables exist
    if settings.db_reset:
        reset_tables()
        logger.warning("DB_RESET=true – all tables dropped and recreated.")
    else:
        create_tables()
    logger.info("Database tables created / verified.")

    seed_startup_books()

    return application


app = create_app()


def main() -> None:
    """Start the uvicorn ASGI server with hot-reload enabled for development."""
    # Check for SSL certificates
    project_root = Path(__file__).resolve().parents[2]
    cert_path = project_root / "certs" / "cert.pem"
    key_path = project_root / "certs" / "key.pem"

    if cert_path.exists() and key_path.exists():
        ssl_keyfile = str(key_path)
        ssl_certfile = str(cert_path)
        protocol = "https"
        logger.info("SSL certificates found. Starting with TLS/HTTPS.")
    else:
        msg = (
            "SSL certificates required but not found. "
            "Expected: certs/cert.pem and certs/key.pem"
        )
        raise FileNotFoundError(msg)

    logger.info(
        "Starting FastAPI Book Management server on {}://127.0.0.1:8000",
        protocol,
    )
    uvicorn.run(
        "book.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
    )


if __name__ == "__main__":
    main()
