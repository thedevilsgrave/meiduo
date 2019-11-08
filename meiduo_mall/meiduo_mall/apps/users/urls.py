# from django.conf.urls import url
from django.urls import path, re_path
from rest_framework_jwt.views import obtain_jwt_token
from . import views

urlpatterns = [
    re_path(r'^users/$', views.UserView.as_view()),
    re_path(r'usernames/(?P<username>\w{5,20})/count/', views.UsernameCountView.as_view()),
    re_path(r'mobiles/(?P<mobile>1[345789]\d{9})/count/', views.MobileCountView.as_view()),
    re_path(r"authorizations/", obtain_jwt_token),    # 登录,获取JWT-token
    re_path(r"accounts/(?P<account>\w{5,20})/sms/token/", views.SmsCodeTokenView.as_view())
]
