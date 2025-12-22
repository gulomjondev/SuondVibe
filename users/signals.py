# posts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post, PostStats


@receiver(post_save, sender=Post)
def create_post_stats(sender, instance, created, **kwargs):
    if created:
        PostStats.objects.create(post=instance)
