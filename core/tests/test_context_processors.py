from decimal import Decimal
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core.cache import cache

from board.models import Category, Ad
from books.models import Book
from ..context_processors import global_site_stats


class GlobalSiteStatsProcessorTest(TestCase):
    """Набір тестів для перевірки автоматичного прокидання глобальної статистики в шаблони."""

    def setUp(self) -> None:
        """Підготовка базових тестових даних перед кожним тестом."""
        cache.clear()
        self.user = User.objects.create_user(username="stat_user", password="password123")
        self.category = Category.objects.create(name="Для дому", description="Меблі та декор")

        Ad.objects.create(
            title="Крісло м'яке",
            description="Опис",
            price=Decimal("4500.00"),
            user=self.user,
            category=self.category
        )

        Book.objects.create(
            title="Історія України",
            author="Михайло Грушевський",
            genre="Історія",
            publication_year=1913,
            isbn="978-966-03-5555-5",
            user=self.user
        )

        cache.set('global_request_metrics_count', 99)

    def test_global_site_stats_returns_correct_dictionary(self) -> None:
        """Перевірка, що процесор коректно зчитує бази даних та кєш і повертає правильну структуру словника."""
        request = RequestFactory().get('/')

        context_data = global_site_stats(request)

        self.assertIsInstance(context_data, dict)
        self.assertIn('global_active_ads', context_data)
        self.assertIn('global_total_books', context_data)
        self.assertIn('total_server_requests', context_data)
        self.assertEqual(context_data['global_active_ads'], 1)
        self.assertEqual(context_data['global_total_books'], 1)
        self.assertEqual(context_data['total_server_requests'], 99)
