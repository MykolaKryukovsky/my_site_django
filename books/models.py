
from django.contrib.auth.models import User
from django.db import models
import uuid

from core.fields import UpperCaseCharField
from core.managers import StatsManager


class Book(models.Model):
    """
    Модель для представлення книги в бібліотечній системі.
    Зберігає детальну інформацію про книгу, включаючи її назву, автора,
    рік видання, унікальний код ISBN, дату додавання до системи, а також
    посилання на користувача, який створив цей запис.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = UpperCaseCharField(max_length=200, verbose_name="Назва книги")
    author = models.CharField(max_length=255, verbose_name="Автор")
    genre = models.CharField(max_length=100, verbose_name="Жанр")
    publication_year = models.IntegerField(verbose_name="Рік видання")
    isbn = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Хто створив")

    objects = StatsManager()

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.title} — {self.author}"
