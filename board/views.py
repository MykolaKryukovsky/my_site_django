
from django.http import HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404
from django.db.models import Count
from datetime import timedelta

from .models import *


def index_view(_request: HttpRequest) -> HttpResponse:
    """Усі активні оголошення та їх сортування"""
    ads = Ad.objects.filter(is_active=True)

    query = _request.GET.get('q')
    if query:
        ads = ads.filter(title__icontains=query)

    cat_id = _request.GET.get('cat_id')
    min_price = _request.GET.get('min_price')

    if cat_id:
        ads = ads.filter(category_id=cat_id)
    if min_price:
        ads = ads.filter(price__gte=min_price)

    sort = _request.GET.get('sort', '-created_at')
    ads = ads.order_by(sort)

    output = f"<h1>Знайдено оголошень: {ads.count()}</h1>"
    for ad in ads:
        output += f"<p>{ad.title} | Ціна: {ad.price} | Дата: {ad.created_at.date()}</p>"

    return HttpResponse(output)


def stats_view(_request):
    if not _request.user.is_superuser:
        return HttpResponse("Доступ тільки для адміна", status=403)

    total_ads = Ad.objects.count()
    active_ads = Ad.objects.filter(is_active=True).count()
    total_comments = Comment.objects.count()

    categories_stats = Category.objects.annotate(ads_count=Count('ads'))

    output = "<h1>Статистика сервісу</h1>"
    output += f"<p>Усього: {total_ads} (Активних: {active_ads})</p>"
    output += f"<p>Усього коментарів: {total_comments}</p>"
    output += "<h3>По категоріях:</h3>"
    for cat in categories_stats:
        output += f"<p>{cat.name}: {cat.ads_count}</p>"

    return HttpResponse(output)


def category_ads_view(_request: HttpRequest, category_id: int) -> HttpResponse:
    """Оголошення конкретної категорії"""
    category = get_object_or_404(Category, id=category_id)
    ads = Ad.objects.filter(category=category, is_active=True)
    return HttpResponse(f"Категорія: {category.name}. Знайдено оголошень: {ads.count()}")


def ad_detail_view(_request: HttpRequest, ad_id: str) -> HttpResponse:
    """Детальне оголошення (з деактивацією та лічильником коментів)"""
    ad = get_object_or_404(Ad, id=ad_id)
    ad.deactivate_if_expired()
    comments_count = ad.comments.count()
    return HttpResponse(f"Оголошення: {ad.title}. Ціна: {ad.price}. Коментарів: {comments_count}")


def recent_ads_view(_request: HttpRequest) -> HttpResponse:
    """Оголошення за останні 30 днів"""
    last_month = timezone.now() - timedelta(days=30)
    ads = Ad.objects.filter(created_at__gte=last_month)
    return HttpResponse(f"Нові оголошення за місяць. Кількість: {ads.count()}")


def user_profile_view(_request: HttpRequest, username: str) -> HttpResponse:
    """Виведення профілю користувача та його оголошень"""
    profile = get_object_or_404(Profile, user__username=username)
    user_ads = Ad.objects.filter(user=profile.user)

    output = f"<h1>Профіль користувача: {profile.user.username}</h1>"
    output += f"<p>Телефон: {profile.phone}</p>"
    output += f"<p>Адреса: {profile.address}</p>"

    output += f"<h2>Оголошення користувача ({user_ads.count()}):</h2>"
    for ad in user_ads:
        output += f"<p>- {ad.title} (Ціна: {ad.price})</p>"

    return HttpResponse(output)
