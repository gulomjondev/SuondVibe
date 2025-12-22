from .metrics import API_REQUEST_DURATION, USER_LOGIN_COUNT
import time
from django.utils.deprecation import MiddlewareMixin


class MetricsMiddleware(MiddlewareMixin):
    """Maxsus middleware metrikalar yig'ish uchun"""

    def process_request(self, request):
        request.start_time = time.time()
        return None

    def process_response(self, request, response):
        # API request duration
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            API_REQUEST_DURATION.observe(duration)

        # User login tracking
        if request.path == '/login/' and response.status_code == 200:
            if request.user.is_authenticated:
                user_type = 'staff' if request.user.is_staff else 'regular'
                USER_LOGIN_COUNT.labels(user_type=user_type).inc()

        return response