
from board.models import Ad
from books.models import Book


def global_site_stats(_request):
    """
    Контекстний процесор, який робить базову статистику сервісу
    доступною у будь-кому шаблоні проєкту.
    """
    active_ads_count = Ad.objects.active().count()
    total_books_count = Book.objects.count()

    return {
        'global_active_ads': active_ads_count,
        'global_total_books': total_books_count,
    }
