
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Ad, Category, Comment


class UserNestedSerializer(serializers.ModelSerializer):
    """Вкладений серіалізатор для виведення інформації про автора."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class CategoryNestedSerializer(serializers.ModelSerializer):
    """Вкладений серіалізатор для виведення інформації про категорію."""
    class Meta:
        model = Category
        fields = ['id', 'name']


class CommentNestedSerializer(serializers.ModelSerializer):
    """Вкладений серіалізатор для виведення списку коментарів."""
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']


class AdSerializer(serializers.ModelSerializer):
    """Базовий серіалізатор для списку оголошень (компактний варіант для загальної стрічки)."""
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Ad
        fields = '__all__'
        read_only_fields = ['user']


class AdDetailSerializer(serializers.ModelSerializer):
    """Глибокий серіалізатор для детального перегляду оголошення з усіма вкладеними даними."""
    user = UserNestedSerializer(read_only=True)
    category = CategoryNestedSerializer(read_only=True)
    comments = CommentNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Ad
        fields = [
            'id', 'title', 'description', 'price', 'is_active',
            'created_at', 'updated_at', 'user', 'category', 'comments'
        ]
