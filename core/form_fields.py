
import re
from django import forms
from django.core.exceptions import ValidationError


class HexColorField(forms.CharField):
    """
    Кастомне поле форми для валідації HEX-коду кольору (наприклад: #FFFFFF або #333).
    Автоматично додає символ '#' на початок, якщо користувач його забув,
    та переводить символи у верхній регістр.
    """

    def to_python(self, value: str) -> str:
        """Очищає вхідні дані: прибирає зайві пробіли та додає '#'."""
        value = super().to_python(value)

        if not value:
            return value

        value = value.strip()

        if not value.startswith('#'):
            value = f"#{value}"

        return value.upper()

    def validate(self, value: str) -> None:
        """Перевіряє відповідність тексту стандарту HEX за допомогою регулярного виразу."""
        super().validate(value)

        if not value:
            return

        hex_regex = r'^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$'

        if not re.match(hex_regex, value):
            raise ValidationError(
                "Некоректний формат HEX-коду. Колір має виглядати як #FFF або #FF5733.",
                code='invalid_hex_color'
            )
