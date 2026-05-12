
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from typing import Any, Type
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender: Type[User], instance: User, created: bool, **kwargs: Any) -> None:
    """
        Створює об'єкт UserProfile автоматично під час створення нового користувача.
        Args:
            sender: Клас моделі, що надіслала сигнал (User).
            instance: Конкретний екземпляр створеного користувача.
            created: Прапор, що вказує, чи було створено новий об'єкт (True) чи оновлено старий.
            **kwargs: Додаткові іменовані аргументи.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender: Type[User], instance: Any, **kwargs: Any) -> None:
    """
        Зберігає пов'язані дані профілю під час кожного збереження об'єкта користувача.
        Args:
            sender: Клас моделі, що надіслала сигнал (User).
            instance: Примірник користувача, який зберігається.
            **kwargs: Додаткові іменовані аргументи.
    """
    instance.profile.save()
