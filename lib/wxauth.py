import requests
from lib.WXBizDataCrypt import WXBizDataCrypt

# 你注册小程序的app_id和app_secret
WXAPP_ID = 'wxfece5910e33d1336'
WXAPP_SECRET = '1379baa802a9078bfb3508169e4f4ed9'


def get_wxapp_session_key(code):
    """小程序登录凭证校验"""
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code' % (
        WXAPP_ID, WXAPP_SECRET, code)
    data = requests.get(url).json()
    print(data)
    return data


def get_user_info(session_key):
    """获取用户信息"""
    pc = WXBizDataCrypt(WXAPP_ID, session_key)
    return pc.decrypt(encryptedData,iv)
