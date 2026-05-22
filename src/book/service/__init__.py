"""Service layer – public API via facade pattern."""

from book.service.book_service import BookDTO, BookService

__all__ = ["BookDTO", "BookService"]
