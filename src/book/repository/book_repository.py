"""Book repository – isolates all database access for books."""

from typing import Annotated

from sqlalchemy.orm import Session

from book.database import get_session
from book.entity import BookEntity


class BookRepository:
    """Handles all raw database operations on BookEntity records."""

    def __init__(self, session: Annotated[Session, get_session()]) -> None:
        """Initialize the repository with an active SQLAlchemy session."""
        self._session = session

    def get_all(self) -> list[BookEntity]:
        """Return every book record currently stored in the database."""
        return list(self._session.query(BookEntity).all())

