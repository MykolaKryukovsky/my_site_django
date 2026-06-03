from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from ..form_fields import HexColorField


class HexColorFieldTest(SimpleTestCase):
    """Набір ізольованих тестів для перевірки логіки валідації поля HexColorField."""

    def test_valid_hex_formats(self) -> None:
        """Перевірка, що поле успішно пропускає стандартні формати HEX-кодів (3 або 6 символів)."""
        field = HexColorField()

        self.assertEqual(field.clean("#FFF"), "#FFF")
        self.assertEqual(field.clean("#FF5733"), "#FF5733")
        self.assertEqual(field.clean("#0d6efd"), "#0D6EFD")  # Має автоматично перевести у верхній регістр

    def test_auto_adds_hash_symbol_if_missing(self) -> None:
        """Перевірка, що поле автоматично додає символ '#' на початок, якщо користувач його забув."""
        field = HexColorField()

        self.assertEqual(field.clean("333"), "#333")
        self.assertEqual(field.clean("ff5733"), "#FF5733")

    def test_strips_whitespace_safely(self) -> None:
        """Перевірка, що поле автоматично прибирає випадкові пробіли навколо тексту."""
        field = HexColorField()

        self.assertEqual(field.clean("  #333  "), "#333")
        self.assertEqual(field.clean("  ff5733  "), "#FF5733")

    def test_invalid_hex_formats_raise_error(self) -> None:
        """Перевірка, що некоректні формати довжини або символів викликають ValidationError."""
        field = HexColorField()
        invalid_inputs = [
            "invalid",
            "#FF573",
            "FF57333",
            "#GG1234",
        ]

        for invalid_input in invalid_inputs:
            with self.assertRaises(ValidationError) as context:
                field.clean(invalid_input)
            self.assertEqual(context.exception.code, 'invalid_hex_color')

    def test_handles_empty_values_if_not_required(self) -> None:
        """Перевірка, що необов'язкове поле коректно повертає порожній рядок без помилок."""
        field = HexColorField(required=False)
        self.assertEqual(field.clean(""), "")
        self.assertEqual(field.clean(None), "")
