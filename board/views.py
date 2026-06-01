
from django.http import HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from .models import Ad, Category, Comment, Profile


def index_view(_request: HttpRequest) -> HttpResponse:
    """Усі активні оголошення та їх сортування"""
    ads = Ad.objects.active()

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
    stats = ads.get_price_stats()

    output = f"<h1>Знайдено оголошень: {ads.count()}</h1>"
    output += (f"<p>Загальна вартість вибірки: {stats['total_sum'] or 0} грн |"
               f" Середня ціна: {stats['average_price'] or 0} грн</p>"
    )
    output += "<hr>"

    for ad in ads:
        output += (
            f"<p>"
            f"<span style='color: {ad.category.color}; font-weight: bold;'>[{ad.category.name}]</span> "  # Категорія попереду
            f"<strong>{ad.title}</strong> | Ціна: {ad.price} | "
            f"Дата: {ad.created_at.date()}<br>"
            f"<small>{ad.short_description()}</small>"
            f"</p>"
        )

    return HttpResponse(output)


def stats_view(_request):
    if not _request.user.is_superuser:
        return HttpResponse("Доступ тільки для адміна", status=403)

    site_financials = Ad.objects.get_price_stats()
    active_financials = Ad.objects.active().get_price_stats()
    total_comments = Comment.objects.count()
    categories_stats = Category.objects.annotate(ads_count=Count('ads'))

    output = "<h1>Статистика сервісу</h1>"
    output += (f"<p>Усього оголошень: {site_financials['total_count']} "
               f"(Активних: {active_financials['total_count']})</p>"
    )
    output += f"<p>Загальна вартість товарів на сайті: {site_financials['total_sum'] or 0} грн</p>"
    output += f"<p>Середня ціна товару в активних оголошеннях: {active_financials['average_price'] or 0} грн</p>"
    output += f"<p>Усього коментарів на платформі: {total_comments}</p>"
    output += "<hr>"
    output += "<h3>Статистика по категоріях (Кількість оголошень):</h3>"

    for cat in categories_stats:
        output += f"<p>{cat.name}: {cat.ads_count} (Активних наразі: {cat.active_ads_count()})</p>"
    return HttpResponse(output)


def category_ads_view(_request: HttpRequest, category_id: int) -> HttpResponse:
    """Оголошення конкретної категорії"""
    category = get_object_or_404(Category, id=category_id)
    ads = Ad.objects.active().filter(category=category)
    cat_stats = ads.get_price_stats()

    output = f"<h1>Категорія: {category.name}</h1>"
    output += f"<p>Знайдено активних оголошень: {cat_stats['total_count']}</p>"
    output += f"<p>Середня вартість товарів у цій категорії: {cat_stats['average_price'] or 0} грн</p>"

    return HttpResponse(output)


def ad_detail_view(_request: HttpRequest, ad_id: str) -> HttpResponse:
    """Детальне оголошення (з деактивацією та лічильником коментів)"""
    ad = get_object_or_404(Ad, id=ad_id)
    ad.deactivate_if_expired()
    comments_count = ad.get_comments_count()
    status = "Активне" if ad.is_active else "Термін дії вичерпано/Деактивовано"

    output = f"<h1>Оголошення: {ad.title}</h1>"
    output += f"<p><strong>Статус:</strong> {status}</p>"
    output += f"<p><strong>Ціна:</strong> {ad.price} грн</p>"
    output += f"<p><strong>Опис:</strong> {ad.description}</p>"
    output += f"<p><strong>Кількість коментарів:</strong> {comments_count}</p>"

    return HttpResponse(output)


def recent_ads_view(_request: HttpRequest) -> HttpResponse:
    """Оголошення за останні 30 днів"""
    last_month = timezone.now() - timedelta(days=30)
    ads = Ad.objects.filter(created_at__gte=last_month)
    recent_stats = ads.get_price_stats()

    return HttpResponse(f"Нові оголошення за місяць. Кількість: {recent_stats['total_count']} "
                        f"на суму {recent_stats['total_sum'] or 0} грн."
    )


def user_profile_view(_request: HttpRequest, username: str) -> HttpResponse:
    """Виведення профілю користувача та його оголошень"""
    profile = get_object_or_404(Profile, user__username=username)
    user_ads = Ad.objects.filter(user=profile.user)
    user_stats = user_ads.get_price_stats()

    output = f"<h1>Профіль користувача: {profile.user.username}</h1>"
    output += f"<p>Телефон: {profile.phone}</p>"
    output += f"<p>Адреса: {profile.address}</p>"
    output += "<hr>"
    output += f"<h2>Оголошення користувача ({user_stats['total_count']}):</h2>"
    output += f"<p>Загальна вартість усіх товарів користувача: {user_stats['total_sum'] or 0} грн</p>"
    output += "<br>"

    for ad in user_ads:
        badge = "[АКТИВНЕ]" if ad.is_active else "[АРХІВ]"
        output += f"<p>{badge} - {ad.title} (Ціна: {ad.price} грн)</p>"

    return HttpResponse(output)
