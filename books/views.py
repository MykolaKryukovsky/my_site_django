
from rest_framework import generics, permissions, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from rest_framework.serializers import BaseSerializer
from .models import Book
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

    queryset = Book.objects.all().order_by('-created_at')
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated, AdminDel]
    pagination_class = BookPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = {
        'author': ['icontains'],
        'genre': ['exact', 'icontains'],
        'publication_year': ['exact', 'gte', 'lte'],
        'isbn': ['exact'],
    }
    search_fields = ['title']

    def perform_create(self, serializer: BookSerializer) -> None:
        """
            Зберігає новий запис книги в базі даних.
            Автоматично прив'язує поточного автентифікованого користувача
            (автора запиту) до поля `user` створюваної книги.
            Args:
                serializer (BaseSerializer): Екземпляр серіалізатора з валідованими даними.
        """
        serializer.save(user=self.request.user)


class RegisterView(generics.CreateAPIView):
    """
        API View для реєстрації нових користувачів у системі.
        Доступний для всіх відвідувачів (анонімних користувачів) без
        необхідності передачі JWT-токена авторизації.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
