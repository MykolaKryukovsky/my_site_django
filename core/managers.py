
from django.db import models, connection
from django.db.models import Sum, Avg, Count
from typing import List, Dict, Any


class StatsQuerySet(models.QuerySet):
    """Кастомний QuerySet для повторно використовуваних методів фільтрації та обробки."""

    def active(self):
        """Повертає тільки активні записи (якщо у моделі є поле is_active)"""
        if hasattr(self.model, 'is_active'):
            return self.filter(is_active=True)
        return self

    def get_price_stats(self, price_field: str = 'price') -> Dict[str, Any]:
        """
        Універсальний метод для підрахунку статистики цін/витрат.
        Повертає словник із загальною сумою, середньою ціною та кількістю позицій.
        """
        return self.aggregate(
            total_sum=Sum(price_field),
            average_price=Avg(price_field),
            total_count=Count('id')
        )

    def get_counts_stats(self, *fields: str) -> Dict[str, Any]:
        """
        Універсальний метод для підрахунку унікальних значень.
        Приймає назви полів (наприклад, 'author', 'genre') і повертає кількість унікальних записів.
        """
        aggregations = {f'distinct_{field}': Count(field, distinct=True) for field in fields}
        aggregations['total_count'] = Count('id')
        return self.aggregate(**aggregations)


class CustomStatsManager(models.Manager.from_queryset(StatsQuerySet)):
    """
    Кастомний менеджер, який автоматично наслідує всі класичні методи QuerySet
    та додає ізольовані низькорівневі методи для виконання сирих SQL-запитів.
    """

    def get_popular_categories_raw(self) -> List[Dict[str, Any]]:
        """
        Універсальний кастомний SQL-запрос (Raw SQL).
        Автоматично визначає точні імена таблиць у базі даних, запобігаючи помилці 500,
        та повертає чистий список словників, повністю сумісний із шаблоном та тестами.
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
            LEFT JOIN {ad_table} a ON c.id = a.category_id AND a.is_active = TRUE
            GROUP BY c.id, c.name
            ORDER BY total_ads DESC
            LIMIT 5;
        """

        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            columns = [col[0] for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]


StatsManager = CustomStatsManager
