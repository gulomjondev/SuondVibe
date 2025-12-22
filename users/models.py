import uuid
import secrets
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from shared.models import BaseModel


# Constants
ORDINARY_USER, MANAGER, ADMIN = ('ordinary_user', 'manager', 'admin')
VIA_PHONE, VIA_EMAIL = ('via_phone', 'via_email')
NEW, CODE_VERIFIED, DONE, PHOTO_STEP = ('new', 'code_verified', 'done', 'photo_step')

EMAIL_EXPIRE_MINUTES = 5
PHONE_EXPIRE_MINUTES = 2


class User(AbstractUser):
    USER_ROLES = (
        (ORDINARY_USER, ORDINARY_USER),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN),
    )

    AUTH_TYPE_CHOICES = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL)
    )

    AUTH_STATUS_CHOICES = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHOTO_STEP, PHOTO_STEP),
    )

    user_roles = models.CharField(max_length=31, choices=USER_ROLES, default=ORDINARY_USER)
    auth_status = models.CharField(max_length=31, choices=AUTH_STATUS_CHOICES, default=NEW)
    auth_type_choices = models.CharField(max_length=31, choices=AUTH_TYPE_CHOICES, default=VIA_PHONE)
    email = models.EmailField(null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=13, null=True, blank=True, unique=True)
    photo = models.ImageField(
        null=True,
        blank=True,
        upload_to='user_photos/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png','heif','webp'])]
    )
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def generate_verification_code(self):
        """Secure 4-digit code"""
        return ''.join(str(secrets.randbelow(10)) for _ in range(4))

    def create_verify_code(self, verify_type=None):
        from users.models import UserConfirmation
        code = self.generate_verification_code()
        UserConfirmation.objects.create(
            user=self,
            verify_type=verify_type,
            code=code
        )
        return code

    def ensure_username(self):
        """Generate unique username if empty"""
        if not self.username:
            while True:
                temp_username = f"vibe-{uuid.uuid4().hex[:8]}"
                if not User.objects.filter(username=temp_username).exists():
                    self.username = temp_username
                    break

    def normalize_email(self):
        if self.email:
            self.email = self.email.lower()

    def ensure_password(self):
        """Set a random password if empty"""
        if not self.password:
            self.set_password(f"password-{uuid.uuid4().hex[:8]}")
        elif not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)

    def clean(self):
        self.ensure_username()
        self.normalize_email()
        self.ensure_password()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)


class UserConfirmation(BaseModel):
    TYPE_CHOICES = (
        (VIA_PHONE, VIA_PHONE),
        (VIA_EMAIL, VIA_EMAIL)
    )

    code = models.CharField(max_length=4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verify_codes')
    verify_type = models.CharField(max_length=31, choices=TYPE_CHOICES)
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            expire_minutes = EMAIL_EXPIRE_MINUTES if self.verify_type == VIA_EMAIL else PHONE_EXPIRE_MINUTES
            self.expiration_time = timezone.now() + timedelta(minutes=expire_minutes)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.code}"
