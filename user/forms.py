import re
import bleach
from typing import Any, Dict
from django import forms
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from user.models import UserProfile
from core.widgets import IconSelectWidget
from core.validators import validate_corporate_email, validate_file_size


class ProjectTeamForm(forms.Form):
    """
    Форма для створення нової команди проєкту.
    """
    email = forms.EmailField(
        label="Email адміністратора",
        validators=[validate_corporate_email]
    )
    main_technology = forms.ChoiceField(
        label="Основна технологія",
        choices=[
            ('python', 'Python / Django'),
            ('js', 'JavaScript / React'),
            ('design', 'UI/UX Design')
        ],
        widget=IconSelectWidget()
    )
    project_name = forms.CharField(
        max_length=100,
        label="Назва проєкту",
        widget=forms.TextInput(attrs={'placeholder': 'Введіть назву проєкту'})
    )
    contact_email = forms.EmailField(
        label="Корпоративний Email",
        validators=[validate_corporate_email],
        widget=forms.EmailInput(attrs={'placeholder': 'name@company.com'})
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class RegistrationForm(forms.ModelForm):
    """
    Форма для реєстрації нового користувача з очищенням через bleach.
    """
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'example@email.com'})
    )
    phone_number = forms.CharField(
        required=True,
        label='Номер телефону',
        widget=forms.TextInput(attrs={'placeholder': '+380XXXXXXXXX'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Введіть пароль'}),
        label='Пароль'
    )
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторіть пароль'}),
        label='Підтвердження пароля'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Оберіть ім\'я користувача'}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_username(self) -> str:
        """Перевіряє унікальність логіну та очищає його від HTML-тегів за допомогою bleach."""
        username = self.cleaned_data.get('username', '')
        cleaned_username = bleach.clean(username, tags=[], strip=True)

        if User.objects.filter(username=cleaned_username).exists():
            raise ValidationError('Це ім\'я користувача вже зайняте.')
        return cleaned_username

    def clean_email(self) -> str:
        """Перевіряє унікальність адреси електронної пошти."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Користувач з таким Email вже існує.')
        return email

    def clean_phone_number(self) -> str:
        """Валідатор формату та унікальності номеру телефону."""
        phone = self.cleaned_data.get('phone_number')
        phone_regex = r'^\+?3?8?(0\d{9})$'
        if not re.match(phone_regex, phone):
            raise ValidationError('Некоректний формат номеру. Приклад: +380501234567')
        if UserProfile.objects.filter(phone_number=phone).exists():
            raise ValidationError('Цей номер телефону вже використовується.')
        return phone

    def clean(self) -> Dict[str, Any]:
        """Перевіряє, чи збігаються паролі."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if password and password_confirmation and password != password_confirmation:
            self.add_error('password_confirmation', 'Паролі не збігаються.')
        return cleaned_data

    def save(self, commit: bool = True) -> User:
        """Створює користувача та заповнює зв'язаний профіль."""
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        profile = user.user_profile
        profile.phone_number = self.cleaned_data['phone_number']
        profile.save()
        return user


class LoginForm(forms.Form):
    """
    Форма для авторизації (входу) існуючого користувача.
    """
    username = forms.CharField(
        label="Ім'я користувача",
        widget=forms.TextInput(attrs={'placeholder': 'Введіть логін або email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Введіть пароль'}),
        label="Пароль"
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class UserProfileForm(forms.ModelForm):
    """
    Форма для оновлення додаткової інформації профілю користувача.
    """
    avatar = forms.ImageField(
        required=False,
        label="Фото профілю",
        validators=[validate_file_size]
    )

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'bio', 'birth_date', 'location', 'avatar']
        labels = {
            'phone_number': 'Номер телефону',
            'bio': 'Про себе',
            'birth_date': 'Дата народження',
            'location': 'Місто',
        }
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Розкажіть трохи про себе...'}),
            'location': forms.TextInput(attrs={'placeholder': 'Ваше місто'}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class CustomPasswordChangeForm(forms.Form):
    """
    Форма для зміни пароля з перевіркою старого пароля та надійності нового.
    """
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Введіть поточний пароль'}),
        label='Поточний пароль',
        required=True
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Мінімум 8 символів'}),
        label='Новий пароль',
        required=True,
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторіть новий пароль'}),
        label='Підтвердження нового пароля',
        required=True
    )

    def __init__(self, user: User = None, *args: Any, **kwargs: Any) -> None:
        self.user = user
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_old_password(self) -> str:
        """Перевіряє правильність поточного пароля."""
        old_password = self.cleaned_data.get('old_password')
        if self.user and not check_password(old_password, self.user.password):
            raise ValidationError('Поточний пароль вказано неправильно.')
        return old_password

    def clean(self) -> Dict[str, Any]:
        """Перевіряє унікальність нового пароля та збіг підтвердження."""
        cleaned_data = super().clean()
        old_password = cleaned_data.get('old_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if old_password and new_password and old_password == new_password:
            self.add_error('new_password', 'Новий пароль повинен відрізнятися від старого.')
        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', 'Паролі не збігаються.')

        return cleaned_data
