
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('api/', include('api.urls')),
    path('chat/', include('chat.urls')),
]
