from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from meiduo_mall.settings.dev import SECRET_KEY

# Create your models here.
from verifications import constants


class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def generate_send_sms_code_token(self):
        """生成发送短息验证码token"""

        # 创建is_dangerous转换工具
        serializer = TJWSSerializer(SECRET_KEY, expires_in=constants.SEND_SMS_TOKEN_EXPIRES)
        data = {'mobile': self.mobile}
        token = serializer.dumps(data)
        return token.decode()

    @staticmethod
    def check_access_token(token):
        """校验access_token"""
        # 创建is_dangerous转换工具
        serializer = TJWSSerializer(SECRET_KEY, expires_in=constants.SEND_SMS_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            mobile = data.get("mobile")
            return mobile

    def generate_set_password_token(self):
        """
        生成修改密码的token
        """
        serializer = TJWSSerializer(SECRET_KEY, expires_in=constants.SET_PASSWORD_TOKEN_EXPIRES)
        data = {'user_id': self.id}
        token = serializer.dumps(data)
        return token.decode()

    @staticmethod
    def check_set_password_token(token, user_id):
        """
        检验设置密码的token
        """
        serializer = TJWSSerializer(SECRET_KEY, expires_in=constants.SET_PASSWORD_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return False
        else:
            if user_id != str(data.get('user_id')):
                return False
            else:
                return True
