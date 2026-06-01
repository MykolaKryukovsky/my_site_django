from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.cache import cache
from board.models import Ad, Category
from books.models import Book


class SystemDashboardView(TemplateView):
    """
    Class-Based View для відображення головної аналітичної панелі сайту.
    Використовує кастомні менеджери для збору агрегованих даних.
    """
    template_name = 'board/dashboard.html'

    def get_context_data(self, **kwargs):
        """Перевизначаємо метод для передачі розширеної статистики у шаблон."""
        context = super().get_context_data(**kwargs)
        context['ad_stats'] = Ad.objects.active().get_price_stats(price_field='price')
        context['book_stats'] = Book.objects.get_counts_stats('author', 'genre')
        context['popular_categories'] = Category.objects.get_popular_categories_raw()
        context['total_server_requests'] = cache.get('global_request_metrics_count', 0)

        return context
