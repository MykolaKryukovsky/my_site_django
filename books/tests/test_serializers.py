
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from typing import Dict, Any

from books.serializers import RegisterSerializer, BookSerializer


class RegisterSerializerTest(TestCase):
    """Набір тестів для перевірки серіалізатора реєстрації користувачів RegisterSerializer."""

    def test_valid_registration_data(self) -> None:
        """Перевірка валідності серіалізатора реєстрації з правильними даними."""
        valid_data = {
            'username': 'api_user',
            'email': 'api@example.com',
            'password': 'securepassword123'
        }
        serializer = RegisterSerializer(data=valid_data)

        self.assertTrue(serializer.is_valid())

        user = serializer.save()

        self.assertEqual(user.username, 'api_user')
        self.assertTrue(user.check_password('securepassword123'))

    def test_password_too_short_invalid(self) -> None:
        """Перевірка помилки валідації, якщо пароль коротший за 6 символів (min_length=6)."""
        invalid_data = {
            'username': 'api_user',
            'email': 'api@example.com',
            'password': '123'
        }
        serializer: RegisterSerializer = RegisterSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)


class BookSerializerTest(TestCase):
    """Набір тестів для перевірки бізнес-валідації серіалізатора книг BookSerializer."""

    def test_valid_book_serializer_data(self) -> None:
        """Перевірка валідності серіалізатора книг з повністю коректними даними."""
        valid_data = {
            'title': 'Чистий код',
            'author': 'Роберт Мартін',
            'genre': 'Програмування',
            'publication_year': 2008,
            'isbn': '978-5-4461-0960-9'
        }
        serializer = BookSerializer(data=valid_data)

        self.assertTrue(serializer.is_valid())

    def test_missing_required_title_field(self) -> None:
        """Перевірка помилки серіалізатора, якщо обов'язкове поле title відсутнє."""
        invalid_data: Dict[str, Any] = {
            'author': 'Роберт Мартін',
            'genre': 'Програмування',
            'publication_year': 2008,
            'isbn': '978-5-4461-0960-9'
        }
        serializer: BookSerializer = BookSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        self.assertEqual(serializer.errors['title'][0], "Це поле обов'язкове.")

    def test_custom_validation_publication_year_in_future(self) -> None:
        """Перевірка кастомної валідації: рік видання не може бути більшим за поточний."""
        future_year = timezone.now().year + 1
        invalid_data = {
            'title': 'Книга з майбутнього',
            'author': 'Тест',
            'genre': 'Фантастика',
            'publication_year': future_year,
            'isbn': '1234567890'
        }
        serializer = BookSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('publication_year', serializer.errors)
        self.assertEqual(
            serializer.errors['publication_year'][0],
            f"Рік видання не може бути більшим за поточний ({timezone.now().year})."
        )

    def test_custom_validation_publication_year_negative(self) -> None:
        """Перевірка кастомної валідації: рік видання не може бути нульовим або негативним."""
        invalid_data = {
            'title': 'Стародавня книга',
            'author': 'Тест',
            'genre': 'Історія',
            'publication_year': 0,
            'isbn': '1234567890'
        }
        serializer = BookSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('publication_year', serializer.errors)
        self.assertEqual(serializer.errors['publication_year'][0], "Рік видання не може бути негативним чи нульовим.")

    def test_custom_validation_isbn_invalid_characters(self) -> None:
        """Перевірка помилки валідації, якщо ISBN містить недозволені символи або літери."""
        invalid_data = {
            'title': 'Тестова книга',
            'author': 'Тест',
            'genre': 'Тест',
            'publication_year': 2020,
            'isbn': '978-5-4461-ABC-X'
        }
        serializer = BookSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('isbn', serializer.errors)
        self.assertEqual(serializer.errors['isbn'][0], "ISBN має складатися лише з цифр та дефісів.")

    def test_custom_validation_isbn_invalid_length(self) -> None:
        """Перевірка помилки валідації, якщо довжина очищеного ISBN не дорівнює 10 або 13 цифрам."""
        invalid_data = {
            'title': 'Тестова книга',
            'author': 'Тест',
            'genre': 'Тест',
            'publication_year': 2020,
            'isbn': '12345-678'
        }
        serializer = BookSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('isbn', serializer.errors)
        self.assertEqual(serializer.errors['isbn'][0], "Довжина ISBN має бути 10 або 13 цифр.")
