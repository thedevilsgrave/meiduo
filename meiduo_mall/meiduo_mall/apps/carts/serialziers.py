from rest_framework import serializers
from goods.models import SKU


class CartSerialziers(serializers.Serializer):
    """
    购物车序列化器
    """
    sku_id = serializers.IntegerField(min_value=1)

    counts = serializers.IntegerField(min_value=1)

    selected = serializers.BooleanField(default=True)

    def validate(self, attrs):
        sku_id = attrs["sku_id"]
        try:
            sku = SKU.objects.get(id=sku_id)
        except Exception:
            raise serializers.ValidationError("商品不存在")

        counts = attrs["counts"]
        if sku.stock < counts:
            raise serializers.ValidationError('商品库存不足')

        return attrs


class CartSKUSerializer(serializers.ModelSerializer):
    """
    购物车商品数据序列化器
    """
    count = serializers.IntegerField(label='数量')
    selected = serializers.BooleanField(label='是否勾选')

    class Meta:
        model = SKU
        fields = ('id', 'count', 'name', 'default_image_url', 'price', 'selected')


class CartSKUDeleteSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(min_value=1)

    def validate_sku_id(self, value):
        try:
            sku = SKU.objects.get(id=value)
        except Exception:
            raise serializers.ValidationError("商品不存在")

        return value
