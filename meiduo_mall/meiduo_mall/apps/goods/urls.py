from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
# from rest_framework_jwt.views import obtain_jwt_token
from . import views

urlpatterns = [
    re_path(r"categories/(?P<category_id>\d+)/skus/", views.SKUListView.as_view()),
    re_path(r"categories/(?P<category_id>\d+)/hotskus/", views.HotSKUListView.as_view())
]

router = DefaultRouter()
router.register('skus/search', views.SKUSearchViewSet, base_name='skus_search')


urlpatterns += router.urls







