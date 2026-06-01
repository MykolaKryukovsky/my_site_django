
from django.http import HttpRequest, HttpResponse
import logging
from django.core.cache import cache


class CustomHeaderMiddleware:
    """
    Кастомний Middleware, який додає службовий заголовок до кожної відповіді сервера.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        response['X-Project-Version'] = '1.0.4-Stable'
        response['X-Developer-Team'] = 'MySystem-Core'

        return response


logger = logging.getLogger('core_analytics')


class RequestMetricsMiddleware:
    """
    ДОБАВЛЕНО: Middleware для підрахунку загальної кількості запитів на сервер
    та логування активності користувачів у файл.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        total_requests = cache.get('global_request_metrics_count', 0)
        total_requests += 1
        cache.set('global_request_metrics_count', total_requests, timeout=None)
        user_status = request.user.username if request.user.is_authenticated else "Anonymous"
        log_message = (f"Запит #{total_requests} | Метод: {request.method} | "
                       f"Шлях: {request.path} | Користувач: {user_status}"
        )
        logger.info(log_message)
        response = self.get_response(request)

        return response
