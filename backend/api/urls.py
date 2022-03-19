from django.urls import path

from backend.api.views import HelloView

urlpatterns = [
    path("",HelloView.as_view(),name="index")
]