
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Номер телефону")
    bio = models.TextField(max_length=500, blank=True, verbose_name="Біографія")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата народження")
    location = models.CharField(max_length=100, blank=True, verbose_name="Місце проживання")
    avatar = models.ImageField(upload_to='profile_pics', null=True, blank=True, verbose_name="Аватар")

    def __str__(self):
        return f"Профіль користувача {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Щоразу, коли створюється новий User, для нього автоматично створюється UserProfile."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Щоразу, коли оновлюється модель User, автоматично зберігається і її профіль."""
    instance.user_profile.save()
