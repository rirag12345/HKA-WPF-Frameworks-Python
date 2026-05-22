"""Book repository – isolates all database access for books."""

from uuid import UUID

from sqlalchemy.orm import Session

from book.entity import BookEntity


class BookRepository:
    """Handles all raw database operations on BookEntity records."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with an active SQLAlchemy session."""
        self._session = session

    def get_all(self) -> list[BookEntity]:
        """Return every book record currently stored in the database."""
        return list(self._session.query(BookEntity).all())

    def get_by_id(self, book_id: UUID) -> BookEntity | None:
        """Return a single book by id, or None if not found."""
        return (
            self._session.query(BookEntity)
            .filter(BookEntity.id == book_id)
            .first()
        )

    def add(self, book: BookEntity) -> None:
        """Persist a single book and commit the transaction."""
        self._session.add(book)
        self._session.commit()

    def count(self) -> int:
        """Return the total number of stored books."""
        return self._session.query(BookEntity).count()

    def add_many(self, books: list[BookEntity]) -> None:
        """Persist multiple books in one transaction."""
        self._session.add_all(books)
        self._session.commit()

    def exists_by_isbn(self, isbn: str) -> bool:
        """Check if a book with the given ISBN already exists."""
        if isbn is None:
            return False
        return (
            self._session.query(BookEntity)
            .filter(BookEntity.isbn == isbn)
            .first()
            is not None
        )

    def delete_by_id(self, book_id: UUID) -> bool:
        """
        Delete a book by its id.

        Returns True if a book was deleted, False if not found.
        """
        book = (
            self._session.query(BookEntity)
            .filter(BookEntity.id == book_id)
            .first()
        )
        if book is None:
            return False
        self._session.delete(book)
        self._session.commit()
        return True

    def exists_by_isbn_except_id(self, isbn: str, book_id: UUID) -> bool:
        """
        Check if ISBN exists on any book EXCEPT the one with given id.

        Useful for update operations to detect conflicts.
        """
        if isbn is None:
            return False
        return (
            self._session.query(BookEntity)
            .filter(BookEntity.isbn == isbn, BookEntity.id != book_id)
            .first()
            is not None
        )

    def update(
        self,
        book_id: UUID,
        title: str,
        author: str,
        isbn: str | None,
        year: int | None,
    ) -> BookEntity | None:
        """
        Update a book by id with new values.

        Returns the updated BookEntity, or None if not found.
        """
        book = self.get_by_id(book_id)
        if book is None:
            return None
        book.title = title
        book.author = author
        book.isbn = isbn
        book.year = year
        self._session.commit()
        return book
