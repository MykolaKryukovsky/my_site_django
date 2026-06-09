from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Category
from ..forms import CategoryCreateForm, AdForm


class BoardFormsTest(TestCase):
    """Набір тестів для перевірки валідації форм застосунку board."""

    def setUp(self) -> None:
        """Підготовка початкових даних для тестів форм."""
        self.user = User.objects.create_user(username="form_user", password="password123")
        self.category = Category.objects.create(
            name="Книги",
            description="Паперові та електронні книги",
            color="#000000"
        )

    def test_category_create_form_valid(self) -> None:
        """Перевірка успішної валідації форми категорії з коректними даними."""
        form_data = {
            'name': 'Спорт і відпочинок',
            'description': 'Товари для активного туризму.',
            'color': '#FF5733'
        }
        form = CategoryCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_category_create_form_invalid_hex(self) -> None:
        """Перевірка невалідності форми категорії при некоректному HEX-кольорі."""
        form_data = {
            'name': 'Нова категорія',
            'description': 'Опис',
            'color': 'invalid-color'  # Некоректне значення для HEX-поля
        }
        form = CategoryCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('color', form.errors)

    def test_ad_form_valid(self) -> None:
        """Перевірка успішної валідації форми оголошення з коректними даними."""
        form_data = {
            'title': 'Продам підручник з Python',
            'category': self.category.id,
            'price': '450.00',
            'description': 'Книга у відмінному стані, без поміток.'
        }
        form = AdForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_ad_form_invalid_price(self) -> None:
        """Перевірка, що форма оголошення блокує від'ємну ціну."""
        form_data = {
            'title': 'Безкоштовний товар',
            'category': self.category.id,
            'price': '-50.00',  # Валідатор моделі або налаштування відсічуть від'ємну ціну
            'description': 'Опис товару.'
        }
        form = AdForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_ad_form_bootstrap_classes(self) -> None:
        """Перевірка, що __init__ форми автоматично додає класи Bootstrap до віджетів."""
        form = AdForm()
        self.assertEqual(form.fields['title'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['price'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['category'].widget.attrs['class'], 'form-select')
