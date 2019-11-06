# from django.conf.urls import url
from django.urls import path, re_path

from . import views

urlpatterns = [
    re_path(r'image_codes/(?P<image_code_id>.+)/$', views.ImageCodeView.as_view()),
    re_path(r'sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
]