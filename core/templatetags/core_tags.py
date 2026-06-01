from django import template

from django.urls import reverse, NoReverseMatch


register = template.Library()


@register.filter(name='short_text')
def short_text(value, max_length=100):
    """Обрізає текст до вказаної довжини і додає трикрапку."""
    string_value = str(value)
    if len(string_value) > max_length:
        return f"{string_value[:max_length]}..."
    return string_value


@register.simple_tag(takes_context=True)
def active_link(context, url_name):
    """
    Повертає CSS-клас 'active', якщо поточний URL збігається з url_name.
    Використовується для підсвічування пунктів меню навігації.
    """
    request = context.get('request')
    if not request:
        return ''
    try:
        if request.path == reverse(url_name):
            return 'active'
    except NoReverseMatch:
        return ''
    return ''
