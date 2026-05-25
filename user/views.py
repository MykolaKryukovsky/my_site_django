
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpRequest, HttpResponse

from .forms import RegistrationForm, UserProfileForm, CustomPasswordChangeForm


def register_view(request: HttpRequest) -> HttpResponse:
    """
        Реєструє нового користувача.
        Якщо користувач вже авторизований, перенаправляє його профіль.
        При успішній реєстрації автоматично виконує вхід.
        Args:
            request: Об'єкт HTTP-запиту.
        Returns:
            Об'єкт HTTP-відповіді з формою реєстрації або редірект.
    """
    if request.user.is_authenticated:
        return redirect('profile_view', username=request.user.username)

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile_view', username=user.username)
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def edit_profile_view(request: HttpRequest) -> HttpResponse:
    """
        Дозволяє авторизованому користувачеві редагувати дані свого профілю.
        Args:
            request: Об'єкт HTTP-запиту.
        Returns:
            Сторінка редагування профілю або редірект на перегляд профілю.
    """
    profile = request.user.user_profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, f'Your profile has been updated!')
            return redirect('profile_view', username=request.user.username)
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})


@login_required
def change_password_view(request: HttpRequest) -> HttpResponse:
    """
        Забезпечує зміну пароля користувача з перевіркою старого пароля.
        Використовує update_session_auth_hash, щоб користувач залишався
        у системі після зміни пароля.
        Args:
            request: Об'єкт HTTP-запиту.
        Returns:
            Сторінка зміни пароля або редірект на профіль.
    """
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, f'Your password was successfully updated!')
            return redirect('profile_view', username=request.user.username)
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})


@login_required
def profile_view(request: HttpRequest, username: str) -> HttpResponse:
    """
        Відображає сторінку профілю конкретного користувача.
        Args:
            request: Об'єкт HTTP-запиту.
            username: Ім'я користувача, профіль якого потрібно переглянути.
        Returns:
            Сторінка з детальною інформацією про профіль.
    """
    target_user = get_object_or_404(User, username=username)
    return render(request, 'profile_detail.html', {'target_user': target_user})


@login_required
def delete_account_view(request: HttpRequest) -> HttpResponse:
    """
        Видаляє обліковий запис поточного користувача.
        Вимагає POST-запиту для підтвердження видалення.
        Args:
            request: Об'єкт HTTP-запиту.
        Returns:
            Підтвердження видалення або редірект на реєстрацію після успіху.
    """
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Ваш обліковий запис успішно видалено.")
        return redirect('register')
    return render(request, 'confirm_delete.html')
