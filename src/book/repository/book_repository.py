"""Book repository – isolates all database access for books."""

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

    def count(self) -> int:
        """Return the total number of stored books."""
        return self._session.query(BookEntity).count()

    def add_many(self, books: list[BookEntity]) -> None:
        """Persist multiple books in one transaction."""
        self._session.add_all(books)
        self._session.commit()
