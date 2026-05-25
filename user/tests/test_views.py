
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class UserViewsTest(TestCase):
    """Набір інтеграційних тестів для перевірки логіки представлень (views.py)."""

    def setUp(self) -> None:
        """Підготовка базових даних: створення тестового користувача."""
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="old_password123"
        )
        self.register_url = reverse('register')
        self.edit_profile_url = reverse('edit_profile')
        self.change_password_url = reverse('change_password')
        self.delete_account_url = reverse('delete_account')
        self.profile_url = reverse('profile_view', kwargs={'username': self.user.username})

    def test_register_view_get_anonymous(self) -> None:
        """Перевірка, що анонімний користувач отримує сторінку реєстрації (код 200)."""
        response = self.client.get(self.register_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_register_view_get_authenticated_redirects(self) -> None:
        """Перевірка, що авторизованого користувача перенаправляє на його профіль."""
        self.client.force_login(self.user)

        response = self.client.get(self.register_url)

        self.assertRedirects(response, self.profile_url)

    def test_register_view_post_success(self) -> None:
        """Перевірка успішної реєстрації нового користувача через POST-запит."""
        form_data = {
            'username': 'new_member',
            'email': 'new_member@example.com',
            'password': 'securepassword123',
            'password_confirmation': 'securepassword123'
        }
        response = self.client.post(self.register_url, data=form_data)
        expected_redirect = reverse('profile_view', kwargs={'username': 'new_member'})

        self.assertRedirects(response, expected_redirect)
        self.assertTrue(User.objects.filter(username='new_member').exists())

    def test_edit_profile_view_login_required(self) -> None:
        """Перевірка, що неавторизованого користувача перенаправляє на сторінку входу (login)."""
        response = self.client.get(self.edit_profile_url)

        self.assertEqual(response.status_code, 302)

    def test_edit_profile_view_get(self) -> None:
        """Перевірка відображення форми редагування профілю для авторизованого користувача."""
        self.client.force_login(self.user)

        response = self.client.get(self.edit_profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')

    def test_edit_profile_view_post_success(self) -> None:
        """Перевірка успішного оновлення текстових даних профілю."""
        self.client.force_login(self.user)

        form_data = {
            'bio': 'Нова біографія для тесту',
            'location': 'Одеса'
        }
        response = self.client.post(self.edit_profile_url, data=form_data)

        self.assertRedirects(response, self.profile_url)
        self.user.user_profile.refresh_from_db()
        self.assertEqual(self.user.user_profile.bio, 'Нова біографія для тесту')
        self.assertEqual(self.user.user_profile.location, 'Одеса')

    def test_change_password_view_post_success(self) -> None:
        """Перевірка успішної зміни пароля авторизованого користувача."""
        self.client.force_login(self.user)

        form_data = {
            'old_password': 'old_password123',
            'new_password': 'brand_new_password_123',
            'confirm_password': 'brand_new_password_123'
        }
        response = self.client.post(self.change_password_url, data=form_data)

        self.assertRedirects(response, self.profile_url)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('brand_new_password_123'))

    def test_profile_view_success(self) -> None:
        """Перевірка успішного відображення сторінки існуючого профілю."""
        self.client.force_login(self.user)

        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_detail.html')
        self.assertEqual(response.context['target_user'], self.user)

    def test_profile_view_404_for_non_existing_user(self) -> None:
        """Перевірка повернення помилки 404, якщо користувача не існує."""
        self.client.force_login(self.user)

        invalid_profile_url = reverse('profile_view', kwargs={'username': 'does_not_exist'})
        response = self.client.get(invalid_profile_url)

        self.assertEqual(response.status_code, 404)

    def test_delete_account_view_get(self) -> None:
        """Перевірка відображення сторінки підтвердження видалення акаунту."""
        self.client.force_login(self.user)

        response = self.client.get(self.delete_account_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'confirm_delete.html')

    def test_delete_account_view_post_success(self) -> None:
        """Перевірка повного видалення облікового запису користувача через POST."""
        self.client.force_login(self.user)

        user_id = self.user.id
        response = self.client.post(self.delete_account_url)

        self.assertRedirects(response, self.register_url)
        self.assertFalse(User.objects.filter(id=user_id).exists())
