
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from core.fields import UpperCaseCharField
from core.managers import StatsManager


def validate_positive_price(value) -> None:
    """Валідатор для перевірки, що ціна є позитивним числом."""
    if value <= 0:
        raise ValidationError("Ціна повинна бути позитивним числом.")


class Category(models.Model):
    """Модель Категорії товарів."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    color = UpperCaseCharField(
        max_length=7,
        default="#0D6EFD",
        verbose_name="Колір категорії (HEX)"
    )

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def active_ads_count(self) -> int:
        """Метод для підрахунку активних оголошень у цій категорії."""
        return self.ads.filter(is_active=True).count()

    def __str__(self) -> str:
        return self.name

    objects = StatsManager()


class Ad(models.Model):
    """Модель Оголошення."""
    title = UpperCaseCharField(max_length=150, verbose_name="Заголовок оголошення")
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_positive_price])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='ads')

    objects = StatsManager()

    class Meta:
        verbose_name = "Оголошення"
        verbose_name_plural = "Оголошення"

    def short_description(self) -> str:
        """Метод короткого опису (до 100 символів)."""
        return self.description[:100] + "..." if len(self.description) > 100 else self.description

    def deactivate_if_expired(self) -> None:
        """
        ВІДКОРИГОВАНО: Метод деактивації через 30 днів.
        Тепер він змінює статус ТІЛЬКИ в пам'яті. Метод .save() видалено,
        що повністю захищає систему від нескінченної рекурсії в сигналах!
        """
        if self.is_active and self.created_at and (timezone.now() - self.created_at).days >= 30:
            self.is_active = False

    def get_comments_count(self) -> int:
        """Покращено: Метод перенесено в саму модель оголошення для зручності виклику в шаблонах."""
        return self.comments.count()

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    """Модель Коментаря до оголошення."""
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='board_comments')

    class Meta:
        verbose_name = "Коментар"
        verbose_name_plural = "Коментарі"

    def __str__(self) -> str:
        return f"Коментар від {self.user.username} до {self.ad.title[:20]}"
