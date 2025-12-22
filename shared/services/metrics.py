# shared/services/metrics.py
from django.core.cache import cache


def increment_metric(key):
    cache.incr(key, 1)
