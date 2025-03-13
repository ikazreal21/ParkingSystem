import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ParkingSystem.settings')

app = Celery('ParkingSystem')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()