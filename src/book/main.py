"""FastAPI application factory and entry point."""

import uvicorn
from fastapi import FastAPI
from loguru import logger

from book.config import settings
from book.database import SessionLocal, create_tables
from book.repository import BookRepository
from book.router import router
from book.service import BookSeedService


def seed_startup_books() -> None:
    """Seed demo books once on startup when the database is empty."""
    with SessionLocal() as session:
        inserted = BookSeedService(BookRepository(session)).seed_if_empty(
            amount=20
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
    application.include_router(router)

    # Create database tables after all entities are imported
    create_tables()
    logger.info("Database tables created / verified.")

    seed_startup_books()

    return application


app = create_app()


def main() -> None:
    """Start the uvicorn ASGI server with hot-reload enabled for development."""
    logger.info(
        "Starting FastAPI Book Management server on http://127.0.0.1:8000"
    )
    uvicorn.run(
        "book.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
