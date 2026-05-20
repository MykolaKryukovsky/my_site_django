
from django import forms
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from typing import Any, Dict, Optional, Type
from user.models import UserProfile
import re


class RegistrationForm(forms.ModelForm):
    """
        Форма для реєстрації нового користувача.
        Включає перевірку унікальності імені та email, а також збіг паролів.
    """

    email = forms.EmailField(required=True, label='Email')
    password = forms.CharField(widget=forms.PasswordInput(), label='Password')
    password_confirmation = forms.CharField(widget=forms.PasswordInput(), label='Password Confirmation')

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def clean_username(self) -> str:
        """Перевіряє, чи не зайняте ім'я користувача."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Username already exists')
        return username

    def clean_email(self) -> str:
        """Перевіряє унікальність адреси електронної пошти."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email already exists')
        return email

    def clean_password(self) -> Dict[str, Any]:
        """Перевіряє, чи збігаються паролі."""
        cleaned_data = super().clean()
        password = self.cleaned_data.get('password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if password != password_confirmation:
            raise ValidationError('Passwords do not match')
        return cleaned_data

    def save(self, commit: bool = True) -> User:
        """Створює користувача через create_user для хешування пароля."""
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        return user


class UserProfileForm(forms.ModelForm):
    """
        Форма для оновлення додаткової інформації профілю користувача.
    """

    class Meta:
        model = UserProfile

        fields = ['bio', 'birth_date', 'location', 'avatar']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4})
        }

    def clean_avatar(self) -> Any:
        """Перевіряє, щоб розмір аватара не перевищував 2 МБ."""
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            max_size = 2 * 1024 * 1024
            if avatar.size > max_size:
                raise ValidationError('Avatar size is too big')
        return avatar


class CustomPasswordChangeForm(forms.Form):
    """
        Форма для зміни пароля з перевіркою старого пароля та надійності нового.
    """
    old_password = forms.CharField(widget=forms.PasswordInput(), label='Old Password', required=True)
    new_password = forms.CharField(widget=forms.PasswordInput(), label='New Password', required=True, min_length=8)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label='Confirm Password', required=True)


    def __init__(self, user: User = None, *args: Any, **kwargs: Any) -> None:
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self) -> str:
        """Перевіряє правильність поточного пароля."""
        old_password = self.cleaned_data.get('old_password')
        if not check_password(old_password, self.user.password):
            raise ValidationError('Old password is not correct')
        return old_password

    def clean(self) -> Dict[str, Any]:
        """
            Перевіряє:
                1. Щоб новий пароль відрізнявся від старого.
                2. Щоб підтвердження збігалося з новим паролем.
        """
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if old_password and new_password and confirm_password == new_password:
            raise ValidationError('Password is same')

        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError('Passwords do not match')

        return cleaned_data
