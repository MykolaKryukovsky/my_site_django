from django.test import TestCase, RequestFactory
from django.core.cache import cache
from django.contrib.auth.models import User
from django.http import HttpResponse

from ..middleware import CustomHeaderMiddleware, RequestMetricsMiddleware


class MiddlewareTest(TestCase):
    """Набір інтеграційних тестів для перевірки роботи кастомних методів Middleware."""

    def setUp(self) -> None:
        """Підготовка базових даних: очищення кєшу перед кожним тестом."""
        cache.clear()
        self.user = User.objects.create_user(username="middleware_user", password="password123")
        self.factory = RequestFactory()
        self.dummy_get_response = lambda req: HttpResponse("OK", status=200)

    def test_custom_header_middleware_adds_headers(self) -> None:
        """Перевірка, що CustomHeaderMiddleware успішно додає кастомні заголовки до відповіді."""
        request = self.factory.get('/')
        middleware = CustomHeaderMiddleware(self.dummy_get_response)

        response = middleware(request)

        self.assertIn('X-Project-Version', response)
        self.assertEqual(response['X-Project-Version'], '1.0.4-Stable')

        self.assertIn('X-Developer-Team', response)
        self.assertEqual(response['X-Developer-Team'], 'MySystem-Core')

    def test_request_metrics_middleware_increments_cache(self) -> None:
        """Перевірка, що RequestMetricsMiddleware коректно рахує та зберігає кількість запитів у кєші."""
        self.assertEqual(cache.get('global_request_metrics_count', 0), 0)

        request = self.factory.get('/some-page/')
        request.user = self.user  # Емулюємо авторизованого користувача
        middleware = RequestMetricsMiddleware(self.dummy_get_response)

        middleware(request)
        self.assertEqual(cache.get('global_request_metrics_count'), 1)

        middleware(request)
        self.assertEqual(cache.get('global_request_metrics_count'), 2)

    def test_request_metrics_middleware_handles_anonymous_user(self) -> None:
        """Перевірка, що логіка підрахунку кєшу не падає, якщо користувач є анонімним."""
        request = self.factory.get('/public-catalogue/')

        middleware = RequestMetricsMiddleware(self.dummy_get_response)

        try:
            response = middleware(request)
            self.assertEqual(response.status_code, 200)
        except AttributeError as e:
            self.fail(f"RequestMetricsMiddleware впав з помилкою AttributeError для анонімного запиту: {str(e)}")

        self.assertEqual(cache.get('global_request_metrics_count'), 1)
