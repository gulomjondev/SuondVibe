from django.apps import AppConfig


class SharedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shared'
# app/tasks.py
from celery import shared_task

@shared_task
def test_task():
    print("Celery is working")
