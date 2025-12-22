from celery import shared_task
from django.core.cache import cache
from django.db.models import Count

from .models import Post, Notification
from .serializers import FeedPostSerializer


@shared_task
def calculate_feed():
    posts = (
        Post.objects
        .select_related("author")
        .annotate(likes_count=Count("likes"))
        .order_by("-created_at")[:20]
    )

    serializer = FeedPostSerializer(posts, many=True)
    feed_data = serializer.data

    # Global feed
    cache.set("feed:global", feed_data, timeout=900)

    # User feeds (faqat keylar farq qiladi)
    from django.contrib.auth import get_user_model
    User = get_user_model()

    for user_id in User.objects.values_list("id", flat=True):
        cache.set(f"feed:{user_id}", feed_data, timeout=900)
@shared_task
def calculate_trending_audio():
    trending_audio = (
        Post.objects
        .values("audio__id", "audio__title")
        .annotate(likes_count=Count("likes"))
        .order_by("-likes_count")[:10]
    )

    cache.set("trending:audio", list(trending_audio), timeout=900)

@shared_task
def send_notification_task(notification_id):
    notification = Notification.objects.get(id=notification_id)

    # bu yerda:
    # - push
    # - websocket
    # - email
    pass