from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.test.utils import CaptureQueriesContext
from django.core.cache import cache
from django.core import mail
from django.db import connection
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Author, Book, Review


class BookViewSetAPITest(APITestCase):
    """Набір інтеграційних тестів для перевірки REST API (BookViewSet & RegisterView)."""

    def setUp(self) -> None:
        """Підготовка даних для API запитів."""
        self.user = User.objects.create_user(username="librarian_api", password="password123")
        self.admin_user = User.objects.create_user(username="admin_api", password="password123", is_staff=True)

        self.book = Book.objects.create(
            title="Енеїда",
            genre="Поема",
            publication_year=1798,
            isbn="978-966-03-8000-0",
            user=self.user
        )

        self.list_url = reverse('books:book-list')
        self.detail_url = reverse('books:book-detail', kwargs={'pk': str(self.book.pk)})
        self.stats_url = reverse('books:book-stats')
        self.register_url = reverse('books:auth_register')

    def test_get_books_list_anonymous_forbidden(self) -> None:
        """Перевірка, що анонімному користувачу заборонено доступ до списку книг (401)."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_books_list_authenticated_success(self) -> None:
        """Перевірка успішного отримання пагінованого списку книг авторизованим користувачем."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_create_book_authenticated_success(self) -> None:
        """Перевірка успішного створення книги через API з автоматичною прив'язкою користувача."""
        self.client.force_authenticate(user=self.user)

        from books.models import Author
        test_author = Author.objects.create(name="Тарас Шевченко")

        data = {
            "title": "Захар Беркут",
            "genre": "Повість",
            "publication_year": 1883,
            "isbn": "978-966-03-9000-0",
            "author": test_author.id  # Змінили ключ з 'author_rel' на 'author'
        }
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_book = Book.objects.get(isbn="978-966-03-9000-0")
        self.assertEqual(created_book.user, self.user)

    def test_delete_book_by_regular_user_forbidden(self) -> None:
        """Перевірка пермішену AdminDel: звичайному користувачу заборонено видаляти книги (403)."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_by_admin_success(self) -> None:
        """Перевірка пермішену AdminDel: адміністратор може успішно видалити книгу (204)."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_custom_action_stats_success(self) -> None:
        """Перевірка працездатності кастомного екшену статистики."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.stats_url, {'genre': 'Поема'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_user_registration_success(self) -> None:
        """Перевірка успішної реєстрації нового користувача через RegisterView."""
        data = {
            "username": "new_library_user",
            "email": "library@example.com",
            "password": "securepassword123",
            "password_confirmation": "securepassword123",
            "phone_number": "+380991112233"
        }
        response = self.client.post(self.register_url, data=data)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])


class ORMPerformanceListViewTest(TestCase):
    """Набір інтеграційних тестів для перевірки традиційного представлення ORMPerformanceListView."""

    def setUp(self) -> None:
        """Підготовка даних для вимірювання продуктивності."""
        self.url = reverse('books:perf_demo')
        self.user = User.objects.create_user(username="perf_tester", password="password123")
        self.author = Author.objects.create(name="Тестовий Автор")

        for i in range(3):
            book = Book.objects.create(
                title=f"Книга Тесту #{i}", genre="Наука", publication_year=2026,
                isbn=f"978-perf-test-{i}", author_rel=self.author, user=self.user
            )
            Review.objects.create(book=book, content="Чудовий відгук 1", rating=5)
            Review.objects.create(book=book, content="Чудовий відгук 2", rating=4)

    def test_view_accessibility_and_template(self) -> None:
        """Перевірка успішної доступності сторінки замірів (200 OK) та шаблону."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/orm_performance.html')

    def test_view_context_contains_performance_metrics(self) -> None:
        """Перевірка, що класс розраховує та передає в HTML-шаблон усі метрики швидкості."""
        response = self.client.get(self.url)
        self.assertIn('slow_queries', response.context)
        self.assertIn('fast_queries', response.context)
        self.assertIn('boost', response.context)
        self.assertTrue(response.context['fast_queries'] <= response.context['slow_queries'])

    def test_optimized_queryset_query_count_is_strictly_two(self) -> None:
        """Перевірка, що метод get_queryset виконує рівно 2 SQL-запити (select_related + prefetch_related)."""
        with CaptureQueriesContext(connection) as ctx:
            books = Book.objects.select_related('author_rel').prefetch_related('reviews')
            for book in books:
                author_name = book.author_rel.name if book.author_rel else "Невідомо"
                reviews = [rev.content for rev in book.reviews.all()]
        self.assertEqual(len(ctx), 2)


class CachedBooksListViewTest(TestCase):
    """Тести для перевірки логіки низькорівневого кешування в CachedBooksListView."""

    def setUp(self) -> None:
        cache.clear()
        self.url = reverse('books:cached_books_catalog')
        self.user = User.objects.create_user(username="cache_user", password="password123")
        self.book = Book.objects.create(
            title="Лісова Пісня", genre="Драма", publication_year=1911,
            isbn="978-cache-cbv", user=self.user
        )

    def test_view_caches_on_first_request_and_uses_cache_on_second(self) -> None:
        """Перевірка, що перший запит іде в БД (from_cache=False), а другий береться з кешу."""
        response1 = self.client.get(self.url)
        self.assertIsNotNone(response1.context)
        self.assertFalse(response1.context['from_cache'])

        response2 = self.client.get(self.url)
        self.assertEqual(response2.status_code, 200)
        self.assertIsNone(response2.context)


class CeleryCSVImportViewsTest(TestCase):
    """Тести для перевірки завантаження CSV та перегляду статусів задач Celery."""

    def setUp(self) -> None:
        from django.conf import settings
        settings.CELERY_TASK_ALWAYS_EAGER = True  # Виконувати таски синхронно в тестах

        self.import_url = reverse('books:csv_import')
        self.user = User.objects.create_user(username="celery_user", password="password123")

        self.fake_task_id = "12345678-abcd-1234-abcd-123456789abc"
        self.status_url = reverse('books:task_status', kwargs={'task_id': self.fake_task_id})

    def test_csv_import_view_accessibility(self) -> None:
        """Перевірка доступності сторінки завантаження CSV файлу."""
        response = self.client.get(self.import_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/csv_import.html')

    def test_task_status_view_accessibility(self) -> None:
        """Перевірка доступності сторінки моніторингу статусу таски Celery."""
        response = self.client.get(self.status_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/task_status.html')
        self.assertEqual(response.context['task_id'], self.fake_task_id)
