"""Book entity – SQLAlchemy 2.0 mapped class."""

from uuid import UUID, uuid7

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from book.database import Base


class BookEntity(Base):
    """Represents a single book record in the database."""

    __tablename__ = "books"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    title: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255))
    isbn: Mapped[str | None] = mapped_column(
        String(20), unique=True, default=None
    )
    year: Mapped[int | None] = mapped_column(default=None)

    def __eq__(self, other: object) -> bool:
        """Check equality based on the primary key id."""
        if not isinstance(other, BookEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Return hash based on the primary key id."""
        return hash(self.id)

    def __repr__(self) -> str:
        """Return a human-readable string using primitive fields only."""
        return f"BookEntity(id={self.id!r}, title={self.title!r})"
