
from django.urls import path
from .views import SystemDashboardView


app_name = 'core'


urlpatterns = [
    path('', SystemDashboardView.as_view(), name='system_dashboard'),
]