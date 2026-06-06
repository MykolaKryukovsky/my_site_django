import random
from django.core.management.base import BaseCommand
from books.models import Author, Book, Review


class Command(BaseCommand):
    help = ("Наповнює базу даних тестовими авторами, "
            "книгами та рецензіями для вимірювання продуктивності"
    )

    def handle(self, *args, **options):
        Review.objects.all().delete()
        Book.objects.all().delete()
        Author.objects.all().delete()

        authors = [Author.objects.create(name=f"Автор #{i}") for i in range(1, 11)]

        books = []
        for i in range(1, 51):
            author = random.choice(authors)
            book = Book.objects.create(
                title=f"Книга Сорту #{i}",
                genre=random.choice(["Наука", "Фантастика", "Драма", "Поезія"]),
                publication_year=random.randint(1900, 2026),
                isbn=f"978-0-00-0000{i:03d}",
                author_rel=author
            )
            books.append(book)

        for book in books:
            for j in range(1, 4):
                Review.objects.create(
                    book=book,
                    content=f"Чудова аналітика та глибокий зміст у рецензії №{j} для цієї книги.",
                    rating=random.randint(3, 5)
                )

        self.stdout.write(self.style.SUCCESS(f"Успішно створено: {Author.objects.count()} "
                f"авторів, {Book.objects.count()}"
                f" книг та {Review.objects.count()} рецензій!"
        ))
