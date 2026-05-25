
from django.test import SimpleTestCase
from django.urls import reverse, resolve, ResolverMatch

from .. import views


class TestUrls(SimpleTestCase):
    """Набір тестів для перевірки коректності маршрутизації (urls.py) застосунку."""

    def test_register_url_resolves(self) -> None:
        """Перевірка, що URL 'register/' викликає правильне представлення register_view."""
        url = reverse('register')
        match = resolve(url)
        self.assertEqual(match.func, views.register_view)

    def test_edit_profile_url_resolves(self) -> None:
        """Перевірка, що URL 'edit/' викликає правильне представлення edit_profile_view."""
        url = reverse('edit_profile')
        match = resolve(url)
        self.assertEqual(match.func, views.edit_profile_view)

    def test_change_password_url_resolves(self) -> None:
        """Перевірка, що URL 'password/' викликає правильне представлення change_password_view."""
        url = reverse('change_password')
        match = resolve(url)
        self.assertEqual(match.func, views.change_password_view)

    def test_delete_account_url_resolves(self) -> None:
        """Перевірка, що URL 'delete/' викликає правильне представлення delete_account_view."""
        url = reverse('delete_account')
        match = resolve(url)
        self.assertEqual(match.func, views.delete_account_view)

    def test_profile_view_url_resolves(self) -> None:
        """Перевірка, що динамічний URL '<str:username>/' викликає правильне представлення profile_view."""
        url = reverse('profile_view', kwargs={'username': 'testuser'})
        match = resolve(url)
        self.assertEqual(match.func, views.profile_view)
