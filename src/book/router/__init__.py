"""Router layer – public API via facade pattern."""

from book.router.book_router import router
from book.router.root_router import root_router

__all__ = ["root_router", "router"]
