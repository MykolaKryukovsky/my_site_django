
from rest_framework import permissions


class IsAdminOrReadOnlyForDelete(permissions.BasePermission):
    """
        Дозволяє видалення (DELETE) лише суперкористувачам/адміністраторам.
        Інші CRUD-операції доступні всім автентифікованим користувачам.
    """
    def has_object_permission(self, request, view, obj):

        if request.method == 'DELETE':
            return bool(request.user and request.user.is_staff)
        return True
