import time
from typing import Any, Dict
from django.core.cache import cache
from rest_framework import generics, permissions, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import connection, reset_queries
from django.db.models import Avg, Count
from django.views.generic import ListView, FormView, View
from django.shortcuts import render, redirect
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpRequest, HttpResponse
from rest_framework.serializers import BaseSerializer
from celery.result import AsyncResult
from django.views.generic import TemplateView

from .nosql_services import MongoDBBookService

from .models import Book, Author
from .forms import CSVUploadForm
from .tasks import import_books_from_csv_task
from .serializers import BookSerializer, RegisterSerializer
from .pagination import BookPagination
from .permissions import IsAdminOrReadOnlyForDelete as AdminDel


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet для виконання CRUD операцій над моделею Книги (Book).
    Забезпечує автоматичне створення (POST), отримання списку (GET),
    перегляд деталей (GET), оновлення (PUT/PATCH) та видалення (DELETE) книг.
    Підтримує пагінацію, фільтрацію, пошук та сортування результатів.
    """
    queryset = Book.objects.all().select_related('user').order_by('-created_at')
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated, AdminDel]
    pagination_class = BookPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'genre': ['exact'],
        'publication_year': ['exact', 'gte', 'lte'],
        'isbn': ['exact'],
    }
    search_fields = ['title', 'author', 'genre']
    ordering_fields = ['publication_year', 'created_at']

    def perform_create(self, serializer: BaseSerializer) -> None:
        """
        Зберігає новий запис книги в базі даних.
        Автоматично прив'язує поточного автентифікованого користувача до поля `user`.
        """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def stats(self, request, *args, **kwargs):
        """
        Повертає статистику з урахуванням переданих в URL параметрів фільтрації.
        Приклад: /api/books/stats/?genre=Sci-Fi
        """
        queryset = self.get_queryset()
        filtered_queryset = self.filter_queryset(queryset)
        stats_data = filtered_queryset.get_counts_stats('author', 'genre')

        return Response(stats_data)


class RegisterView(generics.CreateAPIView):
    """
    API View для реєстрації нових користувачів у системі.
    Доступний для всіх відвідувачів (анонімних користувачів) без JWT-токена.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ORMPerformanceListView(ListView):
    """Класс-представление для демонстрации и сравнения производительности ORM."""
    model = Book
    template_name = 'books/orm_performance.html'
    context_object_name = 'books'

    def get_queryset(self):
        """
        Переопределяем базовый запрос.
        Здесь мы сразу возвращаем ОПТИМИЗИРОВАННЫЙ QuerySet (Вариант №2),
        чтобы класс использовал его по умолчанию при рендеринге.
        """
        return Book.objects.select_related('author_rel').prefetch_related('reviews')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Собираем метрики производительности и передаем их в контекст шаблона."""
        context = super().get_context_data(**kwargs)

        reset_queries()
        start_time_slow = time.perf_counter()

        books_slow = Book.objects.all()
        slow_data = []
        for book in books_slow:
            author_name = book.author_rel.name if book.author_rel else "Невідомо"
            reviews = [rev.content for rev in book.reviews.all()]
            slow_data.append({'title': book.title, 'author': author_name, 'reviews': reviews})

        slow_queries_count = len(connection.queries)
        slow_time = (time.perf_counter() - start_time_slow) * 1000

        reset_queries()
        start_time_fast = time.perf_counter()

        books_fast = self.get_queryset()
        fast_data = []
        for book in books_fast:
            author_name = book.author_rel.name if book.author_rel else "Невідомо"
            reviews = [rev.content for rev in book.reviews.all()]
            fast_data.append({'title': book.title, 'author': author_name, 'reviews': reviews})

        fast_queries_count = len(connection.queries)
        fast_time = (time.perf_counter() - start_time_fast) * 1000

        performance_boost = round(slow_time / fast_time, 1) if fast_time > 0 else 1

        context['slow_queries'] = slow_queries_count
        context['slow_time'] = round(slow_time, 2)
        context['fast_queries'] = fast_queries_count
        context['fast_time'] = round(fast_time, 2)
        context['boost'] = performance_boost
        context['books'] = fast_data

        return context


class CachedBooksListView(ListView):
    """Клас-представлення каталогу книг із низькорівневим API кешування Django."""
    model = Book
    template_name = 'books/cached_books.html'
    context_object_name = 'books'
    _is_from_cache = True

    def get_queryset(self):
        """
        Перевіряє наявність даних у кеші.
        Якщо кеш порожній — робить вибірку з БД та записує її в кеш.
        """
        cache_key = 'global_books_list_cache'
        books = cache.get(cache_key)

        if books is None:
            books = list(Book.objects.select_related('author_rel').all())
            cache.set(cache_key, books, timeout=300)
            self._is_from_cache = False
        else:
            self._is_from_cache = True

        return books

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Додає в контекст сторінки прапорець джерела даних (from_cache)."""
        context = super().get_context_data(**kwargs)
        context['from_cache'] = self._is_from_cache

        return context


