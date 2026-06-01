
from django.core.exceptions import ValidationError


def validate_corporate_email(value):
    """Перевіряє, чи є email корпоративним (забороняє публічні домени)."""
    forbidden_domains = ['gmail.com', 'yahoo.com', 'mail.ru', 'outlook.com']
    email_domain = value.split('@')[-1].lower()

    if email_domain in forbidden_domains:
        raise ValidationError(
            f"Реєстрація через сервіс {email_domain} заборонена. "
            "Використовуйте корпоративну пошту."
        )

def validate_file_size(value):
    """Обмежує максимальний розмір завантажуваного файлу (за замовчуванням 2 МБ)."""
    max_size = 2 * 1024 * 1024

    if value and value.size > max_size:
        raise ValidationError(f"Розмір файлу не повинен перевищувати {max_size // (1024 * 1024)} МБ.")
