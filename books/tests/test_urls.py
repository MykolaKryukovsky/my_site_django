from django.test import SimpleTestCase
from django.urls import reverse, resolve


class BooksUrlsTest(SimpleTestCase):
    """Набір тестів для перевірки коректності маршрутизації API (urls.py) застосунку books."""

    def test_books_list_url_resolves(self) -> None:
        """Перевірка, що API-URL списку книг викликає правильний маршрут."""
        url = reverse('books:book-list')
        match = resolve(url)

        self.assertEqual(match.view_name, 'books:book-list')

    def test_books_detail_url_resolves(self) -> None:
        """Перевірка, що API-URL детальної сторінки книги викликає правильний маршрут."""
        url = reverse('books:book-detail', kwargs={'pk': '12345678-1234-5678-1234-567812345678'})
        match = resolve(url)

        self.assertEqual(match.view_name, 'books:book-detail')

    def test_register_url_resolves(self) -> None:
        """Перевірка, що URL реєстрації користувача через API викликає RegisterView."""
        url = reverse('books:auth_register')
        match = resolve(url)

        self.assertEqual(match.view_name, 'books:auth_register')
