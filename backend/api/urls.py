from django.urls import path

from backend.api.views import HelloView,UserInfoView,RegisterView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
    )

urlpatterns = [
    path("",HelloView.as_view(),name="index"),
    path("userInfo/",UserInfoView.as_view(),name="userdata"),
    path('login/',TokenObtainPairView.as_view(),name="login"),
    path('login/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('register/', RegisterView.as_view(), name="register"),
]