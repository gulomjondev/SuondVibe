from datetime import timedelta

from django.test import TestCase

# Create your tests here.
import pytest
from unittest import TestCase

from django.utils import timezone
from users.models import User, UserConfirmation, VIA_EMAIL, VIA_PHONE
from users.factories import UserFactory

@pytest.mark.django_db
def test_user_creation():
    user = UserFactory()
    assert user.username.startswith("user")
    assert user.check_password("testpassword123")

@pytest.mark.django_db
def test_user_full_name():
    user = UserFactory(first_name="John", last_name="Doe")
    assert user.full_name == "John Doe"

@pytest.mark.django_db
def test_user_token():
    user = UserFactory()
    token = user.token()
    assert "access" in token and "refresh" in token

@pytest.mark.django_db
def test_user_verification_code_creation():
    user = UserFactory()
    code = user.create_verify_code(verify_type="via_email")
    confirmation = UserConfirmation.objects.get(user=user)
    assert confirmation.code == code
    assert confirmation.verify_type == "via_email"
    assert confirmation.expiration_time > timezone.now()
    assert not confirmation.is_confirmed
@pytest.mark.django_db
def test_profile_creation():
    user = UserFactory()
    profile = user.profile
    profile.bio = "Hello"
    profile.save()
    assert profile.bio == "Hello"

@pytest.mark.django_db
def test_user_confirmation_expiration_email():
    user = UserFactory()
    uc = UserConfirmation.objects.create(user=user, code="1234", verify_type=VIA_EMAIL)
    assert uc.expiration_time > timezone.now()
    assert uc.expiration_time <= timezone.now() + timedelta(minutes=5)

@pytest.mark.django_db
def test_user_confirmation_expiration_phone():
    user = UserFactory()
    uc = UserConfirmation.objects.create(user=user, code="1234", verify_type=VIA_PHONE)
    assert uc.expiration_time > timezone.now()
    assert uc.expiration_time <= timezone.now() + timedelta(minutes=2)