import time
from django.core.management.base import BaseCommand
from django.db.models import Avg, Count
from books.models import Book


class Command(BaseCommand):
    help = "Заміряє чисту швидкість виконання важкого аналітичного запиту ORM"

    def handle(self, *args, **options):
        list(Book.objects.annotate(Avg('reviews__rating')).values('id'))

        start_time = time.perf_counter()

        for _ in range(100):
            analytics = Book.objects.select_related('author_rel').annotate(
                total_reviews=Count('reviews'),
                average_rating=Avg('reviews__rating')
            ).order_by('-total_reviews', '-average_rating')
            list(analytics)

        end_time = time.perf_counter()
        total_execution_time = (end_time - start_time) * 1000  # у мілісекундах

        self.stdout.write(self.style.SUCCESS(
            f"⏱️ Сумарний час виконання 100 важких запитів з агрегацією: {total_execution_time:.2f} мс"
        ))
