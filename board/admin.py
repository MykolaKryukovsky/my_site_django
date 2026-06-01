
from django.contrib import admin
from .models import Ad, Category, Comment, Profile


class CommentInline(admin.TabularInline):
    """
    Inline-модель для коментарів.
    Дозволяє бачити, редагувати та видаляти коментарі до оголошення
    прямо на сторінці редагування цього оголошення.
    """
    model = Comment
    extra = 1
    fields = ('user', 'content', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    """
    Кастомне налаштування відображення моделі Оголошення (Ad) в адмінці.
    """
    list_display = ('title', 'category', 'price', 'is_active', 'user', 'created_at')
    list_display_links = ('title',)
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    fieldsets = (
        ("Основна інформація", {
            'fields': ('title', 'category', 'description')
        }),
        ("Економіка та Власник", {
            'fields': ('price', 'user')
        }),
        ("Статус та Дати", {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CommentInline]
    actions = ['make_active', 'make_inactive']

    @admin.action(description="Увімкнути (активувати) обрані оголошення")
    def make_active(self, request, queryset):
        """Масова активація оголошень."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Успішно активовано {updated} оголошень.")

    @admin.action(description="Вимкнути (деактивувати) обрані оголошення")
    def make_inactive(self, request, queryset):
        """Масова деактивація оголошень."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Успішно деактивовано {updated} оголошень.")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Кастомна адмінка для категорій з підрахунком оголошень."""
    list_display = ('name', 'description', 'active_ads_count_display')
    search_fields = ('name',)

    def active_ads_count_display(self, obj):
        """Виводимо кількість активних оголошень через метод моделі."""
        return obj.active_ads_count()

    active_ads_count_display.short_description = "Активних оголошень"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Кастомна адмінка для профілів користувачів."""
    list_display = ('user', 'phone', 'address')
    search_fields = ('user__username', 'phone')
