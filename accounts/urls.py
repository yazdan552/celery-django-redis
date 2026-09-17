from django.urls import path
from .views import test_celery_view


urlpatterns = [
    path('test-celery/', test_celery_view, name='test_celery'),
]