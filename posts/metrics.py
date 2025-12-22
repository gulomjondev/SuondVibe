# yourapp/metrics.py
from prometheus_client import Counter, Gauge, Histogram, Summary
from django_prometheus.models import ExportModelOperationsMixin
from django.db import models
import time

# Business metrikalar
ORDERS_CREATED = Counter('orders_created_total', 'Total number of orders created')
ACTIVE_USERS = Gauge('active_users_count', 'Number of active users in last 30 minutes')
API_REQUEST_DURATION = Histogram('api_request_duration_seconds', 'API request duration')
DATABASE_QUERY_TIME = Summary('database_query_duration_seconds', 'Time spent on database queries')

# User faollik metrikasi
USER_LOGIN_COUNT = Counter('user_login_total', 'Total user logins', ['user_type'])
CART_ADDITIONS = Counter('cart_add_item_total', 'Items added to cart')
CHECKOUT_COMPLETED = Counter('checkout_completed_total', 'Completed checkouts')