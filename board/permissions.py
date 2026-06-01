
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Дозвіл, який дозволяє редагувати об'єкт лише його власнику.
    Для безпечних методів (GET, HEAD, OPTIONS) доступ відкритий усім.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user
