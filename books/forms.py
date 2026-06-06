from django import forms


class CSVUploadForm(forms.Form):
    """Форма для завантаження файлу CSV та автоматичного рендерингу."""
    csv_file = forms.FileField(
        label="Оберіть файл CSV",
        widget=forms.ClearableFileInput(attrs={'accept': '.csv'})
    )

    def __init__(self, *args, **kwargs):
        """Автоматично додає Bootstrap класи до інпуту"""
        super().__init__(*args, **kwargs)
        self.fields['csv_file'].widget.attrs.update({'class': 'form-control'})
