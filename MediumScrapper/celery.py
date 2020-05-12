import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MediumScrapper.settings')

app = Celery('MediumScrapper')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()