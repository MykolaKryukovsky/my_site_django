
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import BookViewSet, RegisterView


app_name = 'books'


router = SimpleRouter()
router.register(r'books', BookViewSet, basename='book')


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register/', RegisterView.as_view(), name='auth_register'),
]
