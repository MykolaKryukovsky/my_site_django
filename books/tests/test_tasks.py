from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from ..models import Book, Author
from ..tasks import import_books_from_csv_task


class CeleryTaskIntegrationTest(TestCase):
    """Інтеграційні тести для перевірки асинхронного імпорту через Celery."""

    def setUp(self) -> None:
        from django.conf import settings
        settings.CELERY_TASK_ALWAYS_EAGER = True

        self.url = reverse('books:csv_import')
        self.user = User.objects.create_user(username="celery_user", password="password123")
        self.csv_data = "title,author,genre,year,isbn\nТестова Книга,Іван Франко,Драма,1900,978-celery-1\n"

    def test_csv_import_task_creates_books_and_sends_email(self) -> None:
        """Перевірка, що задача успішно парсить CSV, зберігає дані в БД та надсилає email."""
        mail.outbox = []
        result = import_books_from_csv_task.delay(self.csv_data, self.user.id, "user@example.com")

        self.assertEqual(result.status, 'SUCCESS')
        self.assertTrue(Book.objects.filter(isbn="978-celery-1").exists())
        self.assertTrue(Author.objects.filter(name="Іван Франко").exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Імпорт книг успішно завершено!", mail.outbox[0].subject)
