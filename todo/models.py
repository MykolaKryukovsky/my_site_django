from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Не виконано'),
        ('completed', 'Виконано')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    