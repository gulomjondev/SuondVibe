from rest_framework import serializers
from .models import Audio

class AudioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Audio
        fields = '__all__'

class TrendingAudioSerializer(serializers.ModelSerializer):
    posts_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Audio
        fields = (
            'id',
            'audio_url',
            'duration',
            'posts_count',
        )


