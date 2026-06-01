
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Дозволяє редагувати bio, аватар та локацію прямо на сторінці користувача."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Додатковий профіль користувача'


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
