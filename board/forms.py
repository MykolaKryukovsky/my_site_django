
from django import forms
from .models import Category, Ad
from core.form_fields import HexColorField


class CategoryCreateForm(forms.ModelForm):
    """
    Форма для створення та редагування категорії з валідацією HEX-коду.
    Повністю сумісна з універсальним form_snippet.html.
    """
    color = HexColorField(
        required=True,
        label="Колір категорії (HEX)",
        widget=forms.TextInput(attrs={'placeholder': '#FF5733'})
    )

    class Meta:
        model = Category
        fields = ['name', 'description', 'color']
        labels = {
            'name': 'Назва категорії',
            'description': 'Опис категорії',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Короткий опис того, які товари підходять сюди...'}),
            'name': forms.TextInput(attrs={'placeholder': 'Наприклад: Електроніка, Одяг'}),
        }

    def __init__(self, *args, **kwargs):
        """Автоматично обгортає всі поля в базові класи для Bootstrap-скрипта"""
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class AdForm(forms.ModelForm):
    """
    ДОДАНО: Форма для створення та редагування оголошень користувачами.
    Автоматично інтегрується з Bootstrap 5 та валідацією.
    """
    class Meta:
        model = Ad
        # Перевірте назви полів у вашій моделі Ad та скоригуйте цей список за потреби
        fields = ['title', 'category', 'price', 'description']
        labels = {
            'title': 'Заголовок оголошення',
            'category': 'Категорія товару',
            'price': 'Ціна (грн)',
            'description': 'Детальний опис',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Що ви продаєте?'}),
            'category': forms.Select(),
            'price': forms.NumberInput(attrs={'placeholder': '0.00', 'min': '0'}),
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Опишіть стан товару, комплектацію та умови доставки...'}),
        }

    def __init__(self, *args, **kwargs):
        """Динамічно додає Bootstrap класи до кожного типу інпуту оголошення"""
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