class CSVImportView(FormView):
    """CBV для завантаження CSV та запуску асинхронної задачі Celery."""
    form_class = CSVUploadForm
    template_name = 'books/csv_import.html'

    def form_valid(self, form: CSVUploadForm) -> HttpResponse:
        csv_file = self.request.FILES['csv_file']

        csv_data_str = csv_file.read().decode('utf-8')

        user_id = self.request.user.id if self.request.user.is_authenticated else None
        user_email = self.request.user.email if user_id and self.request.user.email else "admin@example.com"

        task = import_books_from_csv_task.delay(csv_data_str, user_id, user_email)

        return redirect(reverse('books:task_status', kwargs={'task_id': task.id}))


class TaskStatusView(View):
    """CBV для відображення стану виконання задачі Celery."""

    def get(self, request: HttpRequest, task_id: str) -> HttpResponse:
        try:
            result = AsyncResult(task_id)
            status = result.status
            ready = result.ready()
            task_output = result.result if ready else None
        except Exception:
            status = 'PENDING'
            task_output = None

        context = {
            'task_id': task_id,
            'status': status,
            'result': task_output
        }
        return render(request, 'books/task_status.html', context)


class BookAnalyticsListView(ListView):
    """Класс-представление для отображения глубокой аналитики ORM (Агрегация и Аннотация)."""
    model = Book
    template_name = 'books/orm_analytics.html'
    context_object_name = 'books'

    def get_queryset(self):
        """
        Выбираем книги, подсчитываем количество отзывов и среднюю оценку для каждой,
        после чего сортируем их по количеству отзывов (DESC) и средней оценке (DESC).
        """
        return Book.objects.select_related('author_rel').annotate(
            total_reviews=Count('reviews'),
            average_rating=Avg('reviews__rating')
        ).order_by('-total_reviews', '-average_rating')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Добавляем в контекст аналитику по авторам."""
        context = super().get_context_data(**kwargs)

        # Аннотируем авторов: считаем количество их книг и средний рейтинг их произведений
        context['authors_analytics'] = Author.objects.annotate(
            total_books=Count('books', distinct=True),
            author_avg_rating=Avg('books__reviews__rating')
        ).order_by('-author_avg_rating')

        return context


class BookRawSQLListView(ListView):
    """Клас-представлення для демонстрації низькорівневих сирих SQL-запитів із захистом від ін'єкцій."""
    model = Author
    template_name = 'books/orm_raw_sql.html'
    context_object_name = 'authors'

    def get_queryset(self):
        """
        Запит 1: Вибираємо всіх авторів, які мають книги з більше ніж N відгуками.
        Використовуємо параметризацію %s для повної безпеки даних.
        """
        review_limit_str = self.request.GET.get('limit', '10')
        try:
            review_limit = int(review_limit_str)
        except ValueError:
            review_limit = 10

        sql_query = """
            SELECT a.id, a.name 
            FROM books_author a
            JOIN books_book b ON a.id = b.author_rel_id
            JOIN books_review r ON b.id = r.book_id
            GROUP BY a.id, a.name
            HAVING COUNT(r.id) > %s;
        """

        return Author.objects.raw(sql_query, [review_limit])

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Запит 2: Підрахунок загальної кількості книг за кожним жанром через connection.cursor()."""
        context = super().get_context_data(**kwargs)

        sql_genres_query = """
            SELECT genre, COUNT(id) AS total_books
            FROM books_book
            GROUP BY genre
            ORDER BY total_books DESC;
        """

        with connection.cursor() as cursor:
            cursor.execute(sql_genres_query)
            columns = [col[0] for col in cursor.description]
            genres_stats = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]

        context['genres_stats'] = genres_stats
        context['current_limit'] = self.request.GET.get('limit', '10')
        return context


class MongoDBBooksListView(TemplateView):
    """Контроллер для виведення та додавання динамічних атрибутів книг у NoSQL (MongoDB)."""
    template_name = 'books/nosql_catalog.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['nosql_books'] = MongoDBBookService.get_all_books()
        return context

    def post(self, request, *args, **kwargs):
        """Ендпоінт для створення книги з кастомними атрибутами."""
        title = request.POST.get('title', 'Невідома книга')
        book_id = request.POST.get('book_id', 'gen_id_123')

        attributes = {
            "cover_type": request.POST.get('cover_type', 'М\'яка'),
            "pages": int(request.POST.get('pages', 0)),
            "weight_g": int(request.POST.get('weight_g', 0)),
            "has_illustrations": request.POST.get('has_illustrations') == 'on'
        }

        MongoDBBookService.insert_book_attributes(book_id, title, attributes)
        return redirect(reverse('books:nosql_catalog'))
