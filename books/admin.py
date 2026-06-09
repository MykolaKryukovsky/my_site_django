
from django.http import HttpRequest
from typing import Any

from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Кастомне налаштування відображення Книг в адмінці."""
    list_display = ('title', 'author', 'genre', 'publication_year', 'isbn', 'user', 'created_at')
    list_display_links = ('title', 'isbn')
    list_filter = ('genre', 'publication_year', 'created_at')
    search_fields = ('title', 'author', 'isbn', 'user__username')
    fieldsets = (
        ("Про книгу", {
            'fields': ('id', 'title', 'author', 'genre', 'publication_year', 'isbn')
        }),
        ("Системна інформація", {
            'fields': ('user', 'created_at')
        }),
    )
    readonly_fields = ('id', 'created_at')

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
