from django.contrib.auth.backends import ModelBackend
import re
from .models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_account(account):
    """根基账号信息查找用户对象"""

    try:
        # 判断acc是否是手机号,如果是则根据手机号查询
        if re.match('^1[345789]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            # 如果不是则根据账户名查询
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UserNameMobileAuthenticate(ModelBackend):
    """自定义的认证后端"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 根据user_name查询用户对象    username可以是用户名也可以是用户手机号

        user = get_user_by_account(username)
        # 如果用户存在则调用check_password
        if user is not None and user.check_password(password):
            # 验证成功返回用户对象
            return user





