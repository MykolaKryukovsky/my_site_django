
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book
from datetime import datetime


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class BookSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre', 'publication_year', 'isbn', 'created_at', 'user']

    def validate_publication_year(self, value):
        current_year = datetime.now().year
        if value <= 0:
            raise serializers.ValidationError("Рік видання не може бути негативним чи нульовим.")
        if value > current_year:
            raise serializers.ValidationError(f"Рік видання не може бути більшим за поточний ({current_year}).")
        return value

    def validate_isbn(self, value):
        clean_isbn = value.replace('-', '')
        if not clean_isbn.isdigit():
            raise serializers.ValidationError("ISBN має складатися лише з цифр та дефісів.")

        if len(clean_isbn) not in [10, 13]:
            raise serializers.ValidationError("Довжина ISBN має бути 10 або 13 цифр.")
        return value