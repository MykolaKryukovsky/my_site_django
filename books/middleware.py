from django.core.cache import cache
from django.http import HttpRequest, HttpResponse


class AnonymousBooksCacheMiddleware:
    """
    Кастомний Middleware для повного кешування HTML-сторінки каталогу книг
    виключно для анонімних (неавторизованих) відвідувачів.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.path == '/books/catalog/':
            is_anon = not request.user.is_authenticated if hasattr(request, 'user') else True

            if is_anon:
                cache_key = 'anonymous_books_page_cache'
                cached_response = cache.get(cache_key)

                if cached_response is not None:
                    return cached_response

                response = self.get_response(request)

                if response.status_code == 200:
                    cache.set(cache_key, response, timeout=300)
                return response

        return self.get_response(request)
