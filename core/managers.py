from django.db import models
from django.db.models import Sum, Avg, Count
from django.core.exceptions import ValidationError


class StatsQuerySet(models.QuerySet):
    """Кастомний QuerySet для повторно використовуваних методів фільтрації та обробки."""

    def active(self):
        """Повертає тільки активні записи (якщо у моделі є поле is_active)"""
        if hasattr(self.model, 'is_active'):
            return self.filter(is_active=True)
        return self

    def get_price_stats(self, price_field='price'):
        """
        Універсальний метод для підрахунку статистики цін/витрат.
        Повертає словник із загальною сумою, середньою ціною та кількістю позицій.
        """
        return self.aggregate(
            total_sum=Sum(price_field),
            average_price=Avg(price_field),
            total_count=Count('id')
        )

    def get_counts_stats(self, *fields):
        """
        Універсальний метод для підрахунку унікальних значень.
        Приймає назви полів (наприклад, 'author', 'genre') і повертає кількість унікальних записів.
        """
        aggregations = {f'distinct_{field}': Count(field, distinct=True) for field in fields}
        aggregations['total_count'] = Count('id')
        return self.aggregate(**aggregations)

    def get_popular_categories_raw(self):
        """
        Універсальний кастомний SQL-запрос (Raw SQL).
        Автоматично визначає точні імена таблиць у базі даних, запобігаючи помилці 500.
        """
        try:
            category_table = self.model._meta.db_table
            ad_table = self.model.ads.field.model._meta.db_table
        except AttributeError:
            category_table = "board_category"
            ad_table = "board_ad"

        sql_query = f"""
            SELECT c.id, c.name, COUNT(a.id) AS total_ads
            FROM {category_table} c
            LEFT JOIN {ad_table} a ON c.id = a.category_id
            GROUP BY c.id, c.name
            ORDER BY total_ads DESC
            LIMIT 5;
        """

        return self.model.objects.raw(sql_query)


StatsManager = models.Manager.from_queryset(StatsQuerySet)
