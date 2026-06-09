from django.test import SimpleTestCase
from django.urls import reverse, resolve
from .. import views


class BoardUrlsTest(SimpleTestCase):
    """Набір тестів для перевірки коректності маршрутизації (urls.py) застосунку board."""

    def test_index_url_resolves(self) -> None:
        """Перевірка, що URL 'list/' викликає index_view."""
        url = reverse('board:index_view')
        match = resolve(url)
        self.assertEqual(match.func, views.index_view)
        self.assertEqual(match.view_name, 'board:index_view')

    def test_recent_ads_url_resolves(self) -> None:
        """Перевірка, що URL 'recent/' викликає recent_ads_view."""
        url = reverse('board:recent_ads')
        match = resolve(url)
        self.assertEqual(match.func, views.recent_ads_view)

    def test_category_ads_url_resolves(self) -> None:
        """Перевірка, що динамічний URL категорії викликає category_ads_view."""
        url = reverse('board:category_ads', kwargs={'category_id': 5})
        match = resolve(url)
        self.assertEqual(match.func, views.category_ads_view)
        self.assertEqual(match.kwargs['category_id'], 5)

    def test_ad_detail_url_resolves(self) -> None:
        """Перевірка, що динамічний URL оголошення викликає ad_detail_view."""
        url = reverse('board:ad_detail', kwargs={'ad_id': 42})
        match = resolve(url)
        self.assertEqual(match.func, views.ad_detail_view)
        self.assertEqual(match.kwargs['ad_id'], 42)

    def test_user_profile_url_resolves(self) -> None:
        """Перевірка, що динамічний URL профілю оголошень викликає user_profile_view."""
        url = reverse('board:user_profile', kwargs={'username': 'test_seller'})
        match = resolve(url)
        self.assertEqual(match.func, views.user_profile_view)
        self.assertEqual(match.kwargs['username'], 'test_seller')
