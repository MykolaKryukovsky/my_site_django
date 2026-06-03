from django.test import TestCase
from django.contrib.auth.models import User
from books.models import Book
from ..fields import UpperCaseCharField


class UpperCaseCharFieldTest(TestCase):
    """Набір тестів для перевірки роботи кастомного поля UpperCaseCharField."""

    def setUp(self) -> None:
        """Підготовка базових даних перед кожним тестом."""
        self.user = User.objects.create_user(username="field_tester", password="password123")

    def test_automatically_converts_to_uppercase_on_save(self) -> None:
        """Перевірка, що поле автоматично переводить будь-який текст у верхній регістр при збереженні."""
        book = Book.objects.create(
            title="hello django",
            author="Test",
            genre="Test",
            publication_year=2026,
            isbn="978-0-00-000000-1",
            user=self.user
        )

        self.assertEqual(book.title, "HELLO DJANGO")

        book.refresh_from_db()
        self.assertEqual(book.title, "HELLO DJANGO")

    def test_handles_already_uppercase_text(self) -> None:
        """Перевірка, що поле коректно обробляє текст, який вже у верхньому регістрі."""
        book = Book.objects.create(
            title="PYTHON",
            author="Test",
            genre="Test",
            publication_year=2026,
            isbn="978-0-00-000000-2",
            user=self.user
        )
        self.assertEqual(book.title, "PYTHON")

    def test_handles_non_string_values_safely(self) -> None:
        """Перевірка, що логіка pre_save безпечно ігнорує значення None."""
        book = Book(title=None)
        book_field = Book._meta.get_field('title')

        try:
            book_field.pre_save(book, add=True)
        except AttributeError:
            self.fail("UpperCaseCharField впало з помилкою AttributeError при обробці None!")
