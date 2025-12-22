from django.contrib import admin
from django.urls import path,include
from django_prometheus import exports

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('posts/', include('posts.urls')),
    path('metrics/', exports.ExportToDjangoView, name='prometheus-django-metrics'),

]
