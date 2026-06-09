from decimal import Decimal
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Book


class BooksAPITestCase(APITestCase):
    """Набір інтеграційних тестів для перевірки REST API та прав доступу застосунку books."""

    def setUp(self) -> None:
        """Підготовка базових даних перед кожним тестом API."""
        # Створюємо звичайного користувача та адміністратора (is_staff=True)
        self.user = User.objects.create_user(username="librarian_api", password="password123")
        self.admin_user = User.objects.create_user(username="admin_api", password="password123", is_staff=True)

        self.book = Book.objects.create(
            title="Енеїда",
            author="Іван Котляревський",
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
        """Перевірка, що аноніму заборонено доступ до списку (401 Unauthorized)."""
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_books_list_authenticated_success(self) -> None:
        """Перевірка успішного отримання списку книг авторизованим користувачем."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

    def test_get_book_detail_authenticated_success(self) -> None:
        """Перевірка отримання деталей конкретної книги."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "ЕНЕЇДА")

    def test_create_book_success(self) -> None:
        """Перевірка створення нової книги авторизованим користувачем."""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Захар Беркут",
            "author": "Іван Франко",
            "genre": "Повість",
            "publication_year": 1883,
            "isbn": "978-966-03-9000-0"
        }
        response = self.client.post(self.list_url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Book.objects.filter(isbn="978-966-03-9000-0").exists())

    def test_delete_book_by_regular_user_forbidden(self) -> None:
        """Перевірка IsAdminOrReadOnlyForDelete: звичайному користувачу заборонено видаляти книги (403)."""
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(pk=self.book.pk).exists())

    def test_delete_book_by_admin_success(self) -> None:
        """Перевірка IsAdminOrReadOnlyForDelete: адміністратор може успішно видалити книгу (244 No Content)."""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())

    def test_api_user_registration_success(self) -> None:
        """Перевірка успішної реєстрації нового користувача через API-ендпоінт."""
        data = {
            "username": "new_api_user",
            "email": "new_api@example.com",
            "password": "securepassword123",
            "password_confirmation": "securepassword123",
            "phone_number": "+380991112233"
        }
        response = self.client.post(self.register_url, data=data)

        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])
        self.assertTrue(User.objects.filter(username="new_api_user").exists())
