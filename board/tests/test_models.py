from decimal import Decimal
from datetime import timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..models import Category, Ad, Comment


class BoardModelsTest(TestCase):
    """Набір тестів для перевірки працездатності моделей застосунку board."""

    def setUp(self) -> None:
        """Підготовка базових тестових даних перед кожним тестом."""
        self.user = User.objects.create_user(
            username="seller",
            password="securepassword123"
        )
        self.category = Category.objects.create(
            name="Електроніка",
            description="Гаджети та пристрої",
            color="#0D6EFD"
        )
        self.ad = Ad.objects.create(
            title="Смартфон Apple iPhone 15",
            description="Новий телефон у коробці, оригінал, офіційна гарантія.",
            price=Decimal("35000.00"),
            user=self.user,
            category=self.category
        )

    def test_category_creation_and_methods(self) -> None:
        """Перевірка створення категорії, її __str__ та підрахунку активних оголошень."""
        self.assertEqual(self.category.name, "Електроніка")
        self.assertEqual(str(self.category), "Електроніка")
        self.assertEqual(self.category.active_ads_count(), 1)
        self.ad.is_active = False
        self.ad.save()
        self.assertEqual(self.category.active_ads_count(), 0)

    def test_ad_short_description(self) -> None:
        """Перевірка обрізання короткого опису оголошення до 100 символів."""
        short_ad = Ad(description="Короткий опис")
        self.assertEqual(short_ad.short_description(), "Короткий опис")

        long_desc = "A" * 150
        long_ad = Ad(description=long_desc)
        self.assertEqual(long_ad.short_description(), ("A" * 100) + "...")

    def test_ad_positive_price_validator(self) -> None:
        """Перевірка, що валідатор не дозволяє створювати оголошення з ціною <= 0."""
        invalid_ad = Ad(
            title="Тест",
            description="Опис",
            price=Decimal("-10.00"),
            user=self.user,
            category=self.category
        )
        with self.assertRaises(ValidationError):
            invalid_ad.full_clean()

        invalid_ad.price = Decimal("0.00")
        with self.assertRaises(ValidationError):
            invalid_ad.full_clean()

    def test_ad_deactivate_if_expired(self) -> None:
        """Перевірка методу автоматичної деактивації оголошення через 30 днів."""
        self.assertTrue(self.ad.is_active)
        self.ad.created_at = timezone.now() - timedelta(days=31)
        self.ad.deactivate_if_expired()
        self.assertFalse(self.ad.is_active)

    def test_comment_creation_and_count(self) -> None:
        """Перевірка створення коментаря та зв'язку лічильника коментарів в моделі Ad."""
        self.assertEqual(self.ad.get_comments_count(), 0)

        comment = Comment.objects.create(
            content="Чудова ціна! Який стан батареї?",
            ad=self.ad,
            user=self.user
        )

        self.assertEqual(self.ad.get_comments_count(), 1)
        self.assertIn(f"Коментар від {self.user.username}", str(comment))
