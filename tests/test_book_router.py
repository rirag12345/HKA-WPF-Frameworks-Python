"""Integration tests for GET /books/ endpoint."""

from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from book.entity import BookEntity


def _insert_book(session: Session, title: str, author: str) -> UUID:
    """Insert a BookEntity via the session and return its id."""
    book = BookEntity(title=title, author=author)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book.id


class TestGetAllBooks:
    """Tests for the GET /books/ endpoint."""

    def test_returns_empty_list_when_no_books_exist(
        self, client: TestClient
    ) -> None:
        """A fresh database must return an empty JSON array."""
        response = client.get("/books/")

        assert response.status_code == 200
        assert response.json() == []

    def test_returns_all_books(
        self, client: TestClient, db_session: Session
    ) -> None:
        """All books inserted into the DB must appear in the response."""
        _insert_book(db_session, "Clean Code", "Robert C. Martin")
        _insert_book(db_session, "The Pragmatic Programmer", "David Thomas")

        response = client.get("/books/")
        data = response.json()

        assert response.status_code == 200
        assert len(data) == 2
        titles = {book["title"] for book in data}
        assert titles == {"Clean Code", "The Pragmatic Programmer"}

    def test_book_response_contains_expected_fields(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Each book object in the response must contain all DTO fields."""
        _insert_book(db_session, "Refactoring", "Martin Fowler")

        response = client.get("/books/")
        book = response.json()[0]

        assert "id" in book
        assert "title" in book
        assert "author" in book
        assert "isbn" in book
        assert "year" in book

    def test_book_id_is_valid_uuid(
        self, client: TestClient, db_session: Session
    ) -> None:
        """The id field returned by the API must be a valid UUID string."""
        _insert_book(db_session, "Domain-Driven Design", "Eric Evans")

        response = client.get("/books/")
        raw_id = response.json()[0]["id"]

        # Raises ValueError if the string is not a valid UUID
        parsed = UUID(raw_id)
        assert str(parsed) == raw_id


class TestGetBook:
    """Tests for the GET /books/{book_id} endpoint."""

    def test_returns_single_book_by_id(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Fetching a book by its UUID must return that book."""
        book_id = _insert_book(db_session, "Patterns of EAA", "Martin Fowler")

        response = client.get(f"/books/{book_id}")
        data = response.json()

        assert response.status_code == 200
        assert data["id"] == str(book_id)
        assert data["title"] == "Patterns of EAA"
        assert data["author"] == "Martin Fowler"

    def test_returns_404_for_nonexistent_book(self, client: TestClient) -> None:
        """Fetching a non-existent book by UUID must return 404."""
        fake_id = UUID("12345678-1234-5678-1234-567812345678")

        response = client.get(f"/books/{fake_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_single_book_contains_all_dto_fields(
        self, client: TestClient, db_session: Session
    ) -> None:
        """A single book response must include all DTO fields."""
        book_id = _insert_book(db_session, "Test Book", "Test Author")

        response = client.get(f"/books/{book_id}")
        book = response.json()

        assert "id" in book
        assert "title" in book
        assert "author" in book
        assert "isbn" in book
        assert "year" in book


class TestCreateBook:
    """Tests for the POST /books/ endpoint."""

    def test_creates_book_successfully(self, client: TestClient) -> None:
        """Creating a book with required fields must return 201."""
        payload = {
            "title": "Clean Architecture",
            "author": "Robert C. Martin",
        }

        response = client.post("/books/", json=payload)
        data = response.json()

        assert response.status_code == 201
        assert data["title"] == "Clean Architecture"
        assert data["author"] == "Robert C. Martin"
        assert "id" in data
        assert UUID(data["id"])  # Verify it's a valid UUID

    def test_creates_book_with_all_fields(self, client: TestClient) -> None:
        """Creating a book with all fields must persist them."""
        payload = {
            "title": "The Mythical Man-Month",
            "author": "Frederick Brooks",
            "isbn": "978-0201633610",
            "year": 1975,
        }

        response = client.post("/books/", json=payload)
        data = response.json()

        assert response.status_code == 201
        assert data["title"] == "The Mythical Man-Month"
        assert data["author"] == "Frederick Brooks"
        assert data["isbn"] == "978-0201633610"
        assert data["year"] == 1975

    def test_creates_book_with_optional_fields_null(
        self, client: TestClient
    ) -> None:
        """Creating a book without optional fields must set them to null."""
        payload = {
            "title": "Working Effectively with Legacy Code",
            "author": "Michael Feathers",
        }

        response = client.post("/books/", json=payload)
        data = response.json()

        assert response.status_code == 201
        assert data["isbn"] is None
        assert data["year"] is None

    def test_persists_book_to_database(
        self, client: TestClient, db_session: Session
    ) -> None:
        """A book created via POST must appear in subsequent GET requests."""
        payload = {
            "title": "Code Complete",
            "author": "Steve McConnell",
        }

        response = client.post("/books/", json=payload)
        created_id = response.json()["id"]

        # Fetch the created book via GET
        get_response = client.get(f"/books/{created_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Code Complete"

    def test_rejects_duplicate_isbn(self, client: TestClient) -> None:
        """Creating a book with a duplicate ISBN must return 409 Conflict."""
        # Create first book with ISBN
        first_payload = {
            "title": "Software Architecture",
            "author": "Neal Ford",
            "isbn": "978-0134494167",
        }
        first_response = client.post("/books/", json=first_payload)
        assert first_response.status_code == 201

        # Try to create another book with the same ISBN
        second_payload = {
            "title": "Different Title",
            "author": "Different Author",
            "isbn": "978-0134494167",
        }
        second_response = client.post("/books/", json=second_payload)

        assert second_response.status_code == 409
        assert "already exists" in second_response.json()["detail"].lower()


class TestDeleteBook:
    """Tests for the DELETE /books/{book_id} endpoint."""

    def test_deletes_book_successfully(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Deleting an existing book by UUID must return 204 No Content."""
        book_id = _insert_book(db_session, "Test Deletion", "Author")

        response = client.delete(f"/books/{book_id}")

        assert response.status_code == 204
        assert response.content == b""

    def test_returns_404_for_nonexistent_book_delete(
        self, client: TestClient
    ) -> None:
        """Deleting a non-existent book by UUID must return 404."""
        fake_id = UUID("12345678-1234-5678-1234-567812345678")

        response = client.delete(f"/books/{fake_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_book_is_removed_from_database(
        self, client: TestClient, db_session: Session
    ) -> None:
        """After deletion, the book should no longer exist in the database."""
        book_id = _insert_book(db_session, "Remove Me", "Author")

        # Verify it exists
        get_response = client.get(f"/books/{book_id}")
        assert get_response.status_code == 200

        # Delete it
        delete_response = client.delete(f"/books/{book_id}")
        assert delete_response.status_code == 204

        # Verify it's gone
        get_after_delete = client.get(f"/books/{book_id}")
        assert get_after_delete.status_code == 404
