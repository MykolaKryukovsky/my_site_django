from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from typing import Dict, Any

from ..forms import RegistrationForm, UserProfileForm, CustomPasswordChangeForm


class RegistrationFormTest(TestCase):
    """Набір тестів для перевірки форми реєстрації користувача RegistrationForm."""

    def setUp(self) -> None:
        """Підготовка початкових даних перед запуском кожного тесту."""
        self.existing_user = User.objects.create_user(
            username="existing_user",
            email="existing@example.com",
            password="password123"
        )

    def test_valid_registration_form(self) -> None:
        """Перевірка успішної валідації форми з коректними даними."""
        form_data = {
            'username': 'new_user',
            'email': 'new@example.com',
            'password': 'securepassword123',
            'password_confirmation': 'securepassword123',
            'phone_number': '+380991112233'  # Додано обов'язкове поле
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_save_creates_user(self) -> None:
        """Перевірка, що метод save() успішно створює та хешує пароль користувача."""
        form_data = {
            'username': 'created_user',
            'email': 'created@example.com',
            'password': 'securepassword123',
            'password_confirmation': 'securepassword123',
            'phone_number': '+380991112233'  # Додано обов'язкове поле
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

        user = form.save()
        self.assertEqual(user.username, 'created_user')
        self.assertTrue(user.check_password('securepassword123'))

    def test_duplicate_username_invalid(self) -> None:
        """Перевірка виведення помилки, якщо ім'я користувача вже зайняте."""
        form_data = {
            'username': 'existing_user',
            'email': 'unique@example.com',
            'password': 'password123',
            'password_confirmation': 'password123',
            'phone_number': '+380991112233'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertEqual(form.errors['username'][0], "Це ім'я користувача вже зайняте.")

    def test_duplicate_email_invalid(self) -> None:
        """Перевірка виведення помилки, якщо email вже зареєстрований."""
        form_data = {
            'username': 'unique_user',
            'email': 'existing@example.com',
            'password': 'password123',
            'password_confirmation': 'password123',
            'phone_number': '+380991112233'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'][0], 'Користувач з таким Email вже існує.')

    def test_passwords_do_not_match(self) -> None:
        """Перевірка невалідності форми, якщо паролі не збігаються."""
        form_data = {
            'username': 'unique_user',
            'email': 'unique@example.com',
            'password': 'password123',
            'password_confirmation': 'different_password',
            'phone_number': '+380991112233'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password_confirmation', form.errors)
        self.assertEqual(form.errors['password_confirmation'][0], 'Паролі не збігаються.')


class UserProfileFormTest(TestCase):
    """Набір тестів для перевірки форми профілю користувача UserProfileForm."""

    def test_valid_profile_form(self) -> None:
        """Перевірка успішної валідації форми профілю з коректними даними."""
        form_data = {
            'bio': 'Професійний розробник',
            'birth_date': '2000-01-01',
            'location': 'Львів'
        }
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_avatar_size_exceeds_limit(self) -> None:
        """Перевірка виведення помилки, якщо розмір аватара більший за 2 МБ."""
        large_file = SimpleUploadedFile(
            name="large_avatar.jpg",
            content=b"0" * (2 * 1024 * 1024 + 100),
            content_type="image/jpeg"
        )
        form_data = {'bio': 'Тест'}
        file_data = {'avatar': large_file}

        form = UserProfileForm(data=form_data, files=file_data)
        self.assertFalse(form.is_valid())
        self.assertIn('avatar', form.errors)
        self.assertEqual(form.errors['avatar'][0],'Завантажте коректне зображення. '
                         'Завантажений файл або не є зображенням, або пошкоджений.'
        )


class CustomPasswordChangeFormTest(TestCase):
    """Набір тестів для перевірки форми зміни пароля CustomPasswordChangeForm."""

    def setUp(self) -> None:
        """Створення тестового користувача для перевірки його поточного пароля."""
        self.user = User.objects.create_user(
            username="testuser",
            password="old_secure_password"
        )

    def test_valid_password_change(self) -> None:
        """Перевірка успішної зміни пароля за умови введення правильних даних."""
        form_data: Dict[str, str] = {
            'old_password': 'old_secure_password',
            'new_password': 'new_secure_password123',
            'confirm_password': 'new_secure_password123'
        }
        form = CustomPasswordChangeForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_incorrect_old_password(self) -> None:
        """Перевірка помилки, якщо користувач ввів неправильний поточний пароль."""
        form_data = {
            'old_password': 'wrong_password',
            'new_password': 'new_secure_password123',
            'confirm_password': 'new_secure_password123'
        }
        form = CustomPasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('old_password', form.errors)
        self.assertEqual(form.errors['old_password'][0], 'Поточний пароль вказано неправильно.')

    def test_new_password_is_same_as_old(self) -> None:
        """Перевірка помилки, якщо новий пароль такий самий, як і старий."""
        form_data = {
            'old_password': 'old_secure_password',
            'new_password': 'old_secure_password',
            'confirm_password': 'old_secure_password'
        }
        form = CustomPasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)
        self.assertEqual(form.errors['new_password'][0], 'Новий пароль повинен відрізнятися від старого.')

    def test_new_passwords_do_not_match(self) -> None:
        """Перевірка помилки, якщо новий пароль та підтвердження не збігаються."""
        form_data = {
            'old_password': 'old_secure_password',
            'new_password': 'new_secure_password123',
            'confirm_password': 'different_new_password'
        }
        form = CustomPasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('confirm_password', form.errors)
        self.assertEqual(form.errors['confirm_password'][0], 'Паролі не збігаються.')
