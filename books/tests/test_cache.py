from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
from django.contrib.auth.models import User
from django.test.utils import CaptureQueriesContext
from django.db import connection

from ..models import Author, Book


class BookCacheAndMiddlewareTest(TestCase):
    """Набір інтеграційних тестов для перевірки логіки кэшування та роботи сигналів."""

    def setUp(self) -> None:
        cache.clear()
        self.url = reverse('books:cached_books_catalog')
        self.user = User.objects.create_user(username="librarian_cache", password="password123")
        self.author = Author.objects.create(name="Франко")

        self.book = Book.objects.create(
            title="Лис Микита", genre="Казка", publication_year=1890,
            isbn="978-cache-test", author_rel=self.author, user=self.user
        )

    def test_view_caches_data_on_first_request(self) -> None:
        """Перевірка, що перший запит наповнює кєш, а другий бере дані з кєшу без SQL-запитів."""
        self.assertIsNone(cache.get('global_books_list_cache'))

        response1 = self.client.get(self.url)
        self.assertEqual(response1.status_code, 200)
        self.assertIsNotNone(response1.context)
        self.assertFalse(response1.context['from_cache'])
        self.assertIsNotNone(cache.get('global_books_list_cache'))

        response2 = self.client.get(self.url)
        self.assertEqual(response2.status_code, 200)
        self.assertIsNone(response2.context)

    def test_signal_invalidates_cache_on_new_book(self) -> None:
        """Перевірка, що створення нової книги через сигнал скидає (інвалідує) старий кєш."""
        self.client.get(self.url)
        self.assertIsNotNone(cache.get('global_books_list_cache'))

        Book.objects.create(
            title="Захар Беркут", genre="Повість", publication_year=1883,
            isbn="978-cache-new", author_rel=self.author, user=self.user
        )

        self.assertIsNone(cache.get('global_books_list_cache'))

    def test_anonymous_middleware_caches_html_page(self) -> None:
        """Перевірка, що AnonymousBooksCacheMiddleware успішно кешує HTML-сторінку для анонімів."""
        cache.clear()

        with CaptureQueriesContext(connection) as ctx_slow:
            response1 = self.client.get(self.url)
        self.assertEqual(response1.status_code, 200)
        self.assertIsNotNone(cache.get('anonymous_books_page_cache'))

        with CaptureQueriesContext(connection) as ctx_fast:
            response2 = self.client.get(self.url)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(len(ctx_fast), 0)
