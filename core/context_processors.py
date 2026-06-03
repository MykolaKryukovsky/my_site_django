
from typing import Dict, Any
from django.http import HttpRequest
from django.core.cache import cache

from board.models import Ad
from books.models import Book


def global_site_stats(_request: HttpRequest) -> Dict[str, Any]:
    """
    Контекстний процесор, який робить базову статистику сервісу
    та метрики сервера доступними у будь-якому шаблоні проєкту автоматично.
    """
    active_ads_count = Ad.objects.active().count()
    total_books_count = Book.objects.count()
    total_server_requests = cache.get('global_request_metrics_count', 0)

    return {
        'global_active_ads': active_ads_count,
        'global_total_books': total_books_count,
        'total_server_requests': total_server_requests,  # 👈 Додано для відображення в base.html
    }
