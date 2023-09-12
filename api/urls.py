from django.urls import path
from api import views

urlpatterns = [
    path('login/', views.LoginAPI.as_view()),
    path('refresh-token/', views.RefreshTokenView.as_view()),
    path('register/', views.RegistrationView.as_view()),
    path('online-users/', views.OnlineUserList.as_view(), name='users'),
    # path('api-token/', views.CustomTokenObtainView.as_view(), name='api_token'),
    path('suggested-friends/<int:user_id>/', views.RecommendFriendsView.as_view()),
]
