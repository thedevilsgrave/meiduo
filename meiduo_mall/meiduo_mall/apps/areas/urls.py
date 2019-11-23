from django.urls import path, re_path
from .views import AreasViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("areas", AreasViewSet, base_name="area")

urlpatterns = [

]

urlpatterns += router.urls