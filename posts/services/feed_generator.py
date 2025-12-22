from django.db.models import Case, When, Value, IntegerField
from django.core.cache import cache

from posts.models import Post
from shared.cache_keys import user_feed_key

CACHE_TIMEOUT = 300


def generate_user_feed(user):
    key = user_feed_key(user.id)
    cached = cache.get(key)
    if cached:
        return cached

    following_ids = user.following.values_list("id", flat=True)

    queryset = (
        Post.objects
        .annotate(
            follow_bonus=Case(
                When(user_id__in=following_ids, then=Value(10)),
                default=Value(0),
                output_field=IntegerField()
            )
        )
        .order_by("-follow_bonus", "-created_at")[:100]
    )

    feed = list(
        queryset.values(
            "id", "content", "user_id", "created_at"
        )
    )

    cache.set(key, feed, CACHE_TIMEOUT)
    return feed
