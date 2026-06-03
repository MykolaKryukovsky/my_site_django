
from typing import Any, Dict
from django.views.generic import TemplateView
from django.core.cache import cache

from board.models import Ad, Category
from books.models import Book


class SystemDashboardView(TemplateView):
    """
    Class-Based View для відображення головної аналітичної панелі сайту.
    Збирає зведену статистику з усіх додатків системи та виводить її в реальному часі.
    """
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Перевизначаємо метод для передачі розширеної статистики у шаблон."""
        context = super().get_context_data(**kwargs)
        context['ad_stats'] = Ad.objects.get_price_stats()
        context['book_stats'] = Book.objects.get_counts_stats('author', 'genre')
        context['popular_categories'] = Category.objects.get_popular_categories_raw()
        context['total_server_requests'] = cache.get('global_request_metrics_count', 0)

        return context
