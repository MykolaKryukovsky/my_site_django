
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    bio = models.TextField(max_length=500, blank=True, verbose_name="Біографія")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата народження")
    location = models.CharField(max_length=100, blank=True, verbose_name="Місце проживання")
    avatar = models.ImageField(upload_to='profile_pics', null=True, blank=True, verbose_name="Аватар")

    def __str__(self):
        return f"Профіль користувача {self.user.username}"
