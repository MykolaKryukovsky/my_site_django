
from django.contrib import admin
from django.http import HttpRequest
from typing import Any
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
        Конфігурація адміністративної панелі Django для моделі Книги (Book).
        Визначає зовнішній вигляд таблиці книг, поля для пошуку,
        бічні фільтри, а також автоматизує заповнення поля автора запису.
    """
    list_display = ('title', 'author', 'genre', 'publication_year', 'isbn', 'user', 'created_at')
    list_display_links = ('title',)
    list_filter = ('genre', 'publication_year', 'created_at')
    search_fields = ('title', 'author', 'isbn')
    readonly_fields = ('id', 'created_at', 'user')
    ordering = ['-created_at']

    def save_model(self, request: HttpRequest, obj: Book, form: Any, change: bool) -> None:
        """
            Перевизначає логіку збереження моделі через адмінку.
            Якщо створюється нова книга (а не редагується стара), метод автоматично
            прив'язує поточного адміністратора, який заповнює форму, до поля `user`.
            Args:
                request (HttpRequest): Об'єкт поточного HTTP-запиту від адміністратора.
                obj (Book): Екземпляр моделі книги, що зберігається.
                form (Any): Форма адмін-панелі з даними.
                change (bool): Флаг, який дорівнює True, якщо об'єкт редагується, і False, якщо створюється.
        """
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)
