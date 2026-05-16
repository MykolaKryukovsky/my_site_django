
from rest_framework import generics, permissions
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from .models import Book
from .serializers import BookSerializer, RegisterSerializer
from .pagination import BookPagination
from .permissions import IsAdminOrReadOnlyForDelete as AdminDel


class BookViewSet(viewsets.ModelViewSet):

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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
