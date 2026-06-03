from django.test import SimpleTestCase
from django.urls import reverse, resolve
from .. import views


class MainUrlsTest(SimpleTestCase):
    """Набір тестів для перевірки коректності маршрутизації (urls.py) застосунку main."""

    def test_home_url_resolves(self) -> None:
        """Перевірка, що URL головної сторінки викликає home_view."""
        url = reverse('main:home')
        match = resolve(url)
        self.assertEqual(match.func, views.home_view)
        self.assertEqual(match.view_name, 'main:home')

    def test_about_url_resolves(self) -> None:
        """Перевірка, що URL 'about/' викликає about_view."""
        url = reverse('main:about')
        match = resolve(url)
        self.assertEqual(match.func, views.about_view)

    def test_post_url_resolves(self) -> None:
        """Перевірка, що динамічний URL поста з ID викликає post_view."""
        url = reverse('main:post_detail', kwargs={'id': 42})
        match = resolve(url)
        self.assertEqual(match.func, views.post_view)
        self.assertEqual(match.kwargs['id'], 42)

    def test_event_url_resolves(self) -> None:
        """Перевірка, що складний динамічний URL дати викликає event_view."""
        url = reverse('main:event_detail', kwargs={'year': 2026, 'month': 5, 'day': 1})
        match = resolve(url)
        self.assertEqual(match.func, views.event_view)
        self.assertEqual(match.kwargs['year'], 2026)

    def test_contact_url_resolves(self) -> None:
        """Перевірка, що URL контактів викликає клас-представлення ContactView."""
        url = reverse('main:contact')
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.ContactView)

    def test_services_url_resolves(self) -> None:
        """Перевірка, що URL послуг викликає клас-представлення ServiceView."""
        url = reverse('main:services')
        match = resolve(url)
        self.assertEqual(match.func.view_class, views.ServiceView)
