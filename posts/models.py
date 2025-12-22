
import uuid

from django.db import models
from django.conf import settings

from audios.models import Audio
from django_prometheus.models import ExportModelOperationsMixin




class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    audio = models.ForeignKey(
        'audios.Audio',
        on_delete=models.CASCADE,
        related_name='posts',
    )
    caption = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post {self.id}"


class PostStats(models.Model):
    post = models.OneToOneField(
        Post,
        on_delete=models.CASCADE,
        related_name='stats'
    )
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Stats for {self.post.id}"


class PostLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='liked_posts',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} — {self.text[:20]}'


class SavedPost(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='saved_by',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class Notification(models.Model):
    TYPES = (
        ("like", "Like"),
        ("comment", "Comment"),
        ("follow", "Follow"),
        ("moderation", "Moderation"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="actor_notifications"
    )
    type = models.CharField(max_length=20, choices=TYPES)
    object_id = models.PositiveIntegerField(null=True)
    text = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Order(ExportModelOperationsMixin('order'), models.Model):
    """Buyurtma modeli - avtomatik metrikalar ExportModelOperationsMixin bilan"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Yangi order yaratilganda metrikani yangilash
        if is_new:
            from .metrics import ORDERS_CREATED
            ORDERS_CREATED.inc()

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"


class Product(ExportModelOperationsMixin('product'), models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name