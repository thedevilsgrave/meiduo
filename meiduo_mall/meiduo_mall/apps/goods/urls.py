from django.urls import path, re_path
# from rest_framework_jwt.views import obtain_jwt_token
from . import views

urlpatterns = [
    re_path(r"categories/(?P<category_id>\d+)/hotskus/", views.HotSKUListView.as_view())
]












