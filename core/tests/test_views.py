from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import cache

from board.models import Category, Ad
from books.models import Book


class SystemDashboardViewTest(TestCase):
    """Набір інтеграційних тестів для перевірки головної аналітичної панелі сайту."""

    def setUp(self) -> None:
        """Підготовка базових тестових даних перед кожним тестом."""
        cache.clear()

        self.user = User.objects.create_user(username="analyst", password="password123")
        self.category = Category.objects.create(name="Тестова Категорія", description="Опис")

        self.ad = Ad.objects.create(
            title="Тестове оголошення",
            description="Опис товару",
            price=Decimal("1500.00"),
            user=self.user,
            category=self.category
        )

        self.book = Book.objects.create(
            title="Тестова Книга",
            author="Тестовий Автор",
            genre="Наука",
            publication_year=2026,
            isbn="978-0-00-000000-0",
            user=self.user
        )

        cache.set('global_request_metrics_count', 42)

        self.url = reverse('system_dashboard')

    def test_dashboard_view_success_and_template(self) -> None:
        """Перевірка успішної доступності аналітичної панелі та її шаблону."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_dashboard_view_context_data_structure(self) -> None:
        """Перевірка наявності та коректності розрахованих статистичних даних у контексті."""
        response = self.client.get(self.url)

        self.assertIn('ad_stats', response.context)
        self.assertEqual(response.context['ad_stats']['total_sum'], Decimal("1500.00"))
        self.assertIn('book_stats', response.context)
        self.assertEqual(response.context['book_stats']['distinct_author'], 1)
        self.assertIn('popular_categories', response.context)
        self.assertIsInstance(response.context['popular_categories'], list)
        self.assertIn('total_server_requests', response.context)
        self.assertEqual(response.context['total_server_requests'], 43)
