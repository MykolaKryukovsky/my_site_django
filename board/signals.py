
from typing import Any, Type

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Ad


@receiver(post_save, sender=Ad)
def handle_ad_creation(sender: Type[Ad], instance: Ad, created: bool, **kwargs: Any) -> None:
    """
    Сигнал для обробки подій після збереження моделі Ad.

    Аргументи:
    sender (Type[Ad]): Клас моделі, що надіслав сигнал.
    instance (Ad): Конкретний екземпляр створеного/зміненого оголошення.
    created (bool): Прапор: True, якщо створено запис, False — якщо оновлено.
    **kwargs: Додаткові параметри (raw, using, update_fields).

    Логіка:
    1. Якщо оголошення створено вперше, надсилає email автору.
    2. Перевіряє термін життя оголошення та деактивує його, якщо воно старше 30 днів.
    """
    if created:
        send_mail(
            subject='Оголошення створено',
            message=f'Ваше оголошення "{instance.title}" успішно опубліковано!',
            from_email='admin@board.com',
            recipient_list=[instance.user.email],
            fail_silently=True,
        )

    post_save.disconnect(handle_ad_creation, sender=Ad)
    try:
        instance.deactivate_if_expired()
    finally:
        post_save.connect(handle_ad_creation, sender=Ad)
