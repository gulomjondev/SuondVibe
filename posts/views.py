from linecache import cache

from django.db import models
from django.db.models import Count
from django.shortcuts import render
from rest_framework import generics, permissions, viewsets, status, request
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from posts.models import Post, Like, Comment
from posts.serializers import PostCreateSerializer, PostSerializer, CommentSerializer, FeedPostSerializer, \
    NotificationSerializer
import logging
logger = logging.getLogger(__name__)

class PostCreateAPIView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

class FeedApiView(generics.ListAPIView):
    serializer_class = PostCreateSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return (
            Post.objects.select_related('audio','stats').order_by('-created_at')
        )

    def get(self, request):
        try:
            # oldingi feed code
            return Response(request.data)
        except Exception:
            logger.error("Feed crash", exc_info=True)
            return Response(
                {"error": "Server error"},
                status=500
            )

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user

        like_qs = Like.objects.filter(user=user, post=post)

        if like_qs.exists():
            like_qs.delete()
            return Response(
                {'liked': False},
                status=status.HTTP_200_OK
            )

        Like.objects.create(user=user, post=post)
        return Response(
            {'liked': True},
            status=status.HTTP_201_CREATED
        )

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=request.user)

class MySavedPostView(ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Post.objects.filter(user=self.request.user).select_related('post').order_by('-created_at')
        )
class FeedAPIView(APIView):
    def get(self, request):
        key = f"feed:{request.user.id}"
        feed_data = cache.get(key)

        if not feed_data:
            # DB query
            posts = Post.objects.select_related("author") \
                        .annotate(likes_count=Count("likes")) \
                        .order_by("-created_at")[:20]

            serializer = FeedPostSerializer(posts, many=True, context={"request": request})
            feed_data = serializer.data

            # Cache qilish 1 daqiqa
            cache.set(key, feed_data, timeout=60)

        return Response(feed_data)

    def like_post(request, post_id):
        post = Post.objects.get(id=post_id)
        post.likes.add(request.user)

        # Cache yangilash
        cache.delete(f"feed:{request.user.id}")  # old feed cache tozalandi
        return Response({"success": True})


from .models import Post, Notification


def like_post(request, post_id):
    post = Post.objects.get(id=post_id)
    post.likes.add(request.user)

    # Notification yaratish
    if post.author != request.user:  # o‘z post’ingga like bo‘lmasa
        Notification.objects.create(
            user=post.author,
            sender=request.user,
            post=post,
            type="like"
        )

    return Response({"success": True})

class NotificationAPIView(ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return self.request.user.notifications.order_by("-created_at")


# yourapp/middleware.py
from .metrics import API_REQUEST_DURATION, USER_LOGIN_COUNT
import time
from django.utils.deprecation import MiddlewareMixin


class MetricsMiddleware(MiddlewareMixin):
    """Maxsus middleware metrikalar yig'ish uchun"""

    def process_request(self, request):
        request.start_time = time.time()
        return None

    def process_response(self, request, response):
        # API request duration
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            API_REQUEST_DURATION.observe(duration)

        # User login tracking
        if request.path == '/login/' and response.status_code == 200:
            if request.user.is_authenticated:
                user_type = 'staff' if request.user.is_staff else 'regular'
                USER_LOGIN_COUNT.labels(user_type=user_type).inc()

        return response


from django.http import JsonResponse
from .models import Order, Product
from .metrics import ACTIVE_USERS, CART_ADDITIONS, CHECKOUT_COMPLETED
import random
from datetime import datetime, timedelta
from django.contrib.auth.models import User


def dashboard_data(request):
    """Dashboard uchun ma'lumotlar"""
    # Tasodifiy active users metrikasi
    active_users = User.objects.filter(
        last_login__gte=datetime.now() - timedelta(minutes=30)
    ).count()
    ACTIVE_USERS.set(active_users)

    data = {
        'total_orders': Order.objects.count(),
        'revenue_today': Order.objects.filter(
            created_at__date=datetime.now().date(),
            status='completed'
        ).aggregate(models.Sum('total_amount'))['total_amount__sum'] or 0,
        'active_users': active_users,
    }
    return JsonResponse(data)


def add_to_cart(request, product_id):
    """Savatchaga qo'shish - metrikani yangilash"""
    CART_ADDITIONS.inc()
    # ... savatchaga qo'shish logikasi
    return JsonResponse({'status': 'success'})


def checkout(request):
    """Checkout - metrikani yangilash"""
    # ... checkout logikasi
    CHECKOUT_COMPLETED.inc()
    return JsonResponse({'status': 'success'})
