
from django.contrib import admin
from .models import Profile, Category, Ad, Comment

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'description')

admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Comment)
