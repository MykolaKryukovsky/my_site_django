
from django.contrib.auth.models import User
from django.db import models
import uuid

from core.fields import UpperCaseCharField
from core.managers import StatsManager


class Author(models.Model):
    """Модель автора книги."""
    name = models.CharField(max_length=255, verbose_name="Ім'я автора")

    def __str__(self) -> str:
        return self.name


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
    author_rel = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, related_name='books')

    objects = StatsManager()

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author_rel'], name='books_book_author_idx'),
            models.Index(fields=['genre'], name='books_book_genre_idx'),
        ]

    def __str__(self) -> str:
        if hasattr(self, 'author_rel') and self.author_rel and getattr(self.author_rel, 'name', None):
            return f"{self.title.upper()} — {self.author_rel.name}"

        if hasattr(self, 'author') and self.author:
            return f"{self.title.upper()} — {self.author}"
        return self.title.upper()


class Review(models.Model):
    """Model рецензии/отзыва к книге."""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    content = models.TextField(verbose_name="Текст рецензії")
    rating = models.IntegerField(default=5, verbose_name="Оцінка")

    class Meta:
        verbose_name = "Коментар"
        verbose_name_plural = "Коментарі"
        indexes = [
            models.Index(fields=['book'], name='books_review_book_idx'),
            models.Index(fields=['rating'], name='books_review_rating_idx'),
        ]

    def __str__(self) -> str:
        return f"Рецензія на {self.book.title} ({self.rating}/5)"
