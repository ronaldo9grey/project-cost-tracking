"""
微信公众号服务
支持个人订阅号和服务号
用于微信授权登录和模板消息推送
"""

import requests
import json
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta


class WeChatOfficialService:
    """微信公众号服务"""
    
    BASE_URL = "https://api.weixin.qq.com/cgi-bin"
    OAUTH_URL = "https://open.weixin.qq.com/connect/oauth2"
    
    # 模板消息ID配置（需要在公众号后台申请）
    TEMPLATES = {
        'daily_report_reminder': {
            'id': '',  # 日报填写提醒模板ID
            'url': '/mobile/daily-report.html'
        },
        'evaluation_notification': {
            'id': '',  # 评价通知模板ID
            'url': '/mobile/index.html'
        },
        'pending_evaluation': {
            'id': '',  # 待评价提醒模板ID
            'url': '/mobile/index.html'
        }
    }
    
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化公众号服务
        
        Args:
            app_id: 公众号AppID
            app_secret: 公众号AppSecret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expires_at = None
        self.jsapi_ticket = None
        self.ticket_expires_at = None
    
    def get_auth_url(self, redirect_uri: str, scope: str = "snsapi_userinfo", state: str = "") -> str:
        """
        获取微信授权URL
        
        Args:
            redirect_uri: 授权后重定向地址
            scope: 授权作用域 (snsapi_base/snsapi_userinfo)
            state: 自定义参数
            
        Returns:
            授权URL
        """
        from urllib.parse import quote
        redirect_uri_encoded = quote(redirect_uri, safe='')
        
        auth_url = (
            f"{self.OAUTH_URL}/authorize?"
            f"appid={self.app_id}&"
            f"redirect_uri={redirect_uri_encoded}&"
            f"response_type=code&"
            f"scope={scope}&"
            f"state={state}"
            f"#wechat_redirect"
        )
        return auth_url
    
    def get_access_token_by_code(self, code: str) -> Tuple[str, str]:
        """
        通过code获取用户access_token和openid
        
        Args:
            code: 授权code
            
        Returns:
            (access_token, openid)
        """
        url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        params = {
            "appid": self.app_id,
            "secret": self.app_secret,
            "code": code,
            "grant_type": "authorization_code"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "access_token" in data:
            return data["access_token"], data["openid"]
        else:
            raise Exception(f"获取access_token失败: {data.get('errmsg', '未知错误')}")
    
    def get_user_info(self, access_token: str, openid: str) -> Dict:
        """
        获取用户信息（需要snsapi_userinfo授权）
        
        Args:
            access_token: 用户access_token
            openid: 用户openid
            
        Returns:
            用户信息字典
        """
        url = "https://api.weixin.qq.com/sns/userinfo"
        params = {
            "access_token": access_token,
            "openid": openid,
            "lang": "zh_CN"
        }
        
        response = requests.get(url, params=params, timeout=10)
        return response.json()
    
    def _get_base_access_token(self) -> str:
        """获取公众号基础access_token（用于模板消息等）"""
        import time
        
        # 检查token是否过期
        if self.access_token and self.token_expires_at and time.time() < self.token_expires_at:
            return self.access_token
        
        url = f"{self.BASE_URL}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if "access_token" in data:
            self.access_token = data["access_token"]
            # token 有效期7200秒，提前300秒刷新
            self.token_expires_at = time.time() + data["expires_in"] - 300
            return self.access_token
        else:
            raise Exception(f"获取access_token失败: {data.get('errmsg', '未知错误')}")
    
    def send_template_message(
        self,
        openid: str,
        template_id: str,
        url: str,
        data: Dict,
        miniprogram: Optional[Dict] = None
    ) -> bool:
        """
        发送模板消息
        
        Args:
            openid: 用户openid
            template_id: 模板ID
            url: 点击消息后跳转的URL
            data: 模板数据
            miniprogram: 可选，跳转到小程序
            
        Returns:
            是否发送成功
        """
        access_token = self._get_base_access_token()
        api_url = f"{self.BASE_URL}/message/template/send?access_token={access_token}"
        
        payload = {
            "touser": openid,
            "template_id": template_id,
            "url": url,
            "data": data
        }
        
        if miniprogram:
            payload["miniprogram"] = miniprogram
        
        try:
            response = requests.post(api_url, json=payload, timeout=10)
            result = response.json()
            
            if result.get("errcode") == 0:
                print(f"模板消息发送成功: {openid}")
                return True
            else:
                print(f"模板消息发送失败: {result.get('errmsg')}")
                return False
        except Exception as e:
            print(f"发送模板消息异常: {str(e)}")
            return False
    
    def send_daily_report_reminder(self, openid: str, user_name: str, report_date: str, domain: str) -> bool:
        """发送日报填写提醒"""
        template = self.TEMPLATES.get('daily_report_reminder', {})
        template_id = template.get('id', '')
        
        if not template_id:
            print("未配置日报提醒模板ID")
            return False
        
        url = f"{domain}{template.get('url', '/mobile/daily-report.html')}"
        
        data = {
            "first": {"value": f"您好{user_name}，请及时填写工作日报", "color": "#173177"},
            "keyword1": {"value": report_date, "color": "#173177"},  # 日期
            "keyword2": {"value": "工作日报", "color": "#173177"},  # 类型
            "keyword3": {"value": "未填写", "color": "#FF6B6B"},  # 状态
            "remark": {"value": "点击此消息可直接进入日报填报页面", "color": "#666666"}
        }
        
        return self.send_template_message(openid, template_id, url, data)
    
    def send_evaluation_notification(
        self,
        openid: str,
        user_name: str,
        evaluator_name: str,
        rating: str,
        evaluation_date: str,
        domain: str
    ) -> bool:
        """发送评价通知"""
        template = self.TEMPLATES.get('evaluation_notification', {})
        template_id = template.get('id', '')
        
        if not template_id:
            print("未配置评价通知模板ID")
            return False
        
        url = f"{domain}{template.get('url', '/mobile/index.html')}"
        
        rating_text = {"A": "超目标达成", "B": "按目标达成", "C": "基本达标", "D": "需要改进"}.get(rating, "已评价")
        
        data = {
            "first": {"value": f"您好{user_name}，您的日报已被评价", "color": "#173177"},
            "keyword1": {"value": evaluator_name, "color": "#173177"},  # 评价人
            "keyword2": {"value": f"{rating} ({rating_text})", "color": "#52C41A"},  # 评价结果
            "keyword3": {"value": evaluation_date, "color": "#173177"},  # 评价时间
            "remark": {"value": "点击此消息查看详情", "color": "#666666"}
        }
        
        return self.send_template_message(openid, template_id, url, data)
    
    def get_jsapi_config(self, url: str) -> Dict:
        """
        获取JS-SDK配置（用于微信分享、拍照等）
        
        Args:
            url: 当前页面URL
            
        Returns:
            JS-SDK配置参数
        """
        import time
        import hashlib
        import random
        
        # 获取jsapi_ticket
        ticket = self._get_jsapi_ticket()
        
        # 生成随机字符串
        nonce_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=16))
        timestamp = int(time.time())
        
        # 拼接字符串
        string1 = f"jsapi_ticket={ticket}&noncestr={nonce_str}&timestamp={timestamp}&url={url}"
        signature = hashlib.sha1(string1.encode()).hexdigest()
        
        return {
            "appId": self.app_id,
            "timestamp": timestamp,
            "nonceStr": nonce_str,
            "signature": signature
        }
    
    def _get_jsapi_ticket(self) -> str:
        """获取JS-SDK ticket"""
        import time
        
        if self.jsapi_ticket and self.ticket_expires_at and time.time() < self.ticket_expires_at:
            return self.jsapi_ticket
        
        access_token = self._get_base_access_token()
        url = f"{self.BASE_URL}/ticket/getticket"
        params = {
            "access_token": access_token,
            "type": "jsapi"
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get("errcode") == 0:
            self.jsapi_ticket = data["ticket"]
            self.ticket_expires_at = time.time() + data["expires_in"] - 300
            return self.jsapi_ticket
        else:
            raise Exception(f"获取jsapi_ticket失败: {data.get('errmsg')}")


# 全局服务实例
wechat_official_service: Optional[WeChatOfficialService] = None


def init_wechat_official_service(app_id: str, app_secret: str):
    """初始化公众号服务"""
    global wechat_official_service
    wechat_official_service = WeChatOfficialService(app_id, app_secret)
    return wechat_official_service


def get_wechat_official_service() -> Optional[WeChatOfficialService]:
    """获取公众号服务实例"""
    return wechat_official_service
