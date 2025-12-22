from django.db import models
from django.conf import settings


class AudioMetric(models.Model):
    audio = models.OneToOneField(
        "audios.Audio",
        on_delete=models.CASCADE,
        related_name="metrics"
    )
    play_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)