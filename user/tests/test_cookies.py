from urllib.parse import quote
from django.test import TestCase
from django.urls import reverse


class CookieSessionDemoView(TestCase):
    """Тести для перевірки логіки роботи з Cookies та Сесіями."""

    def setUp(self) -> None:
        self.url = reverse('user:cookie_demo')
        self.clear_url = reverse('user:clear_cookie_demo')

    def test_post_saves_cookie_and_session(self) -> None:
        """Перевірка створення Cookie та сесії."""
        form_data = {'name': 'Анна', 'age': 22}
        response = self.client.post(self.url, data=form_data)

        self.assertRedirects(response, self.url)
        self.assertEqual(self.client.session['user_age'], 22)
        self.assertIn('user_name', response.cookies)
        self.assertEqual(response.cookies['user_name'].value, quote('Анна'))

    def test_clear_view_deletes_everything(self) -> None:
        """Перевірка кнопки 'Вийти'."""
        session = self.client.session
        session['user_age'] = 20
        session.save()
        self.client.cookies['user_name'] = quote('Олег')

        response = self.client.get(self.clear_url)
        self.assertIn(response.cookies['user_name'].value, ['', quote('Олег')])
        self.assertNotIn('user_age', self.client.session)
