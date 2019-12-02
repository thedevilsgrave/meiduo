# from django.conf.urls import url
from django.urls import path, re_path
from rest_framework_jwt.views import obtain_jwt_token
from . import views

urlpatterns = [
    re_path(r'^users/$', views.UserView.as_view()),
    re_path(r'usernames/(?P<username>\w{5,20})/count/', views.UsernameCountView.as_view()),
    re_path(r'mobiles/(?P<mobile>1[345789]\d{9})/count/', views.MobileCountView.as_view()),
    re_path(r"authorizations/", obtain_jwt_token),    # 登录,获取JWT-token
    re_path(r"accounts/(?P<account>\w{5,20})/sms/token/", views.SmsCodeTokenView.as_view()),        # 获取短息验证码的token
    re_path(r"accounts/(?P<account>\w{5,20})/password/token/", views.PasswordTokenView.as_view()),  # 修改密码的token
    re_path(r"users/(?P<pk>\d+)/password/", views.ModifyPasswordView.as_view()),  # 修改密码的token
    re_path(r"^user/$", views.UserDetailView.as_view()),
    re_path(r"emails/", views.EmailView.as_view()),
    re_path(r"emails/verification/", views.VerifyEmailView.as_view()),
    re_path(r"browse_histories/", views.UserBrowsingHistoryView.as_view()),
]
