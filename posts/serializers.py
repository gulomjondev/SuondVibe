from rest_framework import serializers
from posts.models import Post, Comment, Notification


class PostCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = (
            'id',
            'image_url',
            'audio',
            'caption',
        )

class FeedPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username")
    like_count = serializers.IntegerField(source='stats.like_count', read_only=True)
    comment_count = serializers.IntegerField(source='stats.comment_count', read_only=True)

    class Meta:
        model = Post

        fields = (
            'id',
            'image',
            'audio',
            'caption',
            'like_count',
            'comment_count',
            'created_at',
            'author_name',
        )

class PostSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(source='stats.like_count', read_only=True)
    is_liked = serializers.SerializerMethodField()
    saved_count = serializers.IntegerField(source='saved_by.count', read_only=True)
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'
        extra_fields = ('likes_count', 'is_liked')

        def get_is_liked(self, obj):
            user = self.context['request'].user
            if user.is_anonymous:
                return False
            return obj.likes.filter(user=user).exists()

        def  get_is_saved(self, obj):
            user = self.context['request'].user
            if user.is_anonymous:
                return False
            return obj.saved_by.filter(user=user).exists()



class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'user', 'user_name', 'post', 'text', 'created_at')
        read_only_fields = ('user', 'created_at')

class SavedPostSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)

    class Meta:
        model = Post
        fields = (
            'id',
            'post',
            'created_at'
        )

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
