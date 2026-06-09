from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Author, Book, Review


class BookORMAnalyticsTest(TestCase):
    """Набір тестів для перевірки правильності агрегацій, анотацій та сортування в базі даних."""

    def setUp(self) -> None:
        self.url = reverse('books:books_analytics')
        self.user = User.objects.create_user(username="analytics_user", password="password123")

        self.author_a = Author.objects.create(name="Автор А")
        self.author_b = Author.objects.create(name="Автор Б")

        self.book_a1 = Book.objects.create(
            title="Популярна Книга", genre="Драма", publication_year=2020,
            isbn="978-an-1", author_rel=self.author_a, user=self.user
        )
        self.book_a2 = Book.objects.create(
            title="Звичайна Книга", genre="Наука", publication_year=2021,
            isbn="978-an-2", author_rel=self.author_a, user=self.user
        )

        self.book_b1 = Book.objects.create(
            title="Нейтральна Книга", genre="Фентезі", publication_year=2022,
            isbn="978-an-3", author_rel=self.author_b, user=self.user
        )

        Review.objects.create(book=self.book_a1, content="Супер", rating=5)
        Review.objects.create(book=self.book_a1, content="Клас", rating=5)
        Review.objects.create(book=self.book_a1, content="Добре", rating=4)

        Review.objects.create(book=self.book_a2, content="Норм", rating=3)

        Review.objects.create(book=self.book_b1, content="Ок", rating=4)
        Review.objects.create(book=self.book_b1, content="Нормально", rating=4)

    def test_view_accessibility(self) -> None:
        """Перевірка успішного рендерингу сторінки аналітики (200 OK)."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/orm_analytics.html')

    def test_books_annotation_and_sorting_logic(self) -> None:
        """Перевірка правильності підрахунку відгуків та сортування книг у списку."""
        response = self.client.get(self.url)
        books_queryset = response.context['books']

        first_book = books_queryset[0]
        self.assertEqual(first_book.title, "ПОПУЛЯРНА КНИГА")  # враховуємо UpperCaseCharField
        self.assertEqual(first_book.total_reviews, 3)
        self.assertAlmostEqual(first_book.average_rating, 4.67, places=2)

        second_book = books_queryset[1]
        self.assertEqual(second_book.title, "НЕЙТРАЛЬНА КНИГА")
        self.assertEqual(second_book.total_reviews, 2)

    def test_authors_analytics_aggregation(self) -> None:
        """Перевірка точності підрахунку об'ємів книг та середнього рейтингу авторів."""
        response = self.client.get(self.url)
        authors_data = response.context['authors_analytics']

        author_a_stats = next(a for a in authors_data if a.name == "Автор А")
        self.assertEqual(author_a_stats.total_books, 2)
        self.assertEqual(author_a_stats.author_avg_rating, 4.25)

        author_b_stats = next(a for a in authors_data if a.name == "Автор Б")
        self.assertEqual(author_b_stats.total_books, 1)
        self.assertEqual(author_b_stats.author_avg_rating, 4.0)
