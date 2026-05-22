"""Book seeding service for local development startup data."""

from datetime import datetime

from faker import Faker

from book.entity import BookEntity
from book.repository import BookRepository


class BookSeedService:
    """Seeds demo books when the database is still empty."""

    def __init__(self, repository: BookRepository) -> None:
        """Initialize the service with a BookRepository dependency."""
        self._repository = repository
        self._faker = Faker()

    def seed_if_empty(self, amount: int = 5) -> int:
        """Insert demo books if the database is currently empty."""
        if self._repository.count() > 0:
            return 0

        current_year = datetime.now().year
        books = [
            BookEntity(
                title=self._faker.sentence(nb_words=4).rstrip("."),
                author=self._faker.name(),
                isbn=self._faker.unique.numerify(text="978##########"),
                year=self._faker.random_int(min=1950, max=current_year),
            )
            for _ in range(amount)
        ]
        self._repository.add_many(books)
        return amount

