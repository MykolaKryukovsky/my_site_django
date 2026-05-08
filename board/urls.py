
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index_view, name='index'),
    path('recent/', views.recent_ads_view, name='recent_ads'),
    path('category/<int:category_id>/', views.category_ads_view, name='category_ads'),
    path('ad/<int:ad_id>/', views.ad_detail_view, name='ad_detail'),
    path('profile/<str:username>/', views.user_profile_view, name='user_profile'),
    path('stats/', views.stats_view, name='stats'),
]
