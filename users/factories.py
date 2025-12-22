import factory
from users.models import User, Profile

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'testpassword123')

class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    bio = "This is a test bio"
    gender = "other"
