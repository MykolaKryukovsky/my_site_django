from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

# Create your views here.

from django.http import HttpRequest, HttpResponse
#from datetime import datetime


"""
def home_view(_request: HttpRequest) -> HttpResponse:
    #Display the main landing page of the home application.
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


def home_view(request: HttpRequest) -> HttpResponse:
    """Render the main home page."""
    return render(request, 'home/home.html')

def about_view(request: HttpRequest) -> HttpResponse:
    """Render the about us page."""
    return render(request, 'home/about.html')

def contact_view(request: HttpRequest) -> HttpResponse:
    """Display the 'Contact' page using an HTML template."""
    return render(request, 'home/contact.html')

def post_view(request: HttpRequest, id: str) -> HttpResponse:
    """Render the post page with its ID."""
    return render(request, 'home/post.html', {'id': id})

def profile_view(request: HttpRequest, username: str) -> HttpResponse:
    """Render the user profile page."""
    return render(request, 'home/profile.html', {'username': username})

def event_view(request: HttpRequest, year: str, month: str, day: str) -> HttpResponse:
    """Render the event page with date parameters."""
    context = {
        'year': year,
        'month': month,
        'day': day,
    }
    return render(request, 'home/event.html', context)
