import json

from itsdangerous import Serializer

# from meiduo_mall import settings
from django.conf import settings
from meiduo_mall.settings.dev import QQ_APP_ID, QQ_REDIRECT_URL, QQ_APP_KEY
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen

from verifications import constants
from .exceptions import QQAPIException
from users.serializers import logger


class OAuthQQ(object):
    """
    专门用于用户QQ登录类
    提供QQ登录用到的方法
    """

    def __init__(self, app_id=None, app_key=None, qq_redirect_url=None, state=None):
        self.app_id = app_id or QQ_APP_ID
        self.app_key = app_key or QQ_APP_KEY
        self.qq_redirect_url = qq_redirect_url or QQ_REDIRECT_URL
        self.state = state or "/"    # 用于保存登录成功后的跳转页面路径

    def generate_qq_login_url(self):
        """用于拼接用户QQ登录链接地址"""
        params = {
            'response_type': 'code',
            'client_id': self.app_id,
            'redirect_uri': self.qq_redirect_url,
            'state': self.state,
            'scope': 'get_user_info',
        }
        url = 'https://graph.qq.com/oauth2.0/authorize?' + urlencode(params)
        return url

    def get_access_token(self, code):
        """
        获取access_token
        :param code: qq提供的code
        :return: access_token
        """
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.app_id,
            'client_secret': self.app_key,
            'code': code,
            'redirect_uri': self.redirect_url
        }
        url = 'https://graph.qq.com/oauth2.0/token?' + urlencode(params)
        response = urlopen(url)
        response_data = response.read().decode()
        data = parse_qs(response_data)
        access_token = data.get('access_token', None)
        if not access_token:
            logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
            raise QQAPIException('获取access_token异常')

        return access_token[0]

    def get_openid(self, access_token):
        """
        获取用户的openid
        :param access_token: qq提供的access_token
        :return: open_id
        """
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token
        response = urlopen(url)
        response_data = response.read().decode()
        try:
            # 返回的数据 callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;
            data = json.loads(response_data[10:-4])
        except Exception:
            data = parse_qs(response_data)
            logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
            raise QQAPIException('获取access_token异常')
        openid = data.get('openid', None)
        return openid

    @staticmethod
    def generate_save_user_token(openid):
        """
        生成保存用户数据的token
        :param openid: 用户的openid
        :return: token
        """
        serializer = Serializer(settings.SECRET_KEY, expires_in=constants.SAVE_QQ_USER_TOKEN_EXPIRES)
        data = {'openid': openid}
        token = serializer.dumps(data)
        return token.decode()

