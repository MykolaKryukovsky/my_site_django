
from django import template
from django.urls import reverse, NoReverseMatch


register = template.Library()


@register.filter(name='short_text')
def short_text(value, max_length: int = 100) -> str:
    """
    Обрізає текст до вказаної довжини і додає трикрапку.
    Універсальний фільтр для компактного виведення довгих текстів або описів.
    """
    string_value = str(value)
    if len(string_value) > max_length:
        return f"{string_value[:max_length]}..."
    return string_value


@register.simple_tag(takes_context=True)
def active_link(context, url_name: str) -> str:
    """
    ВІДКОРИГОВАНО: Розумне підсвічування пунктів меню навігації.
    Повертає CSS-клас 'active', якщо поточний маршрут збігається з url_name.
    Повністю підтримує простори імен (namespaces) та динамічні URL (профілі, пости).
    """
    request = context.get('request')
    if not request:
        return ''

    resolver_match = getattr(request, 'resolver_match', None)
    if not resolver_match:
        return ''

    current_url_name = (
        f"{resolver_match.namespace}:{resolver_match.url_name}"
        if resolver_match.namespace
        else resolver_match.url_name
    )

    if current_url_name == url_name:
        return 'active'

    if url_name.endswith(':index_view') or url_name.endswith(':home'):
        base_namespace = url_name.split(':')[0]
        if resolver_match.namespace == base_namespace:
            return 'active'

    try:
        if request.path == reverse(url_name):
            return 'active'
    except NoReverseMatch:
        pass

    return ''
