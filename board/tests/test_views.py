from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Category, Ad


class BoardViewsTest(TestCase):
    """Набір інтеграційних тестів для перевірки логіки представлень (views.py) застосунку board."""

    def setUp(self) -> None:
        """Підготовка початкових даних перед кожним тестом."""
        self.user = User.objects.create_user(username="seller_test", password="password123")
        self.cat1 = Category.objects.create(name="Транспорт", description="Авто та мото")
        self.cat2 = Category.objects.create(name="Нерухомість", description="Квартири та будинки")
        self.ad1 = Ad.objects.create(
            title="Продам Велосипед",
            description="Гірський велосипед у відмінному стані.",
            price=Decimal("5000.00"),
            user=self.user,
            category=self.cat1
        )
        self.ad2 = Ad.objects.create(
            title="Оренда Квартири",
            description="Затишна однокімнатна квартира в центрі.",
            price=Decimal("12000.00"),
            user=self.user,
            category=self.cat2
        )

    def test_index_view_without_filters(self) -> None:
        """Перевірка відображення загального списку оголошень без застосування фільтрів."""
        url = reverse('board:index_view')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board/ad_list.html')
        self.assertIn('ads', response.context)
        self.assertIn('categories', response.context)
        self.assertIn('stats', response.context)

    def test_index_view_search_filter(self) -> None:
        """Перевірка працездатності пошукового фільтра за текстом заголовку (?q=)."""
        url = reverse('board:index_view')
        response = self.client.get(url, {'q': 'Велосипед'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['ads'].count(), 1)
        self.assertEqual(response.context['ads'].first().title, "ПРОДАМ ВЕЛОСИПЕД")

    def test_index_view_category_and_price_filter(self) -> None:
        """Перевірка комбінованої фільтрації за категорією та мінімальною ціною."""
        url = reverse('board:index_view')

        response = self.client.get(url, {
            'cat_id': self.cat1.id,
            'min_price': '6000.00'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['ads'].count(), 0)

    def test_category_ads_view_success(self) -> None:
        """Перевірка відображення сторінки конкретної категорії."""
        url = reverse('board:category_ads', kwargs={'category_id': self.cat2.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board/category_ads.html')
        self.assertEqual(response.context['category'], self.cat2)
        # У цій категорії має бути лише одне оголошення про квартиру
        self.assertEqual(response.context['ads'].count(), 1)

    def test_ad_detail_view_success(self) -> None:
        """Перевірка відображення детальної сторінки оголошення."""
        url = reverse('board:ad_detail', kwargs={'ad_id': self.ad1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board/ad_detail.html')
        self.assertEqual(response.context['ad'], self.ad1)
        self.assertIn('comments', response.context)

    def test_recent_ads_view_success(self) -> None:
        """Перевірка відображення сторінки нещодавніх оголошень."""
        url = reverse('board:recent_ads')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board/recent_ads.html')
        self.assertIn('recent_stats', response.context)

    def test_user_profile_view_success(self) -> None:
        """Перевірка відображення оголошень конкретного автора профілю."""
        url = reverse('board:user_profile', kwargs={'username': self.user.username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board/user_ads.html')
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(response.context['user_ads'].count(), 2)
