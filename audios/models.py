import uuid
from django.db.models import F, Count, IntegerField, ExpressionWrapper

from django.db import models


class Audio(models.Model):
    OWNER = (
        ('system', 'System'),
        ('user', 'User'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.CharField(max_length=20, choices=OWNER, default='system')
    auido_url = models.URLField(max_length=255)
    duration  = models.DurationField(help_text='Duration in seconds')
    created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Audio {self.id} ({self.duration}s)"
