
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from core.fields import UpperCaseCharField
from core.managers import StatsManager


def validate_positive_price(value: int) -> None:
    """Валідатор для цін"""
    if value <= 0:
        raise ValidationError("Ціна повинна бути позитивним числом.")


class Profile(models.Model):
    """Модель профілю (доп. атрибути для користувача)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=11)
    address = models.TextField()

    def __str__(self) -> str:
        return str(self.user.username)


class Category(models.Model):
    """Модель Категорії"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    color = UpperCaseCharField(
        max_length=7,
        default="#0D6EFD",
        verbose_name="Колір категорії (HEX)"
    )

    def active_ads_count(self) -> int:
        """Метод для підсчета активних оголошень"""
        return self.ads.filter(is_active=True).count()

    def __str__(self) -> None:
        return self.name


class Ad(models.Model):
    """Модель Оголошення"""
    title = UpperCaseCharField(max_length=150, verbose_name="Заголовок оголошення")
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_positive_price])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='ads')

    objects = StatsManager()

    def short_description(self) -> str:
        """Метод короткого опису (до 100 символів)"""
        return self.description[:100] + "..." if len(self.description) > 100 else self.description

    def deactivate_if_expired(self) -> None:
        """Метод деактивації через 30 днів"""
        if self.is_active and (timezone.now() - self.created_at).days >= 30:
            self.is_active = False
            self.save()

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    """Модель Комментария"""
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_comments_count(self) -> int:
        """Метод для підсчета коментарів до об'явлення"""
        return self.ad.comments.count()

    def __str__(self) -> str:
        return f"Коментар від {self.user.username} до {self.ad.title[:20]}"
