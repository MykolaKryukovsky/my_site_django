
from rest_framework.pagination import PageNumberPagination


class BookPagination(PageNumberPagination):
    """
        Клас пагінації для розділення списку книг на сторінки.
        Забезпечує автоматичне розбиття великих масивів даних на порції,
        додаючи в JSON-відповідь службові метадані: загальну кількість записів (count),
        а також посилання на наступну (next) та попередню (previous) сторінки.
    """
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100
