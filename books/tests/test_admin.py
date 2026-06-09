from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from ..models import Book
from ..admin import BookAdmin


class BookAdminTest(TestCase):
    """Набір тестів для перевірки кастомної логіки адмін-панелі BookAdmin."""

    def setUp(self) -> None:
        """Підготовка даних: створення суперкористувача та ініціалізація адмін-сайту."""
        self.site = AdminSite()
        self.admin_instance = BookAdmin(Book, self.site)
        self.admin_user = User.objects.create_superuser(
            username="admin_user",
            password="adminpassword123",
            email="admin@example.com"
        )

    def test_save_model_automatically_assigns_user(self) -> None:
        """Перевірка, що метод save_model автоматично прив'язує адміна при створенні книги."""
        from django.test import RequestFactory
        request = RequestFactory().get('/admin/books/book/add/')
        request.user = self.admin_user

        new_book = Book(
            title="Тигролови",
            author="Іван Багряний",
            genre="Роман",
            publication_year=1944,
            isbn="978-966-03-6111-0"
        )
        self.admin_instance.save_model(request, obj=new_book, form=None, change=False)
        self.assertEqual(new_book.user, self.admin_user)
        self.assertTrue(Book.objects.filter(isbn="978-966-03-6111-0").exists())
        self.assertEqual(new_book.title, "ТИГРОЛОВИ")
