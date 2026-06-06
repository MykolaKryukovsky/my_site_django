from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Author, Book, Review


class BookRawSQLTest(TestCase):
    """Набір тестів для перевірки працездатності та безпеки низькорівневих Raw SQL запитів."""

    def setUp(self) -> None:
        self.url = reverse('books:books_raw_sql')
        self.user = User.objects.create_user(username="sql_tester", password="password123")

        self.author_popular = Author.objects.create(name="Популярний Автор")
        self.author_regular = Author.objects.create(name="Звичайний Автор")

        self.book_pop = Book.objects.create(
            title="Бестселер", genre="Фантастика", publication_year=2025,
            isbn="978-raw-1", author_rel=self.author_popular, user=self.user
        )
        self.book_reg = Book.objects.create(
            title="Проста Книга", genre="Наука", publication_year=2026,
            isbn="978-raw-2", author_rel=self.author_regular, user=self.user
        )

        Review.objects.create(book=self.book_pop, content="Клас", rating=5)
        Review.objects.create(book=self.book_pop, content="Супер", rating=5)
        Review.objects.create(book=self.book_pop, content="Цікаво", rating=4)

        Review.objects.create(book=self.book_reg, content="Норм", rating=3)

    def test_raw_sql_filtering_success(self) -> None:
        """Перевірка правильної роботи HAVING COUNT у сирому SQL при зміні ліміту."""
        # Запитуємо авторів, у яких більше 2 відгуків. Має повернутися тільки Популярний Автор (3 відгуки)
        response = self.client.get(self.url, {'limit': '2'})
        self.assertEqual(response.status_code, 200)

        authors_queryset = response.context['authors']
        self.assertEqual(len(list(authors_queryset)), 1)
        self.assertEqual(authors_queryset[0].name, "Популярний Автор")

        response_all = self.client.get(self.url, {'limit': '0'})
        self.assertEqual(len(list(response_all.context['authors'])), 2)

    def test_cursor_genres_aggregation_success(self) -> None:
        """Перевірка агрегації жанрів за допомогою connection.cursor()."""
        response = self.client.get(self.url)
        genres_data = response.context['genres_stats']

        self.assertEqual(len(genres_data), 2)

        fantasy_stat = next(g for g in genres_data if g['genre'] == "Фантастика")
        self.assertEqual(fantasy_stat['total_books'], 1)

    def test_sql_injection_defense_safety(self) -> None:
        """Перевірка захисту від SQL-ін'єкцій: передача шкідливого рядка не повинна ламати базу."""
        malicious_payload = "1; DROP TABLE books_review;"

        response = self.client.get(self.url, {'limit': malicious_payload})

        self.assertEqual(response.status_code, 200)
        self.assertIn('genres_stats', response.context)
