
from django import forms
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from typing import Any, Dict
import re

from user.models import UserProfile
from core.widgets import IconSelectWidget
from core.validators import validate_corporate_email, validate_file_size


class ProjectTeamForm(forms.Form):

    email = forms.EmailField(validators=[validate_corporate_email])

    main_technology = forms.ChoiceField(
        label="Основна технологія",
        choices=[
            ('python', 'Python / Django'),
            ('js', 'JavaScript / React'),
            ('design', 'UI/UX Design')
        ],
        widget=IconSelectWidget(attrs={'class': 'form-select'})  # Підключаємо віджет
    )

    project_name = forms.CharField(
        max_length=100,
        label="Назва проєкту",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    contact_email = forms.EmailField(
        label="Корпоративний Email",
        validators=[validate_corporate_email],  # Підключаємо валідатор
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@company.com'})
    )


class RegistrationForm(forms.ModelForm):
    """
        Форма для реєстрації нового користувача.
        Включає перевірку унікальності імені та email, а також збіг паролів.
    """

    email = forms.EmailField(required=True, label='Email')
    phone_number = forms.CharField(
        required=True,
        label='Номер телефону',
        widget=forms.TextInput(attrs={'placeholder': '+380XXXXXXXXX'})
    )
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

    def clean_phone_number(self) -> str:
        """ДОДАНО: Кастомний валідатор формату та унікальності номеру телефону."""
        phone = self.cleaned_data.get('phone_number')
        phone_regex = r'^\+?3?8?(0\d{9})$'
        if not re.match(phone_regex, phone):
            raise ValidationError('Некоректний формат номеру. Приклад: +380501234567')
        if UserProfile.objects.filter(phone_number=phone).exists():
            raise ValidationError('This phone number is already in use')

        return phone

    def clean_password(self) -> Dict[str, Any]:
        """Перевіряє, чи збігаються паролі."""
        cleaned_data = super().clean()
        password = self.cleaned_data.get('password')
        password_confirmation = self.cleaned_data.get('password_confirmation')

        if password and password_confirmation and password != password_confirmation:
            self.add_error('password_confirmation', 'Passwords do not match')

        return cleaned_data

    def save(self, commit: bool = True) -> User:
        """Створює користувача через create_user для хешування пароля."""
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )

        profile = user.user_profile
        profile.phone_number = self.cleaned_data['phone_number']
        profile.save()

        return user


class UserProfileForm(forms.ModelForm):
    """
        Форма для оновлення додаткової інформації профілю користувача.
    """
    avatar = forms.ImageField(required=False, validators=[validate_file_size])


    class Meta:
        model = UserProfile
        fields = ['phone_number', 'bio', 'birth_date', 'location', 'avatar']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4})
        }


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
        if self.user and not check_password(old_password, self.user.password):
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

        if old_password and new_password and old_password == new_password:
            self.add_error('new_password', 'The new password must be different from the old one')
        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match')

        return cleaned_data
