import base64
import pickle

from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from .serialziers import CartSerialziers, CartSKUSerializer, CartSKUDeleteSerializer


# Create your views here.


class CartView(APIView):
    """购物车"""

    def perform_authentication(self, request):
        """重写检查JWT_token正确"""
        pass

    def post(self, request):
        """保存购物车数据"""
        serializer = CartSerialziers(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.data.get('sku_id')
        count = serializer.data.get('count')
        selected = serializer.data.get('selected')

        # 尝试对请求的用户进行验证
        try:
            user = request.user
        except Exception:
            # 验证失败，用户未登录
            user = None

        if user is not None and user.is_authenticated:
            # 用户已登录，在redis中保存
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            # 记录购物车商品数量
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            # 记录购物车的勾选项
            pl.sadd('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(serializer.data)
        else:
            # 用户未登录，在cookie中保存
            # {
            #     1001: { "count": 10, "selected": true},
            #     ...
            # }
            # 使用pickle序列化购物车数据，pickle操作的是bytes类型
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}

            sku = cart.get(sku_id)
            if sku:
                count += int(sku.get('count'))

            cart[sku_id] = {
                'count': count,
                'selected': True
            }
            response = Response(serializer.data)
            response.set_cookie('cart', base64.b64encode(pickle.dumps(cart)).decode())
            return response

    def get(self, request):
        """
           获取购物车
        """
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            # 用户已登录，从redis中读取
            redis_conn = get_redis_connection('cart')
            redis_cart = redis_conn.hgetall('cart_%s' % user.id)
            redis_cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)
            cart = {}
            for key, val in redis_cart.items():
                cart[int(key)] = {
                    'count': int(val),
                    'selected': key in redis_cart_selected
                }
        else:
            # 用户未登录，从cookie中读取
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}

        # 遍历处理购物车数据
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']

        serializer = CartSKUSerializer(skus, many=True)
        return Response(serializer.data)

    def put(self, request):
        """修改购物车"""
        serializer = CartSerialziers(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.data.get('sku_id')
        count = serializer.data.get('count')
        selected = serializer.data.get('selected')

        # 尝试对请求的用户进行验证
        try:
            user = request.user
        except Exception:
            # 验证失败，用户未登录
            user = None

        if user is not None and user.is_authenticated:
            # 用户已登录，在redis中保存
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hset('cart_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            else:
                pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(serializer.data)
        else:
            # 用户未登录，在cookie中保存
            # 使用pickle序列化购物车数据，pickle操作的是bytes类型
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}

            cart[sku_id] = {
                'count': count,
                'selected': selected
            }
            response = Response(serializer.data)
            response.set_cookie('cart', base64.b64encode(pickle.dumps(cart)).decode())
            return response

    def delete(self, request):
        """删除购物车"""
        serializer = CartSKUDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.data['sku_id']

        try:
            user = request.user
        except Exception:
            # 验证失败，用户未登录
            user = None

        if user is not None and user.is_authenticated:
            # 用户已登录，在redis中保存
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            pl.hdel('cart_%s' % user.id, sku_id)
            pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # 用户未登录，在cookie中保存
            response = Response(status=status.HTTP_204_NO_CONTENT)

            # 使用pickle序列化购物车数据，pickle操作的是bytes类型
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
                if sku_id in cart:
                    del cart[sku_id]
                    response.set_cookie('cart', base64.b64encode(pickle.dumps(cart)).decode())
            return response

