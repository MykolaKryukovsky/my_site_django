from django.test import TestCase
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

from ..models import UserProfile


class UserProfileModelTest(TestCase):
    """Набір тестів для перевірки працездатності моделі UserProfile."""

    def setUp(self) -> None:
        """Підготовка початкових даних перед кожним тестом."""
        self.user = User.objects.create_user(username="testuser", password="securepassword123")
        self.profile, created = UserProfile.objects.get_or_create(user=self.user)
        self.profile.bio = "Розробник на Django."
        self.profile.location = "Київ"
        self.profile.save()

    def test_profile_creation_and_fields(self) -> None:
        """Перевірка коректності створення профілю та збереження значення його полів."""
        self.assertTrue(isinstance(self.profile, UserProfile))
        self.assertEqual(self.profile.bio, "Розробник на Django.")
        self.assertEqual(self.profile.location, "Київ")
        self.assertIsNone(self.profile.birth_date)
        self.assertFalse(bool(self.profile.avatar))

    def test_string_representation(self) -> None:
        """Перевірка правильної роботи магічного методу __str__ для текстового виводу."""
        expected_str = f"Профіль користувача {self.user.username}"
        self.assertEqual(str(self.profile), expected_str)

    def test_one_to_one_relationship_uniqueness(self) -> None:
        """Перевірка обмеження OneToOneField: у одного користувача може бути лише один профіль."""
        with self.assertRaises(IntegrityError):
            UserProfile.objects.create(user=self.user, bio="Другий профіль")

    def test_cascade_deletion(self) -> None:
        """Перевірка каскадного видалення: разом із користувачем має видалятися і його профіль."""
        profile_id = self.profile.id
        self.user.delete()

        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(id=profile_id)
