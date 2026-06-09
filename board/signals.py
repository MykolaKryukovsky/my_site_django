
from typing import Any, Type
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Ad


@receiver(pre_save, sender=Ad)
def handle_ad_expiration_pre_save(sender: Type[Ad], instance: Ad, **kwargs: Any) -> None:
    """
    Сигнал СРАБАТЫВАЕТ ДО сохранения модели Ad в базу данных.

    Логика:
    Проверяет срок жизни объявления и меняет статус прямо в памяти.
    Это исключает бесконечную рекурсию и экономит один SQL-запрос на запись!
    """
    if hasattr(instance, 'deactivate_if_expired'):
        instance.deactivate_if_expired()


@receiver(post_save, sender=Ad)
def handle_ad_creation_post_save(sender: Type[Ad], instance: Ad, created: bool, **kwargs: Any) -> None:
    """
    Сигнал СРАБАТЫВАЕТ ПОСЛЕ успешного сохранения модели Ad.

    Логика:
    Если объявление создано впервые, отправляет email автору.
    """
    if created and instance.user and instance.user.email:
        send_mail(
            subject='Оголошення успішно створено',
            message=f'Вітаємо! Ваше оголошення "{instance.title}" успішно опубліковано на нашій платформі.',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'admin@board.com'),
            recipient_list=[instance.user.email],
            fail_silently=True,
        )
