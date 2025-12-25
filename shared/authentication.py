from rest_framework.authentication import BaseAuthentication
from users.models import User
from .external_auth import get_external_user

class ExternalJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get("Authorization")

        if not auth:
            return None

        token = auth.split(" ")[1]
        data = get_external_user(token)

        if not data:
            return None

        user, _ = User.objects.get_or_create(
            external_id=data["id"],
            defaults={
                "username": data["username"],
                "email": data.get("email", "")
            }
        )

        return (user, None)
# shared/authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

class CoreJWTAuthentication(BaseAuthentication):
    """
    Custom JWT authentication example.
    """
    def authenticate(self, request):
        # JWTAuthentication dan foydalanish
        jwt_auth = JWTAuthentication()
        return jwt_auth.authenticate(request)
