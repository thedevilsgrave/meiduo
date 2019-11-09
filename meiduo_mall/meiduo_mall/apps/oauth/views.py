from django.shortcuts import render
from .utils import OAuthQQ
# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView


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
