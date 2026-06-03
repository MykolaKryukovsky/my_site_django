from django.test import TestCase
from django.urls import reverse


class MainViewsTest(TestCase):
    """Набір інтеграційних тестів для перевірки логіки представлень застосунку main."""

    def test_home_view_html_content(self) -> None:
        """Перевіряє успішне відображення головної сторінки."""
        url = reverse('main:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/home.html')

    def test_about_view_html_tags(self) -> None:
        """Перевіряє відображення сторінки 'Про нас'."""
        url = reverse('main:about')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/about.html')

    def test_post_view_html_dynamic_id(self) -> None:
        """Перевіряє успішне відображення сторінки поста."""
        url = reverse('main:post_detail', kwargs={'id': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/post.html')

    def test_event_view_contains_date_parameters(self) -> None:
        """Перевірка відображення сторінки подій."""
        url = reverse('main:event_detail', kwargs={'year': 2026, 'month': 12, 'day': 25})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/event.html')

    def test_contact_view_html_cbv_data(self) -> None:
        """Перевірка відображення контактних даних Class-Based View."""
        url = reverse('main:contact')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/contact.html')

    def test_service_view_without_filter(self) -> None:
        """Перевірка, що ServiceView повертає список послуг."""
        url = reverse('main:services')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/services.html')

    def test_service_view_html_filter_results(self) -> None:
        """Перевіряє успішність запиту послуг з фільтром."""
        url = reverse('main:services')
        response = self.client.get(url, {'q': 'SEO'})
        self.assertEqual(response.status_code, 200)

    def test_service_view_with_filter_empty(self) -> None:
        """Перевірка порожнього результату фільтрації."""
        url = reverse('main:services')
        response = self.client.get(url, {'q': 'not_existing_service_name'})
        self.assertEqual(response.status_code, 200)
