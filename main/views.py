from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

# Create your views here.

from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView
from datetime import datetime
from typing import Any


"""
def home_view(_request: HttpRequest) -> HttpResponse:
    #Display the main landing page of the main application.
    return HttpResponse("Ласкаво просимо на головну сторінку")

def about_view(_request: HttpRequest) -> HttpResponse:
    #Display the 'About Us' page with project information.
    return HttpResponse("Сторінка про нас")

def contact_view(_request: HttpRequest) -> HttpResponse:
    #Display the 'Contact' page with contact details.
    return HttpResponse("Зв'яжіться з нами")

def post_view(_request: HttpRequest, id: int) -> HttpResponse:
    #Display a specific post identified by its ID.
    return HttpResponse(f"Ви переглядаєте пост з ID: {id}")

def profile_view(_request: HttpRequest, username: str) -> HttpResponse:
    #Display the user profile page.
    return HttpResponse(f"Ви переглядаєте профіль користувача: {username}")

def event_view(_request: HttpRequest, year: int, month: int, day: int) -> HttpResponse:
    #Display details for an event occurring on a specific date.
    event_date = f"{year}-{month}-{day}"
    current_year = datetime.now().year
    if int(year) < current_year:
        status = "(це подія з минулого)"
    elif int(year) == current_year:
        status = "(це подія цього року)"
    else:
        status = "(це майбутня подія)"

    return HttpResponse(f"Дата події: {event_date} {status}")
"""


def post_view(request: HttpRequest, id: int) -> HttpResponse:
    """Render the post page with its ID."""
    return render(request, 'main/post.html', {'id': id})


def profile_view(request: HttpRequest, username: str) -> HttpResponse:
    """Render the user profile page."""
    return render(request, 'main/profile.html', {'username': username})


def event_view(request: HttpRequest, year: str, month: str, day: str) -> HttpResponse:
    """Render the event page with date parameters."""
    context = {
        'year': year,
        'month': month,
        'day': day,
    }
    return render(request, 'main/event.html', context)


def home_view(request: HttpRequest) -> HttpResponse:
    """Render the main page."""
    context = {
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
    """Render the about us page."""
    context = {
        'project_description': "Цей сайт створено як навчальний проект для вивчення основ <strong>Django</strong>, маршрутизації та шаблонів.",
        'goals': [
            "Навчитися створювати гнучкі веб-застосунки з використанням динамічних URL.",
            "Опанувати професійну структуру коду та роботу з шаблонами для великих проектів."
        ],
        'update_date': datetime.now()
    }
    return render(request, 'main/about.html', context)


class ContactView(TemplateView):
    """View of the contact page (Class)"""
    template_name = 'main/contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['email'] = 'INFO@MYSITE.COM'
        context['phone'] = '+380 99 123 45 67'
        context['address'] = 'м. Одеса, вул. Дерибасівська'
        context['is_open'] = True
        return context


class ServiceView(TemplateView):
    """View of the list of services (Class)"""
    template_name = 'main/services.html'

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)

        all_services = [
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
