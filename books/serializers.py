
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book
from datetime import datetime
from typing import Any, Dict


class RegisterSerializer(serializers.ModelSerializer):
    """
        Серіалізатор для реєстрації нових користувачів через API.
        Забезпечує валідацію полів username, email таpassword, а також
        безпечне створення користувача із хэшуванням пароля в базі даних.
    """
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data: Dict[str, Any]) -> User:
        """
            Створює та повертає нового користувача з зашифрованим паролем.
            Args:
                validated_data (Dict[str, Any]): Словник перевірених та валідованих даних користувача.
            Returns:
                 User: Екземпляр створеного користувача системи.
        """

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class BookSerializer(serializers.ModelSerializer):
    """
        Серіалізатор для керування даними книг (Book) у REST API.
        Переводить об'єкти бази даних у формат JSON для клієнта та виконує
        сувору бізнес-валідацію вхідних даних при створенні чи оновленні книг.
    """
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre', 'publication_year', 'isbn', 'created_at', 'user']

    def validate_publication_year(self, value: int) -> int:
        """
            Перевіряє коректність вказаного року видання книги.
            Рік не може бути меншим або рівним нулю, а також не може перевищувати поточний календарний рік.
            Args:
                value (int): Рік видання, надісланий у запиті.
            Returns:
                int: Валідоване значення року видання.
            Raises:
                serializers.ValidationError: Якщо рік не проходить перевірку.
        """
        current_year = datetime.now().year
        if value <= 0:
            raise serializers.ValidationError("Рік видання не може бути негативним чи нульовим.")
        if value > current_year:
            raise serializers.ValidationError(f"Рік видання не може бути більшим за поточний ({current_year}).")
        return value

    def validate_isbn(self, value: str) -> str:
        """
            Перевіряє міжнародний стандартний номер книги (ISBN).
            Очищує рядок від дефісів та перевіряє, щоб номер складався виключно
            з цифр і мав фіксовану довжину у 10 або 13 символів.
            Args:
                value (str): Рядок із кодом ISBN з запиту.
            Returns:
                str: Оригінальний валідований рядок ISBN.
            Raises:
                serializers.ValidationError: Якщо формат або довжина ISBN не відповідають стандарту.
        """
        clean_isbn = value.replace('-', '')
        if not clean_isbn.isdigit():
            raise serializers.ValidationError("ISBN має складатися лише з цифр та дефісів.")

        if len(clean_isbn) not in [10, 13]:
            raise serializers.ValidationError("Довжина ISBN має бути 10 або 13 цифр.")
        return value
