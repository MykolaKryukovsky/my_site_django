from django.test import TestCase, RequestFactory
from django.template import Template, Context
from django.urls import path
from django.http import HttpResponse


def dummy_view(request):
    return HttpResponse("OK")


class CoreTemplateExtensionsTest(TestCase):
    """Набір тестів для перевірки кастомного фільтра short_text та тегу active_link."""

    def test_short_text_filter_behavior(self) -> None:
        """Перевірка обрізання тексту фільтром short_text та додавання трикрапки."""
        long_text = "A" * 150
        template_to_render = Template("{% load core_tags %}{{ text|short_text }}")
        rendered = template_to_render.render(Context({'text': long_text}))

        self.assertEqual(rendered, ("A" * 100) + "...")

        template_with_arg = Template("{% load core_tags %}{{ text|short_text:10 }}")
        rendered_short = template_with_arg.render(Context({'text': "0123456789XXXXX"}))

        self.assertEqual(rendered_short, "0123456789...")

        rendered_clean = template_to_render.render(Context({'text': "Hello"}))

        self.assertEqual(rendered_clean, "Hello")

    def test_active_link_tag_matches(self) -> None:
        """Перевірка розумного підсвічування пунктів меню тегом active_link."""
        factory = RequestFactory()
        request = factory.get('/profile/list/')

        from django.urls import ResolverMatch
        request.resolver_match = ResolverMatch(
            func=dummy_view,
            args=(),
            kwargs={},
            url_name='index_view',
            app_names=['board'],
            namespaces=['board']
        )

        template_tag = Template("{% load core_tags %}{% active_link 'board:index_view' %}")
        rendered_class = template_tag.render(Context({'request': request}))

        self.assertEqual(rendered_class, 'active')

    def test_active_link_tag_no_match(self) -> None:
        """Перевірка, що тег active_link повертає порожній рядок, якщо роути не збігаються."""
        factory = RequestFactory()
        request = factory.get('/home/')

        from django.urls import ResolverMatch
        request.resolver_match = ResolverMatch(
            func=dummy_view,
            args=(),
            kwargs={},
            url_name='home',
            app_names=['main'],
            namespaces=[]
        )
        template_tag = Template("{% load core_tags %}{% active_link 'user:login' %}")
        rendered_class = template_tag.render(Context({'request': request}))

        self.assertEqual(rendered_class, '')
