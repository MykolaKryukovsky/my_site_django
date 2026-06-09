
import logging
from datetime import datetime
from typing import Any, Dict, List
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView


logger = logging.getLogger(__name__)


def home_view(request: HttpRequest) -> HttpResponse:
    """Відображає головну сторінку додатку з тестовими даними."""
    context: Dict[str, Any] = {
        'welcome_text': "Ласкаво просимо на наш Django сайт!",
        'site_description': "Це основний застосунок для роботи з маршрутизацією та шаблонами. Тут ми вивчаємо Django на прикладах.",
        'services': ['Веб-розробка', 'SEO', 'Дизайн', 'Мобільні додатки'],
        'posts': [
            {'id': 1, 'title': 'Перший пост'},
            {'id': 2, 'title': 'Другий пост'}
        ],
        'event_date': datetime(2026, 5, 1),
        'show_promo': True
    }
    return render(request, 'main/home.html', context)


def about_view(request: HttpRequest) -> HttpResponse:
    """Відображає сторінку інформації 'Про нас'."""
    context: Dict[str, Any] = {
        'project_description': "Цей сайт створено як навчальний проект для вивчення основ <strong>Django</strong>, маршрутизації та шаблонів.",
        'goals': [
            "Навчитися створювати гнучкі веб-застосунки з використанням динамічних URL.",
            "Опанувати професійну структуру коду та роботу з шаблонами для великих проектів."
        ],
        'update_date': datetime.now()
    }
    return render(request, 'main/about.html', context)


def post_view(request: HttpRequest, id: int) -> HttpResponse:
    """Відображає сторінку конкретного поста за його ID."""
    return render(request, 'main/post.html', {'id': id})


def event_view(request: HttpRequest, year: int, month: int, day: int) -> HttpResponse:
    """Відображає сторінку події з динамічними параметрами дати (типізовано як int)."""
    context: Dict[str, int] = {
        'year': year,
        'month': month,
        'day': day,
    }
    return render(request, 'main/event.html', context)


class ContactView(TemplateView):
    """Клас-представлення для відображення сторінки контактів."""
    template_name = 'main/contact.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['email'] = 'INFO@MYSITE.COM'
        context['phone'] = '+380 99 123 45 67'
        context['address'] = 'м. Одеса, вул. Дерибасівська'
        context['is_open'] = True
        return context


class ServiceView(TemplateView):
    """Клас-представлення для відображення та фільтрації списку послуг сайту."""
    template_name = 'main/services.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        all_services: List[Dict[str, Any]] = [
            {
                'name': 'Веб-розробка',
                'description': 'Створення сучасних та швидких сайтів на базі Django та Python.',
                'icon': 'bi-code-slash',
                'category': 'it',
                'updated_at': datetime.now(),
                'html_details': '<b>Best Choice</b>'
            },
            {
                'name': 'Мобільні додатки',
                'description': 'Розробка зручних застосунків для iOS та Android.',
                'icon': 'bi-phone',
                'category': 'mobile',
                'updated_at': datetime.now(),
            },
            {
                'name': 'SEO Оптимізація',
                'description': 'Виведення вашого бізнесу в топ пошукових запитів Google.',
                'icon': 'bi-graph-up-arrow',
                'category': 'marketing',
                'updated_at': None,
            }
        ]

        query = self.request.GET.get('q', '').lower()

        if query:
            filtered_services = [
                item for item in all_services
                if query in item['name'].lower() or query in item.get('category', '').lower()
            ]
        else:
            filtered_services = all_services

        context['services'] = filtered_services
        context['query'] = query
        context['has_discounts'] = True

        return context
