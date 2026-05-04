from django.urls import path, re_path
from . import views


urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),

    re_path(r'^post/(?P<id>\d+)/$', views.post_view, name='post_detail'),
    re_path(r'^profile/(?P<username>[a-zA-Z]+)/$',
            views.profile_view, name='profile_detail'
    ),
    re_path(r'^event/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
            views.event_view, name='event_detail'
    ),

    path('contact/', views.ContactView.as_view(), name='contact'),
    path('services/', views.ServiceView.as_view(), name='services'),
]
