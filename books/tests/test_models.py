import uuid
from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Author, Book, Review


class BookModelsTest(TestCase):
    """Набір тестів для перевірки працездатності моделей застосунку books."""

    def setUp(self) -> None:
        """Підготовка базових тестових даних перед кожним тестом."""
        self.user = User.objects.create_user(
            username="librarian",
            password="securepassword123"
        )
        self.book = Book.objects.create(
            title="Кобзар",
            author="Тарас Шевченко",
            genre="Поезія",
            publication_year=1840,
            isbn="978-966-03-7000-0",
            user=self.user
        )

    def test_book_creation_and_fields(self) -> None:
        """Перевірка коректності створення книги та збереження полів."""
        self.assertIsInstance(self.book.id, uuid.UUID)
        self.assertEqual(self.book.title, "КОБЗАР")
        self.assertEqual(self.book.author, "Тарас Шевченко")
        self.assertEqual(self.book.genre, "Поезія")
        self.assertEqual(self.book.publication_year, 1840)
        self.assertEqual(self.book.isbn, "978-966-03-7000-0")
        self.assertEqual(self.book.user, self.user)

    def test_string_representation(self) -> None:
        """Перевірка магічного методу __str__ для текстового виводу книги."""
        expected_str = "КОБЗАР — Тарас Шевченко"
        self.assertEqual(str(self.book), expected_str)

    def test_set_null_on_user_deletion(self) -> None:
        """Перевірка, що при видаленні користувача запис книги не видаляється (on_delete=models.SET_NULL)."""
        self.user.delete()
        self.book.refresh_from_db()
        self.assertIsNone(self.book.user)


class BookAndReviewModelsTest(TestCase):
    """Набір тестів для перевірки працездатності моделей Book та Review застосунку books."""

    def setUp(self) -> None:
        """Підготовка базових тестових даних перед кожним тестом."""
        self.user = User.objects.create_user(
            username="librarian",
            password="securepassword123"
        )
        self.author = Author.objects.create(name="Тарас Шевченко")

        self.book = Book.objects.create(
            title="Кобзар",
            genre="Поезія",
            publication_year=1840,
            isbn="978-966-03-7000-0",
            user=self.user,
            author_rel=self.author
        )

        self.review = Review.objects.create(
            book=self.book,
            content="Неймовірна збірка української поезії, обов'язкова до прочитання.",
            rating=5
        )

    def test_book_creation_and_fields(self) -> None:
        """Перевірка коректності створення книги та збереження полів."""
        self.assertIsInstance(self.book.id, uuid.UUID)
        self.assertEqual(self.book.title, "КОБЗАР")
        self.assertEqual(self.book.author_rel, self.author)
        self.assertEqual(self.book.isbn, "978-966-03-7000-0")

    def test_book_string_representation(self) -> None:
        """Перевірка магічного методу __str__ для текстового виводу книги."""
        self.assertEqual(str(self.book), "КОБЗАР — Тарас Шевченко")


    def test_review_creation_and_fields(self) -> None:
        """Перевірка успішного створення рецензії та заповнення її атрибутів."""
        self.assertEqual(self.review.book, self.book)
        self.assertEqual(self.review.content, "Неймовірна збірка української поезії, обов'язкова до прочитання.")
        self.assertEqual(self.review.rating, 5)

    def test_review_string_representation(self) -> None:
        """Перевірка магічного методу __str__ для моделі Review."""
        expected_str = f"Рецензія на КОБЗАР (5/5)"
        self.assertEqual(str(self.review), expected_str)

    def test_review_cascade_deletion_with_book(self) -> None:
        """Перевірка каскадного видалення: разом із книговею мають видалятися її рецензії."""
        review_id = self.review.id

        self.book.delete()

        with self.assertRaises(Review.DoesNotExist):
            Review.objects.get(id=review_id)
