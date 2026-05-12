
from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('edit/', views.edit_profile_view, name='edit_profile'),
    path('password/', views.change_password_view, name='change_password'),
    path('delete/', views.delete_account_view, name='delete_account'),
    path('<str:username>/', views.profile_view, name='profile_view'),
]
