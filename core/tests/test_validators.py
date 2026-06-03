from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from ..validators import validate_corporate_email, validate_file_size


class CoreValidatorsTest(SimpleTestCase):
    """Набір ізольованих тестів для перевірки кастомних валідаторів безпеки застосунку core."""

    def test_validate_corporate_email_valid(self) -> None:
        """Перевірка, що валідатор успішно пропускає справжні корпоративні email-адреси."""
        try:
            validate_corporate_email("developer@company.com")
            validate_corporate_email("manager@it-firm.ua")
        except ValidationError:
            self.fail("Валідатор помилково заблокував валідну корпоративну пошту!")

    def test_validate_corporate_email_forbidden_domains(self) -> None:
        """Перевірка, що валідатор блокує популярні публічні домени (gmail, ukr.net тощо)."""
        forbidden_emails = [
            "user@gmail.com",
            "test@ukr.net",
            "client@outlook.com",
            "worker@icloud.com"
        ]

        for email in forbidden_emails:
            with self.assertRaises(ValidationError) as context:
                validate_corporate_email(email)
            self.assertIn("заборонена", context.exception.message)

    def test_validate_corporate_email_invalid_format(self) -> None:
        """Перевірка викидання помилки при передачі зовсім некоректного формату пошти."""
        with self.assertRaises(ValidationError):
            validate_corporate_email("plain_text_without_at")
        with self.assertRaises(ValidationError):
            validate_corporate_email("")

    def test_validate_file_size_valid(self) -> None:
        """Перевірка, що файл розміром менше або рівно 2 МБ успішно проходить валідацію."""
        valid_file = SimpleUploadedFile(
            name="avatar.png",
            content=b"0" * (1 * 1024 * 1024),
            content_type="image/png"
        )
        try:
            validate_file_size(valid_file)
        except ValidationError:
            self.fail("Валідатор помилково заблокував файл дозволеного розміру!")

    def test_validate_file_size_exceeds_limit(self) -> None:
        """Перевірка, що файл розміром більше 2 МБ блокується валідатором."""
        large_file = SimpleUploadedFile(
            name="huge_photo.jpg",
            content=b"0" * (2 * 1024 * 1024 + 500),
            content_type="image/jpeg"
        )

        with self.assertRaises(ValidationError) as context:
            validate_file_size(large_file)
        self.assertIn("не повинен перевищувати 2 МБ", context.exception.message)

    def test_validate_file_size_handles_none_safely(self) -> None:
        """Перевірка стійкості валідатора, якщо файл не був переданий (None)."""
        try:
            validate_file_size(None)
        except Exception as e:
            self.fail(f"Валідатор впав з критичною помилкою {str(e)} при отриманні None!")
