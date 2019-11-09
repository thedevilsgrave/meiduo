from meiduo_mall.settings.dev import QQ_APP_ID, QQ_REDIRECT_URL, QQ_APP_KEY
from urllib.parse import urlencode


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



