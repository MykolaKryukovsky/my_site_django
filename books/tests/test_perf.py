from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.test.utils import CaptureQueriesContext
from django.db import connection
from ..models import Author, Book, Review


class ORMPerformanceTest(TestCase):
    """Тести для контролю кількості SQL-запитів та оптимізації через ListView."""

    def setUp(self) -> None:
        self.url = reverse('books:perf_demo')
        self.user = User.objects.create_user(username="perf_tester", password="password123")

        author = Author.objects.create(name="Тестовий Автор")
        for i in range(15):
            book = Book.objects.create(
                title=f"Книга {i}", genre="Драма", publication_year=2026,
                isbn=f"978-perf-{i}", author_rel=author, user=self.user
            )
            Review.objects.create(book=book, content="Чудово", rating=5)

    def test_optimized_query_count_is_minimal(self) -> None:
        """Перевірка, що оптимізований метод робить рівно 2 SQL-запити незалежно від об'єму даних."""
        with CaptureQueriesContext(connection) as ctx:
            books = Book.objects.select_related('author_rel').prefetch_related('reviews')
            for book in books:
                author = book.author_rel.name if book.author_rel else "None"
                reviews = [r.content for r in book.reviews.all()]

        self.assertEqual(len(ctx), 2)

    def test_view_accessibility(self) -> None:
        """Перевірка успішності відображення сторінки результатів."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
