
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    BookViewSet,
    RegisterView,
    ORMPerformanceListView,
    CachedBooksListView,
    CSVImportView,
    TaskStatusView,
    BookAnalyticsListView,
    BookRawSQLListView,
    MongoDBBooksListView
)


app_name = 'books'


router = SimpleRouter()
router.register(r'books', BookViewSet, basename='book')


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register/', RegisterView.as_view(), name='auth_register'),
    path('api/perf-demo/', ORMPerformanceListView.as_view(), name='perf_demo'),
    path('books/catalog/', CachedBooksListView.as_view(), name='cached_books_catalog'),
    path('books/import/', CSVImportView.as_view(), name='csv_import'),
    path('books/task/<str:task_id>/', TaskStatusView.as_view(), name='task_status'),
    path('books/analytics/',BookAnalyticsListView.as_view(), name='books_analytics'),
    path('books/raw-sql/', BookRawSQLListView.as_view(), name='books_raw_sql'),
    path('books/nosql/', MongoDBBooksListView.as_view(), name='nosql_catalog'),

]
