import time
import logging
from django.http import HttpRequest, HttpResponse
from django.core.cache import cache


logger = logging.getLogger('core_analytics')


class CustomHeaderMiddleware:
    """
    Кастомний Middleware, який додає службові заголовки безпеки
    та версии до кожної відповіді сервера.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        response['X-Project-Version'] = '1.0.4-Stable'
        response['X-Developer-Team'] = 'MySystem-Core'

        return response


class RequestMetricsMiddleware:
    """
    Middleware для підрахунку загальної кількості запитів на сервер за допомогою кэшу
    та централізованого логування активності користувачів у файл server_activity.log.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        total_requests = cache.get('global_request_metrics_count', 0)
        total_requests += 1
        cache.set('global_request_metrics_count', total_requests, timeout=None)
        response = self.get_response(request)

        if hasattr(request, 'user') and request.user.is_authenticated:
            user_status = f"User: {request.user.username}"
        else:
            user_status = "Anonymous"

        log_message = (
            f"Запит #{total_requests} | Метод: {request.method} | "
            f"Шлях: {request.path} | Статус: {response.status_code} | {user_status}"
        )
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        logger.info(log_message, extra={'add_time': current_time})

        return response
