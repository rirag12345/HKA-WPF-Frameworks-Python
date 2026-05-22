"""Book service – business logic and Pydantic DTO conversion."""

from uuid import UUID

from pydantic import BaseModel

from book.entity import BookEntity
from book.repository import BookRepository


class BookDTO(BaseModel):
    """Data Transfer Object representing a book returned to the API consumer."""

    id: UUID
    title: str
    author: str
    isbn: str | None
    year: int | None

    # Allow constructing this DTO directly from a SQLAlchemy ORM instance
    model_config = {"from_attributes": True}


class BookService:
    """Orchestrates book-related use cases and converts entities to DTOs."""

    def __init__(self, repository: BookRepository) -> None:
        """Initialize the service with a BookRepository dependency."""
        self._repository = repository

    def get_all_books(self) -> list[BookDTO]:
        """Retrieve every book and return as a list of DTOs."""
        books: list[BookEntity] = self._repository.get_all()
        return [BookDTO.model_validate(book) for book in books]


