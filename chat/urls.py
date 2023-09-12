from django.urls import path
from chat import views

urlpatterns = [
    path('chat-room/', views.ChatRoomView.as_view()),
]
