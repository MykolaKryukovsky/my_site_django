import csv
import io
from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import Book, Author


@shared_task(bind=True)
def import_books_from_csv_task(self, csv_data_str: str, user_id: int, recipient_email: str) -> str:
    """Асинхронна задача Celery для імпорту книг із файлу CSV."""
    csv_file = io.StringIO(csv_data_str)
    reader = csv.reader(csv_file)

    next(reader, None)

    user = User.objects.get(id=user_id) if user_id else None
    imported_count = 0

    for row in reader:
        if len(row) < 5:
            continue

        title, author_name, genre, year, isbn = row[0], row[1], row[2], row[3], row[4]

        author, _ = Author.objects.get_or_create(name=author_name)

        if not Book.objects.filter(isbn=isbn).exists():
            Book.objects.create(
                title=title,
                genre=genre,
                publication_year=int(year),
                isbn=isbn,
                author_rel=author,
                user=user
            )
            imported_count += 1

    subject = "Імпорт книг успішно завершено! 🎉"
    message = f"Вітаємо! Асинхронний імпорт книг закінчено.\nУспішно додано книг: {imported_count}."

    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[recipient_email],
        fail_silently=False,
    )

    return f"Успішно імпортовано книг: {imported_count}"
