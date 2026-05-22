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


class BookCreateRequest(BaseModel):
    """Request body for creating a new book."""

    title: str
    author: str
    isbn: str | None = None
    year: int | None = None


class BookService:
    """Orchestrates book-related use cases and converts entities to DTOs."""

    def __init__(self, repository: BookRepository) -> None:
        """Initialize the service with a BookRepository dependency."""
        self._repository = repository

    def get_all_books(self) -> list[BookDTO]:
        """Retrieve every book and return as a list of DTOs."""
        books: list[BookEntity] = self._repository.get_all()
        return [BookDTO.model_validate(book) for book in books]

    def get_book(self, book_id: UUID) -> BookDTO:
        """
        Retrieve a single book by id and return as DTO.

        Raises ValueError if the book does not exist.
        """
        book = self._repository.get_by_id(book_id)
        if book is None:
            msg = f"Book with id {book_id} not found"
            raise ValueError(msg)
        return BookDTO.model_validate(book)

    def create_book(self, request: BookCreateRequest) -> BookDTO:
        """Create and persist a new book, then return it as DTO."""
        book = BookEntity(
            title=request.title,
            author=request.author,
            isbn=request.isbn,
            year=request.year,
        )
        self._repository.add(book)
        return BookDTO.model_validate(book)
