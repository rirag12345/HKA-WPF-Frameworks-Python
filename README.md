# Book Management API (FastAPI + SQLAlchemy)

A lightweight demo backend for managing books with FastAPI,
SQLAlchemy 2.0, and SQLite.

## Highlights

- REST API with OpenAPI/Swagger and ReDoc
- Full CRUD for books (`GET`, `POST`, `PUT`, `DELETE`)
- UUID as primary key
- ISBN stored as `UNIQUE` with validation
- SQLite persistence (`books.db` in the project root)
- Startup seeding with Faker (only when the database is empty)
- Ruff for formatting/linting and Pytest for tests

## Project Structure

```text
src/book/
  entity/      # SQLAlchemy mapped classes
  repository/  # Data access layer
  service/     # Business logic + DTOs
  router/      # FastAPI routes / REST endpoints
```

## Requirements

- Python `>= 3.14`
- `uv` installed

## Quick Start

### 1) Install dependencies

```bash
uv sync
```

### 2) Generate TLS certificates for development

At the moment, `uv run book` expects certificates at:
`certs/cert.pem` and `certs/key.pem`.

```bash
mkdir -p certs
openssl req -x509 -newkey rsa:4096 -nodes \
  -out certs/cert.pem -keyout certs/key.pem \
  -days 30 -subj "/CN=localhost"
```

> Note: `certs/key.pem` is private and should never be committed to Git.

### 3) Start the server

```bash
uv run book
```

Development URLs:

- `https://127.0.0.1:8000`
- Swagger UI: `https://127.0.0.1:8000/docs`
- ReDoc: `https://127.0.0.1:8000/redoc`

With self-signed certificates, your browser will show a security warning.
This is expected for local development.

## API Overview

- `GET /books/` - list all books
- `GET /books/{book_id}` - get one book
- `POST /books/` - create a book
- `PUT /books/{book_id}` - fully update a book
- `DELETE /books/{book_id}` - delete a book

## Example Requests (self-signed TLS)

Use `curl -k` to ignore the local certificate warning.

```bash
curl -k https://127.0.0.1:8000/books/
```

```bash
curl -k -X POST https://127.0.0.1:8000/books/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Architecture",
    "author": "Robert C. Martin",
    "isbn": "978-0134494166",
    "year": 2017
  }'
```

## Quality Checks

```bash
uvx ruff format src tests
uvx ruff check src tests
uv run pytest
uvx ty check src tests
```

## Important Notes

- ISBN is `UNIQUE` in the database.
- Invalid ISBN formats are rejected with `422`.
- Duplicates (for example same ISBN) return `409 Conflict`.
- Startup seeding only inserts demo books when the database is empty.

## License

See `LICENSE`.
