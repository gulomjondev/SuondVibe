from django.db import models
import uuid

# Create your models here.

class BaseModel(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    id = models.UUIDField(primary_key=True, unique=True,default=uuid.uuid4, editable=False)
    class Meta:
        abstract = True


def metrics():
    return None