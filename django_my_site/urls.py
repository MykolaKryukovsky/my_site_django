"""
URL configuration for django_my_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from board import views as board_views
from core.views import SystemDashboardView

from board.views_api import AdViewSet
from .api import api as ninja_api


router = DefaultRouter()
router.register(r'board-ads', AdViewSet, basename='board-ad-api')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('dashboard/', SystemDashboardView.as_view(), name='system_dashboard'),
    path('board/', include('board.urls')),
    path('accounts/', include('allauth.urls')),
    path('profile/', include('user.urls', namespace='user')),
    path('', include('books.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/', include(router.urls)),
    path('api/v2/', ninja_api.urls),
]

handler404 = 'user.views.custom_handler404'
handler500 = 'user.views.custom_handler500'

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)),] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
