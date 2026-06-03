from django.test import TestCase
from django.contrib.auth.models import User

from ..models import UserProfile


class UserProfileSignalsTest(TestCase):
    """Набір тестів для перевірки автоматичного спрацьовування сигналів моделі UserProfile."""

    def test_profile_created_automatically_on_user_creation(self) -> None:
        """Перевірка, що сигнал create_user_profile автоматично створює UserProfile для нового User."""
        self.assertFalse(UserProfile.objects.exists())

        user = User.objects.create_user(
            username="signaluser",
            password="securepassword123"
        )

        self.assertTrue(UserProfile.objects.filter(user=user).exists())

        profile = user.user_profile

        self.assertIsNotNone(profile)
        self.assertEqual(profile.user, user)

    def test_profile_saved_automatically_on_user_save(self) -> None:
        """Перевірка, що сигнал save_user_profile автоматично зберігає зміни профілю при збереженні User."""
        user = User.objects.create_user(
            username="updateuser",
            password="securepassword123"
        )
        profile = user.user_profile
        profile.bio = "Оновлена біографія через сигнал"
        user.email = "updateuser@example.com"
        user.save()  # Сигнал post_save должен автоматически вызвать profile.save() внутри себя

        fresh_profile = UserProfile.objects.get(id=profile.id)

        self.assertEqual(fresh_profile.bio, "Оновлена біографія через сигнал")
        self.assertEqual(user.email, "updateuser@example.com")
