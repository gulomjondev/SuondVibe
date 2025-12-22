from platform import system

from django.db.models import Count
from django.shortcuts import render

# Create your views here.

from rest_framework import generics
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from audios.models import Audio
from audios.serializers import AudioSerializer, TrendingAudioSerializer
from .services.trending import get_trending_audios


class AudioCreateAPIView(CreateAPIView):
    serializer_class = AudioSerializer
    permission_classes = [IsAdminUser]

class TrendingListAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = TrendingAudioSerializer

    def get_queryset(self):
        return (
            Audio.objects.filter(owner='system').annotate(posts_cunt=Count('posts')).order_by('-created_at','-posts_count')
        )
class TrendingAudioView(APIView):
    def get(self,request):
        return Response(get_trending_audios())
