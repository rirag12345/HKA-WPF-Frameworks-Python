"""Book router – REST endpoints for the /books resource."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from book.database import get_session
from book.repository import BookRepository
from book.service import BookCreateRequest, BookDTO, BookService

router = APIRouter(prefix="/books", tags=["Books"])


def get_book_service(
    session: Annotated[Session, Depends(get_session)],
) -> BookService:
    """Wire a BookRepository into a BookService for dependency injection."""
    return BookService(BookRepository(session))


@router.get(
    "/",
    summary="List all books",
    status_code=status.HTTP_200_OK,
    description=(
        "Returns a list of every book stored in the database. "
        "An empty list is returned when no books exist yet."
    ),
)
def get_all_books(
    service: Annotated[BookService, Depends(get_book_service)],
) -> list[BookDTO]:
    """Return all books from the database as a JSON array."""
    return service.get_all_books()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book",
    description="Create and persist a new book record in the database.",
    responses={
        201: {"description": "Book created successfully"},
        409: {"description": "A book with this ISBN already exists"},
    },
)
def create_book(
    request: BookCreateRequest,
    service: Annotated[BookService, Depends(get_book_service)],
) -> BookDTO:
    """Create a new book and return the created record with its generated id."""
    try:
        return service.create_book(request)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.get(
    "/{book_id}",
    summary="Retrieve a single book by id",
    status_code=status.HTTP_200_OK,
    description="Returns the book with the given UUID, or 404 if not found.",
    responses={404: {"description": "Book not found"}},
)
def get_book(
    book_id: UUID,
    service: Annotated[BookService, Depends(get_book_service)],
) -> BookDTO:
    """Return a single book identified by its UUID."""
    try:
        return service.get_book(book_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
