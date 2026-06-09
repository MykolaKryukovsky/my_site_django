from django.test import SimpleTestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from ..forms import CSVUploadForm


class CSVUploadFormTest(SimpleTestCase):
    """Набір тестів для валідації форми CSVUploadForm."""

    def test_form_with_valid_file(self) -> None:
        """Перевірка успішної валідації при завантаженні коректного CSV файлу."""
        csv_file = SimpleUploadedFile("books.csv", b"title,author\nBook,Author", content_type="text/csv")
        form = CSVUploadForm(files={'csv_file': csv_file})
        self.assertTrue(form.is_valid())

    def test_form_without_file_invalid(self) -> None:
        """Перевірка, що форма не валідується без завантаженого файлу."""
        form = CSVUploadForm(files={})
        self.assertFalse(form.is_valid())
        self.assertIn('csv_file', form.errors)

    def test_form_automatically_adds_bootstrap_class(self) -> None:
        """Перевірка наявності Bootstrap класу у віджеті форми."""
        form = CSVUploadForm()
        self.assertEqual(form.fields['csv_file'].widget.attrs['class'], 'form-control')
