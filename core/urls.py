
from django.urls import path
from .views import SystemDashboardView


urlpatterns = [
    path('dashboard/', SystemDashboardView.as_view(), name='system_dashboard'),
]
