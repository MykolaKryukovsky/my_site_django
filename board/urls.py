from django.urls import path, include

from rest_framework.routers import DefaultRouter
from . import views
from .views_api import AdViewSet


router = DefaultRouter()
router.register(r'ads', AdViewSet, basename='ad-api')

urlpatterns = [
    path('list/', views.index_view, name='index_view'),
    path('recent/', views.recent_ads_view, name='recent_ads'),
    path('category/<int:category_id>/', views.category_ads_view, name='category_ads'),
    path('ad/<int:ad_id>/', views.ad_detail_view, name='ad_detail'),
    path('profile/<str:username>/', views.user_profile_view, name='user_profile'),
    path('stats/', views.stats_view, name='stats'),
    path('api/', include(router.urls)),
]