"""
微信通知服务模块
支持企业微信应用消息推送
"""

import json
import requests
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.daily_report import DailyReport
from app.models.resource import Personnel
from app.models.daily_report_evaluation import DailyReportEvaluation


class WeChatNotificationService:
    """企业微信通知服务"""
    
    BASE_URL = "https://qyapi.weixin.qq.com/cgi-bin"
    
    def __init__(self, corp_id: str, corp_secret: str, agent_id: str):
        """
        初始化微信通知服务
        
        Args:
            corp_id: 企业ID
            corp_secret: 应用凭证密钥
            agent_id: 应用ID
        """
        self.corp_id = corp_id
        self.corp_secret = corp_secret
        self.agent_id = agent_id
        self.access_token = None
        self.token_expires_at = None
    
    def _get_access_token(self) -> str:
        """获取企业微信 access_token"""
        # 检查token是否过期
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        # 重新获取token
        url = f"{self.BASE_URL}/gettoken"
        params = {
            "corpid": self.corp_id,
            "corpsecret": self.corp_secret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("errcode") == 0:
                self.access_token = data["access_token"]
                # token 有效期2小时，提前5分钟刷新
                self.token_expires_at = datetime.now() + timedelta(seconds=data["expires_in"] - 300)
                return self.access_token
            else:
                raise Exception(f"获取access_token失败: {data.get('errmsg')}")
        except Exception as e:
            raise Exception(f"请求access_token失败: {str(e)}")
    
    def send_text_message(
        self,
        user_id: str,
        content: str,
        safe: int = 0
    ) -> bool:
        """
        发送文本消息
        
        Args:
            user_id: 用户ID（企业微信中的UserID）
            content: 消息内容
            safe: 是否是保密消息，0-否，1-是
            
        Returns:
            是否发送成功
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}/message/send?access_token={access_token}"
        
        data = {
            "touser": user_id,
            "msgtype": "text",
            "agentid": self.agent_id,
            "text": {
                "content": content
            },
            "safe": safe
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get("errcode") == 0:
                return True
            else:
                print(f"发送消息失败: {result.get('errmsg')}")
                return False
        except Exception as e:
            print(f"发送消息异常: {str(e)}")
            return False
    
    def send_text_card(
        self,
        user_id: str,
        title: str,
        description: str,
        url: Optional[str] = None,
        btntxt: str = "查看详情"
    ) -> bool:
        """
        发送文本卡片消息
        
        Args:
            user_id: 用户ID
            title: 标题
            description: 描述
            url: 点击后跳转的链接
            btntxt: 按钮文字
            
        Returns:
            是否发送成功
        """
        access_token = self._get_access_token()
        api_url = f"{self.BASE_URL}/message/send?access_token={access_token}"
        
        data = {
            "touser": user_id,
            "msgtype": "textcard",
            "agentid": self.agent_id,
            "textcard": {
                "title": title,
                "description": description,
                "url": url or "",
                "btntxt": btntxt
            }
        }
        
        try:
            response = requests.post(api_url, json=data, timeout=10)
            result = response.json()
            
            if result.get("errcode") == 0:
                return True
            else:
                print(f"发送卡片消息失败: {result.get('errmsg')}")
                return False
        except Exception as e:
            print(f"发送卡片消息异常: {str(e)}")
            return False
    
    def send_news_message(
        self,
        user_id: str,
        articles: List[Dict]
    ) -> bool:
        """
        发送图文消息
        
        Args:
            user_id: 用户ID
            articles: 图文消息列表 [{"title": "标题", "description": "描述", "url": "链接", "picurl": "图片链接"}]
            
        Returns:
            是否发送成功
        """
        access_token = self._get_access_token()
        url = f"{self.BASE_URL}/message/send?access_token={access_token}"
        
        data = {
            "touser": user_id,
            "msgtype": "news",
            "agentid": self.agent_id,
            "news": {
                "articles": articles
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get("errcode") == 0:
                return True
            else:
                print(f"发送图文消息失败: {result.get('errmsg')}")
                return False
        except Exception as e:
            print(f"发送图文消息异常: {str(e)}")
            return False
    
    def send_daily_report_reminder(
        self,
        user_id: str,
        user_name: str,
        report_date: str
    ) -> bool:
        """
        发送日报填写提醒
        
        Args:
            user_id: 企业微信用户ID
            user_name: 用户姓名
            report_date: 日报日期
            
        Returns:
            是否发送成功
        """
        title = "⏰ 日报填写提醒"
        description = f"""<div class=\"gray\">{datetime.now().strftime('%Y年%m月%d日')}</div>
<div class=\"normal\">您好，{user_name}！</div>
<div class=\"highlight\">请尽快填写 {report_date} 的工作日报。</div>
<div class=\"normal\">点击按钮进入系统填写日报。</div>"""
        
        return self.send_text_card(
            user_id=user_id,
            title=title,
            description=description,
            url="https://your-system-url.com/daily-report",
            btntxt="立即填写"
        )
    
    def send_evaluation_notification(
        self,
        user_id: str,
        user_name: str,
        evaluator_name: str,
        rating: str,
        comment: Optional[str] = None
    ) -> bool:
        """
        发送评价通知
        
        Args:
            user_id: 被评价人企业微信ID
            user_name: 被评价人姓名
            evaluator_name: 评价人姓名
            rating: 评价等级
            comment: 评价评语
            
        Returns:
            是否发送成功
        """
        title = "⭐ 日报评价通知"
        
        rating_text = {"A": "超目标达成", "B": "按目标达成", "C": "基本达标", "D": "需要改进"}.get(rating, "已评价")
        
        description = f"""<div class=\"gray\">{datetime.now().strftime('%Y年%m月%d日')}</div>
<div class=\"normal\">您好，{user_name}！</div>
<div class=\"highlight\">您的日报已被 {evaluator_name} 评价</div>
<div class=\"normal\">评价等级：<font color=\"info\">{rating} ({rating_text})</font></div>"""
        
        if comment:
            description += f"<div class=\"normal\">评语：{comment[:100]}</div>"
        
        return self.send_text_card(
            user_id=user_id,
            title=title,
            description=description,
            url="https://your-system-url.com/daily-report/my-reports",
            btntxt="查看详情"
        )
    
    def send_pending_evaluation_reminder(
        self,
        user_id: str,
        user_name: str,
        pending_count: int
    ) -> bool:
        """
        发送待评价提醒（给上级）
        
        Args:
            user_id: 评价人企业微信ID
            user_name: 评价人姓名
            pending_count: 待评价数量
            
        Returns:
            是否发送成功
        """
        title = "📋 待评价提醒"
        description = f"""<div class=\"gray\">{datetime.now().strftime('%Y年%m月%d日')}</div>
<div class=\"normal\">您好，{user_name}！</div>
<div class=\"highlight\">您有 <font color=\"warning\">{pending_count}</font> 份日报待评价</div>
<div class=\"normal\">请及时完成评价工作。</div>"""
        
        return self.send_text_card(
            user_id=user_id,
            title=title,
            description=description,
            url="https://your-system-url.com/daily-report/evaluation",
            btntxt="去评价"
        )


# 全局通知服务实例（需要在应用启动时初始化）
wechat_service: Optional[WeChatNotificationService] = None


def init_wechat_service(corp_id: str, corp_secret: str, agent_id: str):
    """初始化微信通知服务"""
    global wechat_service
    wechat_service = WeChatNotificationService(corp_id, corp_secret, agent_id)
    return wechat_service


def get_wechat_service() -> Optional[WeChatNotificationService]:
    """获取微信通知服务实例"""
    return wechat_service
