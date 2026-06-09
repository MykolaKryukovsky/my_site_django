from decimal import Decimal
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Category, Ad


class AdAPITestCase(APITestCase):
    """Набір тестів для перевірки REST API (AdViewSet) застосунку board."""

    def setUp(self) -> None:
        """Підготовка базових даних перед кожним тестом API."""
        self.owner = User.objects.create_user(username="owner", password="password123")
        self.other_user = User.objects.create_user(username="other", password="password123")
        self.category = Category.objects.create(name="Меблі", description="Для дому")
        self.ad = Ad.objects.create(
            title="Стіл офісний",
            description="Зручний великий стіл.",
            price=Decimal("2500.00"),
            user=self.owner,
            category=self.category
        )
        self.list_url = reverse('board-ad-api-list')
        self.detail_url = reverse('board-ad-api-detail', kwargs={'pk': self.ad.pk})

    def test_get_ads_list_anonymous(self) -> None:
        """Перевірка, що анонімний користувач може отримати список оголошень (200 OK)."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_ad_detail_anonymous(self) -> None:
        """Перевірка отримання деталей конкретного оголошення."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("СТІЛ ОФІСНИЙ", response.data['title'].upper())

    def test_create_ad_anonymous_forbidden(self) -> None:
        """Перевірка, що аноніму заборонено створювати оголошення (401 Unauthorized)."""
        data = {
            "title": "Новий Стіл",
            "description": "Тестовий опис",
            "price": "1500.00",
            "category": self.category.id
        }
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_ad_authenticated_success(self) -> None:
        """Перевірка успішного створення оголошення авторизованим користувачем."""
        self.client.force_authenticate(user=self.owner)
        data = {
            "title": "Новий Диван",
            "description": "Дуже м'який диван.",
            "price": "9000.00",
            "category": self.category.id
        }
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ad.objects.get(id=response.data['id']).user, self.owner)

    def test_update_ad_by_owner_success(self) -> None:
        """Перевірка, що власник може оновити своє оголошення (200 OK)."""
        self.client.force_authenticate(user=self.owner)
        data = {"title": "Стіл комп'ютерний", "price": "2700.00", "description": "Опис", "category": self.category.id}
        response = self.client.put(self.detail_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_ad_by_other_user_forbidden(self) -> None:
        """Перевірка, що чужий користувач не може редагувати оголошення (403 Forbidden)."""
        self.client.force_authenticate(user=self.other_user)
        data = {"title": "Спроба зламу", "price": "1.00", "description": "Опис", "category": self.category.id}
        response = self.client.put(self.detail_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_ad_by_owner_success(self) -> None:
        """Перевірка успішного видалення свого оголошення власником (204 No Content)."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ad.objects.filter(pk=self.ad.pk).exists())

    def test_api_filtering_and_search(self) -> None:
        """Перевірка роботи вбудованої фільтрації та пошуку через API query-параметри."""
        response = self.client.get(self.list_url, {'search': 'Стіл'})
        self.assertEqual(len(response.data), 1)

        response = self.client.get(self.list_url, {'search': 'неіснуючий_текст'})
        self.assertEqual(len(response.data), 0)
