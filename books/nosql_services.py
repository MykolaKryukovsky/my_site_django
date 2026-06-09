from typing import List, Dict, Any
from django.conf import settings


class MongoDBBookService:
    """Сервісний шар для безпечної та високопродуктивної роботи з NoSQL (MongoDB)."""

    @staticmethod
    def get_collection():
        """Повертає поточну колекцію книг з налаштувань Django."""
        return settings.MONGO_BOOKS_COLLECTION

    @classmethod
    def insert_book_attributes(cls, book_id: str, title: str, attributes: Dict[str, Any]) -> str:
        """
        Безпечно записує книгу та її кастомні NoSQL атрибути.
        Захищено від ін'єкцій завдяки використанню структурованих BSON-документів.
        """
        collection = cls.get_collection()
        document = {
            "book_id": str(book_id),
            "title": title,
            "attributes": attributes  # Тут може бути будь-який вкладений JSON (колір, сторінки, вага)
        }
        result = collection.update_one(
            {"book_id": str(book_id)},
            {"$set": document},
            upsert=True
        )
        return str(result.upserted_id) if result.upserted_id else book_id

    @classmethod
    def get_book_by_id(cls, book_id: str) -> Dict[str, Any]:
        """Швидке читання одного документа за строгим індексованим полем."""
        collection = cls.get_collection()
        document = collection.find_one({"book_id": str(book_id)}, {"_id": 0})
        return document if document else {}

    @classmethod
    def get_all_books(cls) -> List[Dict[str, Any]]:
        """Вибірка всіх книг з NoSQL сховища."""
        collection = cls.get_collection()
        return list(collection.find({}, {"_id": 0}))
