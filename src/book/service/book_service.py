"""Book service – business logic and Pydantic DTO conversion."""

import re
from uuid import UUID

from pydantic import BaseModel, field_validator

from book.entity import BookEntity
from book.repository import BookRepository


def validate_isbn(isbn: str | None) -> str | None:
    """
    Validate ISBN format.

    Accepts ISBN-13 (13 digits, starting with 978 or 979) or
    ISBN-10 (10 digits). Returns the ISBN if valid, raises ValueError
    if invalid format.
    """
    if isbn is None or isbn == "":
        return None

    # Remove common separators (hyphens, spaces)
    clean_isbn = isbn.replace("-", "").replace(" ", "").strip()

    # ISBN-13: 13 digits, must start with 978 or 979
    if len(clean_isbn) == 13:
        if not re.match(r"^(978|979)\d{10}$", clean_isbn):
            msg = (
                f"Invalid ISBN-13 format: {isbn}. "
                "Must be 13 digits starting with 978 or 979"
            )
            raise ValueError(msg)
        return clean_isbn

    # ISBN-10: 10 digits or 9 digits + X
    if len(clean_isbn) == 10:
        if not re.match(r"^\d{9}[\dX]$", clean_isbn.upper()):
            msg = (
                f"Invalid ISBN-10 format: {isbn}. "
                "Must be 10 digits (last can be X)"
            )
            raise ValueError(msg)
        return clean_isbn.upper()

    msg = f"Invalid ISBN format: {isbn}. Must be 10 or 13 digits"
    raise ValueError(msg)


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

    @field_validator("isbn", mode="before")
    @classmethod
    def validate_isbn_field(cls, v: str | None) -> str | None:
        """Validate ISBN format when provided."""
        return validate_isbn(v)


class BookUpdateRequest(BaseModel):
    """Request body for updating an existing book."""

    title: str
    author: str
    isbn: str | None = None
    year: int | None = None

    @field_validator("isbn", mode="before")
    @classmethod
    def validate_isbn_field(cls, v: str | None) -> str | None:
        """Validate ISBN format when provided."""
        return validate_isbn(v)


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
        """
        Create and persist a new book, then return it as DTO.

        Raises ValueError if a book with the same ISBN already exists.
        """
        # Check for duplicate ISBN if provided
        if request.isbn and self._repository.exists_by_isbn(request.isbn):
            msg = f"A book with ISBN {request.isbn} already exists"
            raise ValueError(msg)

        book = BookEntity(
            title=request.title,
            author=request.author,
            isbn=request.isbn,
            year=request.year,
        )
        self._repository.add(book)
        return BookDTO.model_validate(book)

    def delete_book(self, book_id: UUID) -> None:
        """
        Delete a book by its id.

        Raises ValueError if the book does not exist.
        """
        deleted = self._repository.delete_by_id(book_id)
        if not deleted:
            msg = f"Book with id {book_id} not found"
            raise ValueError(msg)

    def update_book(self, book_id: UUID, request: BookUpdateRequest) -> BookDTO:
        """
        Update an existing book with new values.

        Raises ValueError if book not found or ISBN is duplicate.
        """
        # Check if book exists
        existing_book = self._repository.get_by_id(book_id)
        if existing_book is None:
            msg = f"Book with id {book_id} not found"
            raise ValueError(msg)

        # Check for duplicate ISBN (excluding this book itself)
        if request.isbn and self._repository.exists_by_isbn_except_id(
            request.isbn, book_id
        ):
            msg = f"A book with ISBN {request.isbn} already exists"
            raise ValueError(msg)

        updated_book = self._repository.update(
            book_id, request.title, request.author, request.isbn, request.year
        )
        return BookDTO.model_validate(updated_book)
