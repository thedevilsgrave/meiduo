from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import CreateAPIView,GenericAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import re
from rest_framework.mixins import UpdateModelMixin

from users.serializers import UserDetailSerializer
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


class PasswordTokenView(GenericAPIView):
    """用户帐号设置密码的token"""
    serializer_class = serializers.CheckSMSCodeSerializer

    def get(self, request, account):
        """
        根据用户帐号获取修改密码的token
        """
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        # 生成修改用户密码的access token
        access_token = user.generate_set_password_token()

        return Response({'user_id': user.id, 'access_token': access_token})


class ModifyPasswordView(UpdateModelMixin, GenericAPIView):
    """重置用户密码"""
    queryset = User.objects.all()
    serializer_class = serializers.ResetPasswordSerializer

    def post(self, request, pk):
        return self.update(request, pk)


class UserDetailView(RetrieveAPIView):
    """用户详细信息"""

    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """返货请求的用户对象"""

        return self.request.user


class EmailView(UpdateAPIView):
    """保存邮箱"""
    serializer_class = serializers.EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class VerifyEmailView(APIView):
    """
    邮箱验证
    """
    def get(self, request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证token
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})