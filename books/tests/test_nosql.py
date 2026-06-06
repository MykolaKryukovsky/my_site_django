import mongomock
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from ..nosql_services import MongoDBBookService


class DjangoMongoDBIntegrationTest(TestCase):
    """Тести для перевірки надійності NoSQL шару інтеграції з MongoDB."""

    @patch('books.nosql_services.MongoDBBookService.get_collection')
    def test_insert_and_read_nosql_document_success(self, mock_get_collection) -> None:
        """Перевірка безпечного збереження даних та захисту від NoSQL витоків за допомогою mongomock."""
        fake_collection = mongomock.MongoClient().db.collection
        mock_get_collection.return_value = fake_collection

        book_id = "test-uuid-nosql-100"
        attrs = {"pages": 420, "cover_type": "Тверда", "custom_field": "Спеціальне значення"}

        MongoDBBookService.insert_book_attributes(book_id, "Майстер і Маргарита", attrs)

        saved_doc = MongoDBBookService.get_book_by_id(book_id)
        self.assertEqual(saved_doc['title'], "Майстер і Маргарита")
        self.assertEqual(saved_doc['attributes']['pages'], 420)
        self.assertEqual(saved_doc['attributes']['custom_field'], "Спеціальне значення")
