
from django.urls import path
from . import views


app_name = 'user'


urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('edit/', views.edit_profile_view, name='edit_profile'),
    path('password/', views.change_password_view, name='change_password'),
    path('delete/', views.delete_account_view, name='delete_account'),
    path('team/create/', views.create_project_team_view, name='create_project_team'),
    path('u/<str:username>/', views.profile_view, name='profile_view'),
    path('cookie-demo/', views.cookie_session_demo_view, name='cookie_demo'),
    path('cookie-demo/clear/', views.clean_cookie_session_view, name='clear_cookie_demo'),
]
