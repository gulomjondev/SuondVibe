from django.utils.timezone import now
from django.db.models import F, ExpressionWrapper, FloatField
from django.core.cache import cache

from audios.models import Audio

TRENDING_CACHE_KEY = "trending:audios"
CACHE_TIMEOUT = 300  # 5 min


def get_trending_audios(limit=50):
    cached = cache.get(TRENDING_CACHE_KEY)
    if cached:
        return cached

    queryset = Audio.objects.annotate(
        score=ExpressionWrapper(
            (
                (F("play_count") * 1.0) +
                (F("like_count") * 2.5) +
                (F("comment_count") * 3.0)
            ) / (
                (now() - F("created_at")) / 3600 + 2
            ) ** 1.5,
            output_field=FloatField()
        )
    ).order_by("-score")[:limit]

    data = list(
        queryset.values(
            "id", "title", "score", "play_count", "like_count"
        )
    )

    cache.set(TRENDING_CACHE_KEY, data, CACHE_TIMEOUT)
    return data
