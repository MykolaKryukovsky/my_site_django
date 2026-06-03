
from django.urls import path
from . import views


app_name = 'main'


urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('services/', views.ServiceView.as_view(), name='services'),
    path('post/<int:id>/', views.post_view, name='post_detail'),
    path('event/<int:year>/<int:month>/<int:day>/', views.event_view, name='event_detail'),
]
