from django.shortcuts import render
from rest_framework.views import APIView
from django_redis import get_redis_connection
from django.http.response import HttpResponse

from meiduo_mall.libs.captcha.captcha import captcha
from . import constants
# Create your views here.


class ImageCodeView(APIView):
    """
    图片验证码
    """
    def get(self, request, image_code_id):

        # 生成验证码图片
        text, image = captcha.generate_captcha()

        # 获取redis的连接对象
        redis_conn = get_redis_connection("verify_codes")
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return HttpResponse(image, content_type="images/jpg")

