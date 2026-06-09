import time
import logging
from typing import Callable, Optional
from django.http import HttpRequest, HttpResponse
from django.http import Http404
from django.shortcuts import render


logger = logging.getLogger(__name__)


class AuditAccessMiddleware:
    """
    Проміжне програмне забезпечення для аудиту та логування доступу.
    Фіксує кожен запит до системи: IP-адресу, метод, шлях та статус користувача.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response: Callable[[HttpRequest], HttpResponse] = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Обробляє вхідний запит та логує інформацію про доступ."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR', '0.0.0.0')
        user_status = f"User: {request.user.username}" if request.user.is_authenticated else "Anonymous"
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        logger.info(
            f"[ACCESS] IP: {ip_address} | {user_status} | Method: {request.method} | Path: {request.path}",
            extra={'add_time': current_time}
        )
        response = self.get_response(request)

        return response


class ErrorHandlingMiddleware:
    """
    Проміжне програмне забезпечення для централізованої обробки помилок.
    Перехоплює виключення (500) та аналізує статус-коди для рендерингу кастомних сторінок помилок.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Обробляє запит та перевіряє статус-код відповіді на помилку 404."""
        response = self.get_response(request)

        if response.status_code == 404:
            logger.warning(f"[404 NOT FOUND] Path: {request.path} | IP: {request.META.get('REMOTE_ADDR')}")
            return render(request, 'errors/404.html', status=404)

        return response

    def process_exception(self, request: HttpRequest, exception: Exception) -> Optional[HttpResponse]:
        """Перехоплює будь-які необроблені виключення в коді views, повертаючи помилку 500."""
        if isinstance(exception, Http404):
            return None

        logger.critical(f"[500 SERVER ERROR] Path: {request.path} | Error: {str(exception)}", exc_info=True)

        return render(request, 'errors/500.html', status=500)
