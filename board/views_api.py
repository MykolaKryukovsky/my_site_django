
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Ad
from .serializers import AdSerializer, AdDetailSerializer
from .permissions import IsOwnerOrReadOnly


class AdViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD операцій над оголошеннями.
    Підтримує кастомні дозволи, фільтрацію, пошук та вкладені поля.
    """
    queryset = Ad.objects.all().order_by('-created_at')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'category': ['exact'],
        'is_active': ['exact'],
        'price': ['gte', 'lte'],
    }
    search_fields = ['title', 'description']

    def get_serializer_class(self):
        """Динамічно обираємо серіалізатор: для деталей — розгорнутий, для списку — компактний."""
        if self.action == 'retrieve':
            return AdDetailSerializer
        return AdSerializer

    def perform_create(self, serializer):
        """Автоматично прив'язуємо поточного користувача при створенні оголошення."""
        serializer.save(user=self.request.user)
