from django.urls import path

from audios.views import TrendingListAPIView

urlpatterns = [
    path('audio/trending/', TrendingListAPIView.as_view(),name='trending'),
]