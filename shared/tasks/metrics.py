# shared/tasks/metrics.py
from celery import shared_task
from django.core.cache import cache
from audios.models import Audio
from shared.metrics import AudioMetric


@shared_task
def sync_audio_metrics():
    for audio in Audio.objects.all().only("id"):
        play = cache.get(f"audio:{audio.id}:play", 0)
        like = cache.get(f"audio:{audio.id}:like", 0)

        metric, _ = AudioMetric.objects.get_or_create(audio=audio)
        metric.play_count += play
        metric.like_count += like
        metric.save()

        cache.delete_many([
            f"audio:{audio.id}:play",
            f"audio:{audio.id}:like"
        ])
