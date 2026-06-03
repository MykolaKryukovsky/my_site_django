
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from typing import Any, Type
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    ВІДКОРИГОВАНО: Сигнал для автоматичного створення профілю користувача.
    Використовує get_or_create для повного запобігання помилкам UniqueViolation у тестах.
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Синхронізує та зберігає профіль при оновленні користувача."""
    if hasattr(instance, 'user_profile'):
        instance.user_profile.save()
