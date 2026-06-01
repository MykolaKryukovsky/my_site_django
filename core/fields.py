
from django.db import models


class UpperCaseCharField(models.CharField):
    """Кастомне поле, яке автоматично переводить текст у UPPERCASE."""
    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if value:
            value = value.upper()
            setattr(model_instance, self.attname, value)
        return value
