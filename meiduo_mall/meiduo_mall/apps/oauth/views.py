from django.shortcuts import render

from carts.utils import merge_cart_cookie_to_redis
from .utils import OAuthQQ
from .models import OauthUser
# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_jwt.settings import api_settings


class OAuthQQUrlView(APIView):
    """
    提供QQ登录的网址,
    前端请求的接口网址: /oauth/qq/authorization/state=xxxxxxxx
    state值是前段传递,参数值为QQ登录成功后,我们后端吧用户引导到那个项目页面
    """

    def get(self, request):
        # 提取state参数
        state = request.query_params.get("state")

        if not state:
            state = "/"       # 前段如果没有传默认引导到首页

        # 按照QQ文档说明拼接用户登录链接地址
        oauth_qq = OAuthQQ(state=state)
        login_url = oauth_qq.generate_qq_login_url()

        return Response({"oauth_url": login_url})


class QQAuthUserView(APIView):
    """
    QQ登录的用户
    """
    def get(self, request):
        """
        获取qq登录的用户数据
        """
        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)

        oauth = OAuthQQ()

        # 获取用户openid
        try:
            access_token = oauth.get_access_token(code)
            openid = oauth.get_openid(access_token)
        except Exception:
            return Response({'message': 'QQ服务异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 判断用户是否存在
        try:
            qq_user = OauthUser.objects.get(openid=openid)
        except OauthUser.DoesNotExist:
            # 用户第一次使用QQ登录
            token = oauth.generate_save_user_token(openid)
            return Response({'access_token': token})
        else:
            # 找到用户, 生成token
            user = qq_user.user
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            response = Response({
                'token': token,
                'user_id': user.id,
                'username': user.username
            })
            response = merge_cart_cookie_to_redis(request, user, response)
            return response