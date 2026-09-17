import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'celery_app.settings')

app = Celery('celery_app')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-system-every-15s': {
        'task': 'accounts.tasks.check_system_status',
        'schedule': 15.0,
    },
}
