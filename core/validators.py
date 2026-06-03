
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile


def validate_corporate_email(value: str) -> None:
    """
    Перевіряє, чи є email корпоративним (забороняє публічні домени).
    Захищає систему від реєстрації проектних команд через безкоштовні поштові сервіси.
    """
    forbidden_domains = [
        'gmail.com', 'yahoo.com', 'mail.ru', 'outlook.com',
        'ukr.net', 'icloud.com', 'yandex.ru', 'hotmail.com'
    ]

    if not value or '@' not in value:
        raise ValidationError("Некоректна адреса електронної пошти.")

    email_domain = value.split('@')[-1].lower()

    if email_domain in forbidden_domains:
        raise ValidationError(
            f"Реєстрація через сервіс {email_domain} заборонена. "
            "Будь ласка, використовуйте вашу робочу корпоративну пошту."
        )


def validate_file_size(value: UploadedFile) -> None:
    """
    Обмежує максимальний розмір завантажуваного файлу (за замовчуванням 2 МБ).
    Захищає диск сервера від переповнення при завантаженні аватарів користувачів.
    """
    if not value:
        return

    max_size = 2 * 1024 * 1024  # 2 Мегабайти в байтах

    if value.size > max_size:
        max_size_mb = max_size // (1024 * 1024)
        raise ValidationError(f"Розмір файлу занадто великий. Він не повинен перевищувати {max_size_mb} МБ.")
