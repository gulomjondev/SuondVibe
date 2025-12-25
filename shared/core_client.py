from celery.worker.state import requests


def get_core_user(token):
    requests.get("/api/me/")
