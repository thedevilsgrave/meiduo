from django.shortcuts import render
from rest_framework.generics import CreateAPIView,GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
import re

from . import serializers
from .models import User
from verifications.serializers import CheckImageCodeSerialzier
from .utils import get_user_by_account
# Create your views here.


class UsernameCountView(APIView):
    """
    用户名数量
    """
    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


class MobileCountView(APIView):
    """
    手机号数量
    """
    def get(self, request, mobile):
        """
        获取指定手机号数量
        """
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


class UserView(CreateAPIView):
    """
    用户注册
    """
    serializer_class = serializers.CreateUserSerializer


class SmsCodeTokenView(GenericAPIView):
    """获取发送短息验证码的凭证"""

    serializer_class = CheckImageCodeSerialzier

    def get(self, request, account):

        # 校验图片验证码
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 根据用户名查询用户对象
        user = get_user_by_account(account)
        if user is None:
            return Response({"message": "用户不存在!"}, status=404)

        # 根据用户对象的手机号生成access_token
        access_token = user.generate_send_sms_code_token()
        # 修改手机号中间4为
        return Response({
            "mobile": re.sub(r"(\d{3})\d{4}(\d{3})", r"\1****\2", user.mobile),
            'access_token': access_token,
        })




