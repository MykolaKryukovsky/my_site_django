
from django import forms
from .models import Category
from core.form_fields import HexColorField


class CategoryCreateForm(forms.ModelForm):
    """Форма для створення та редагування категорії з валідацією HEX-коду."""
    color = HexColorField(
        required=True,
        label="Колір категорії (HEX)",
        widget=forms.TextInput(attrs={'placeholder': '#FF5733', 'class': 'form-control'})
    )

    class Meta:
        model = Category
        fields = ['name', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
