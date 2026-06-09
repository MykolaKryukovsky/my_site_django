
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet
from django.db.models import Model


class IsAdminOrReadOnlyForDelete(permissions.BasePermission):
    """
        Клас прав доступу для обмеження операції видалення об'єктів.
        Дозволяє виконання HTTP-методу `DELETE` виключно користувачам зі
        статусом адміністратора (is_staff). Усі інші типи запитів (GET, POST,
        PUT, PATCH) дозволяються без додаткових перевірок на рівні цього класу.
    """
    def has_object_permission(self, request: Request, view: ViewSet, obj: Model) -> bool:
        """
        Перевіряє, чи має користувач дозвіл на виконання операції над конкретним об'єктом.
        Args:
                request (Request): Об'єкт поточного HTTP-запиту від клієнта.
                view (ViewSet): Екземпляр контролера, який обробляє цей запит.
                obj (Model): Конкретний екземпляр моделі (книги), до якого здійснюється доступ.
        Returns:
                bool: True, якщо доступ дозволено, інакше False.
        """
        if request.method == 'DELETE':
            return bool(request.user and request.user.is_staff)
        return True
