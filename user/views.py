import logging
from typing import Tuple, Any
from django.views.decorators.clickjacking import xframe_options_deny
from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django_ratelimit.decorators import ratelimit
from urllib.parse import quote, unquote

from .forms import (
    RegistrationForm,
    LoginForm,
    UserProfileForm,
    CustomPasswordChangeForm,
    ProjectTeamForm,
    SessionFieldsForm,
)


logger = logging.getLogger(__name__)


def home_view(request: HttpRequest) -> HttpResponse:
    """Відображає головну сторінку додатка."""
    return render(request, 'user/home.html')


def register_view(request: HttpRequest) -> HttpResponse:
    """Реєструє нового користувача."""
    if request.user.is_authenticated:
        return redirect(reverse('user:profile_view', kwargs={'username': request.user.username}))

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Реєстрація успішна! Ласкаво просимо до системи.")
            return redirect(reverse('user:profile_view', kwargs={'username': user.username}))
    else:
        form = RegistrationForm()
    return render(request, 'user/register.html', {'form': form})


@xframe_options_deny
@ratelimit(key='ip', rate='5/m', block=True)
def login_view(request: HttpRequest) -> HttpResponse:
    """Обробляє автентифікацію та вхід користувача в систему."""
    if request.user.is_authenticated:
        return redirect(reverse('user:profile_view', kwargs={'username': request.user.username}))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Вітаємо з поверненням, {username}!")
                return redirect(reverse('main:home'))  # Виправлено на безпечний редирект через reverse
            else:
                messages.error(request, "Неправильне ім'я користувача або пароль.")
    else:
        form = LoginForm()
    return render(request, 'user/login.html', {'form': form})


def logout_view(request: HttpRequest) -> HttpResponse:
    """Завершує роботу поточної сесії користувача (вихід із системи)."""
    logout(request)
    messages.info(request, "Ви успішно вийшли із системи.")
    return redirect(reverse('user:login'))


@login_required
def profile_view(request: HttpRequest, username: str) -> HttpResponse:
    """Відображає сторінку профілю конкретного користувача."""
    target_user = get_object_or_404(User, username=username)
    return render(request, 'user/profile_detail.html', {'target_user': target_user})


@login_required
def edit_profile_view(request: HttpRequest) -> HttpResponse:
    """Дозволяє авторизованому користувачеві редагувати дані свого профілю."""
    profile = request.user.user_profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профіль успішно оновлено!')
            return redirect(reverse('user:profile_view', kwargs={'username': request.user.username}))
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'user/edit_profile.html', {'form': form})


@login_required
def change_password_view(request: HttpRequest) -> HttpResponse:
    """Забезпечує безпечну зміну пароля користувача з перевіркою старого пароля."""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Ваш пароль успішно оновлено!')
            return redirect(reverse('user:profile_view', kwargs={'username': request.user.username}))
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'user/change_password.html', {'form': form})


@login_required
def delete_account_view(request: HttpRequest) -> HttpResponse:
    """Видаляє обліковий запис поточного користувача."""
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Ваш обліковий запис успішно видалено назавжди.")
        return redirect(reverse('user:register'))
    return render(request, 'user/confirm_delete.html')


@login_required
def create_project_team_view(request: HttpRequest) -> HttpResponse:
    """Представлення для відображення та обробки форми створення команди проєкту."""
    if request.method == 'POST':
        form = ProjectTeamForm(request.POST)
        if form.is_valid():
            messages.success(request, f"Команду проєкту '{form.cleaned_data['project_name']}' успішно створено!")
            return redirect(reverse('main:home'))
    else:
        form = ProjectTeamForm()

    return render(request, 'user/create_team.html', {'form': form})


def get_user_secure(username: str) -> list[Tuple[Any, ...]]:
    """Безпечний сирий SQL-запит для отримання інформації про користувача."""
    query = "SELECT id, username, email FROM auth_user WHERE username = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (username,))
        return cursor.fetchall()


def custom_handler404(request, exception=None):
    """Кастомний обробник помилки 404 для головного urls.py"""
    return render(request, 'errors/404.html', status=404)


def custom_handler500(request):
    """Кастомний обробник помилки 500 для головного urls.py"""
    return render(request, 'errors/500.html', status=500)


def cookie_session_demo_view(request: HttpRequest) -> HttpResponse:
    """Оновлене представлення для керування сесіями та cookies."""
    raw_user_name = request.COOKIES.get('user_name')
    user_name = unquote(raw_user_name) if raw_user_name is not None else None
    user_age = request.session.get('user_age')

    if user_name is not None:
        try:
            user_age = int(user_age)
            if user_age <= 0 or user_age > 120:
                raise ValueError
        except (ValueError, TypeError):
            if 'user_age' in request.session:
                del request.session['user_age']
            user_age = None

    form = SessionFieldsForm

    if request.method == 'POST':
        form = SessionFieldsForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            age = form.cleaned_data['age']
            request.session['user_age'] = age
            response = redirect(reverse('user:cookie_demo'))
            safe_name = quote(name)
            response.set_cookie('user_name', safe_name, max_age=600, httponly=True, samesite='Lax')
            return response

    response = render(request, 'user/cookie_demo.html', {
        'form': form,
        'user_name': user_name,
        'user_age': user_age
     })

    if user_name:
        response.set_cookie('user_name', quote(user_name), max_age=600, httponly=True, samesite='Lax')

    return response


def clean_cookie_session_view(request: HttpRequest) -> HttpResponse:
    """Повне очищення сесії та cookies (Кнопка 'Вийти')."""
    if 'user_age' in request.session:
        del request.session['user_age']

    response = redirect(reverse('user:cookie_demo'))
    response.delete_cookie('user_name')
    return response
