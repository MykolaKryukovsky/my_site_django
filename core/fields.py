
from django.db import models
from typing import Any


class UpperCaseCharField(models.CharField):
    """
    Кастомное поле символов, которое автоматически переводит
    любой входящий текст в верхний регистр (UPPERCASE) перед сохранением в БД.
    """

    def pre_save(self, model_instance: models.Model, add: bool) -> Any:
        value = super().pre_save(model_instance, add)
        if isinstance(value, str):
            value = value.upper()
            setattr(model_instance, self.attname, value)
        return value
