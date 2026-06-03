from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from board.models import Category, Ad


class CustomStatsManagerTest(TestCase):
    """Набір інтеграційних тестів для перевірки агрегацій та сирих SQL-запитів StatsManager."""

    def setUp(self) -> None:
        """Підготовка тестових даних за допомогою реальних моделей board."""
        self.user = User.objects.create_user(username="manager_tester", password="password123")

        self.cat_electronics = Category.objects.create(name="Електроніка", description="Гаджети")
        self.cat_books = Category.objects.create(name="Книги", description="Література")

        self.ad1 = Ad.objects.create(
            title="Смартфон",
            description="Опис",
            price=Decimal("10000.00"),
            is_active=True,
            user=self.user,
            category=self.cat_electronics
        )
        self.ad2 = Ad.objects.create(
            title="Ноутбук",
            description="Опис",
            price=Decimal("20000.00"),
            is_active=True,
            user=self.user,
            category=self.cat_electronics
        )
        self.ad3 = Ad.objects.create(
            title="Старий ПК",
            description="Опис",
            price=Decimal("5000.00"),
            is_active=False,
            user=self.user,
            category=self.cat_electronics
        )

    def test_queryset_active_filter(self) -> None:
        """Перевірка методу .active(), що він відсікає неактивні записи."""
        all_ads = Ad.objects.filter(category=self.cat_electronics)
        active_ads = Ad.objects.active().filter(category=self.cat_electronics)

        self.assertEqual(all_ads.count(), 3)
        self.assertEqual(active_ads.count(), 2)

    def test_get_price_stats_math(self) -> None:
        """Перевірка математичних обчислень (Sum, Avg, Count) методу get_price_stats."""
        stats = Ad.objects.active().filter(category=self.cat_electronics).get_price_stats()

        self.assertEqual(stats['total_sum'], Decimal("30000.00"))
        self.assertEqual(stats['average_price'], 15000.0)
        self.assertEqual(stats['total_count'], 2)

    def test_get_popular_categories_raw_sql(self) -> None:
        """Перевірка виконання складного низькорівневого сирого SQL-запиту менеджера."""
        popular_cats = Category.objects.get_popular_categories_raw()

        self.assertIsInstance(popular_cats, list)
        self.assertTrue(len(popular_cats) >= 2)

        electronics_stats = next(c for c in popular_cats if c['name'] == "Електроніка")
        self.assertEqual(electronics_stats['total_ads'], 2)
