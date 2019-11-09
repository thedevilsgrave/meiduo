from django.urls import path, re_path
from .views import OAuthQQUrlView

urlpatterns = [
    re_path(r"^oauth/qq/authorization/$", OAuthQQUrlView.as_view())
]

