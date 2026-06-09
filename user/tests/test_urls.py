from django.test import SimpleTestCase
from django.urls import reverse, resolve


class TestUrls(SimpleTestCase):
    """Набір тестів для перевірки коректності маршрутизації (urls.py) застосунку."""

    def test_register_url_resolves(self) -> None:
        """Перевірка, що URL 'register/' викликає правильне представлення register_view."""
        url = reverse('user:register')
        match = resolve(url)
        self.assertEqual(match.view_name, 'user:register')

    def test_edit_profile_url_resolves(self) -> None:
        """Перевірка, що URL 'edit/' викликає правильне представлення edit_profile_view."""
        url = reverse('user:edit_profile')
        match = resolve(url)
        self.assertEqual(match.view_name, 'user:edit_profile')

    def test_change_password_url_resolves(self) -> None:
        """Перевірка, що URL 'password/' викликає правильне представлення change_password_view."""
        url = reverse('user:change_password')
        match = resolve(url)
        self.assertEqual(match.view_name, 'user:change_password')

    def test_delete_account_url_resolves(self) -> None:
        """Перевірка, що URL 'delete/' викликає правильне представлення delete_account_view."""
        url = reverse('user:delete_account')
        match = resolve(url)
        self.assertEqual(match.view_name, 'user:delete_account')

    def test_profile_view_url_resolves(self) -> None:
        """Перевірка, що динамічний URL '<str:username>/' викликає правильне представлення profile_view."""
        url = reverse('user:profile_view', kwargs={'username': 'testuser'})
        match = resolve(url)
        self.assertEqual(match.view_name, 'user:profile_view')
