from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Book


@receiver(post_save, sender=Book)
@receiver(post_delete, sender=Book)
def invalidate_book_cache(sender, instance, **kwargs):
    """
    Автоматично очищає кєш списку книг при будь-якій модифікації даних.
    Очищає як загальний кєш списку, так і індивідуальні кєші сторінок анонімів.
    """
    cache.delete('global_books_list_cache')
    cache.delete('anonymous_books_page_cache')
