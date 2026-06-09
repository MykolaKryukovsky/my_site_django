from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from .models import Ad, Category, Comment


def index_view(request: HttpRequest) -> HttpResponse:
    """Відображає список усіх активних оголошень із фільтрацією та сортуванням."""
    ads = Ad.objects.active()
    query = request.GET.get('q')
    if query:
        ads = ads.filter(title__icontains=query)

    cat_id = request.GET.get('cat_id')
    min_price = request.GET.get('min_price')

    if cat_id:
        ads = ads.filter(category_id=cat_id)
    if min_price:
        ads = ads.filter(price__gte=min_price)

    sort = request.GET.get('sort', '-created_at')
    ads = ads.order_by(sort)
    stats = ads.get_price_stats()
    categories = Category.objects.all()
    context = {
        'ads': ads,
        'categories': categories,
        'stats': stats,
        'query': query,
        'current_cat': int(cat_id) if cat_id else None,
        'current_min_price': min_price,
        'current_sort': sort,
    }
    return render(request, 'board/ad_list.html', context)


def category_ads_view(request: HttpRequest, category_id: int) -> HttpResponse:
    """Відображає оголошення конкретної обраної категорії."""
    category = get_object_or_404(Category, id=category_id)
    ads = Ad.objects.active().filter(category=category)
    cat_stats = ads.get_price_stats()
    context = {
        'category': category,
        'ads': ads,
        'cat_stats': cat_stats,
    }
    return render(request, 'board/category_ads.html', context)


def ad_detail_view(request: HttpRequest, ad_id: int) -> HttpResponse:
    """Відображає детальну сторінку конкретного оголошення (типізовано як int)."""
    ad = get_object_or_404(Ad, id=ad_id)
    ad.deactivate_if_expired()
    comments_count = ad.get_comments_count()
    comments = Comment.objects.filter(ad=ad).order_by('-created_at') if hasattr(Comment, 'ad') else []
    context = {
        'ad': ad,
        'comments_count': comments_count,
        'comments': comments,
    }
    return render(request, 'board/ad_detail.html', context)


def recent_ads_view(request: HttpRequest) -> HttpResponse:
    """Відображає оголошення, створені за останні 30 днів."""
    last_month = timezone.now() - timedelta(days=30)
    ads = Ad.objects.filter(created_at__gte=last_month).order_by('-created_at')
    recent_stats = ads.get_price_stats()
    context = {
        'ads': ads,
        'recent_stats': recent_stats,
    }
    return render(request, 'board/recent_ads.html', context)


def user_profile_view(request: HttpRequest, username: str) -> HttpResponse:
    """Відображає список оголошень конкретного автора."""
    author = get_object_or_404(User, username=username)
    user_ads = Ad.objects.filter(user=author).order_by('-created_at')
    user_stats = user_ads.get_price_stats()

    context = {
        'author': author,
        'user_ads': user_ads,
        'user_stats': user_stats,
    }
    return render(request, 'board/user_ads.html', context)
