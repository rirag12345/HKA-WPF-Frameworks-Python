"""Root router – landing endpoint that lists available API routes."""

from fastapi import APIRouter
from pydantic import BaseModel

root_router = APIRouter(tags=["Info"])


class RouteInfo(BaseModel):
    """Describes a single available API route group."""

    path: str
    description: str


class ApiIndex(BaseModel):
    """Response model for the root endpoint."""

    name: str
    version: str
    docs: str
    redoc: str
    routes: list[RouteInfo]


@root_router.get(
    "/",
    summary="API index",
    description="Returns an overview of all available API routes.",
)
def api_index() -> ApiIndex:
    """Return a human-readable index of all available endpoints."""
    return ApiIndex(
        name="FastAPI Book Management",
        version="0.1.0",
        docs="/docs",
        redoc="/redoc",
        routes=[
            RouteInfo(
                path="/books/",
                description="List all books (GET) or create a new one (POST)",
            ),
            RouteInfo(
                path="/books/{book_id}",
                description=(
                    "Retrieve (GET), update (PUT) or delete (DELETE) "
                    "a specific book by UUID"
                ),
            ),
            RouteInfo(
                path="/docs",
                description="Interactive Swagger UI (OpenAPI)",
            ),
            RouteInfo(
                path="/redoc",
                description="ReDoc API documentation",
            ),
        ],
    )
