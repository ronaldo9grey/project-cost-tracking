"""
通知服务API
提供微信消息推送、通知管理等功能
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.dependencies import get_db
from app.core.exceptions import BadRequestException
from app.services.wechat_notification import get_wechat_service, WeChatNotificationService
from app.models.resource import Personnel
from app.models.notification import Notification, NotificationSetting
from app.api.v1.auth import get_current_user
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/notifications", tags=["通知服务"])


class WeChatConfig(BaseModel):
    """企业微信配置"""
    corp_id: str
    corp_secret: str
    agent_id: str


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    user_id: str
    message_type: str = "text"  # text, textcard, news
    content: str
    title: Optional[str] = None
    url: Optional[str] = None


class NotificationSettingUpdate(BaseModel):
    """通知设置更新"""
    daily_report_reminder: bool = True
    evaluation_notification: bool = True
    pending_evaluation_reminder: bool = True
    reminder_time: str = "18:00"  # 日报提醒时间


@router.post("/wechat/init")
def init_wechat(config: WeChatConfig):
    """
    初始化企业微信通知服务
    
    需要在系统设置中配置企业微信参数后才能使用通知功能
    """
    try:
        service = WeChatNotificationService(
            corp_id=config.corp_id,
            corp_secret=config.corp_secret,
            agent_id=config.agent_id
        )
        # 测试获取token
        service._get_access_token()
        
        # 保存配置到全局
        from app.services.wechat_notification import init_wechat_service
        init_wechat_service(config.corp_id, config.corp_secret, config.agent_id)
        
        return SuccessResponse(data=None, message="企业微信通知服务初始化成功")
    except Exception as e:
        raise BadRequestException(message=f"初始化失败：{str(e)}")


@router.post("/wechat/send")
def send_wechat_message(
    request: SendMessageRequest,
    current_user: Personnel = Depends(get_current_user)
):
    """
    发送企业微信消息
    
    管理员可用于发送自定义通知
    """
    service = get_wechat_service()
    if not service:
        raise BadRequestException(message="企业微信服务未初始化")
    
    if request.message_type == "text":
        success = service.send_text_message(
            user_id=request.user_id,
            content=request.content
        )
    elif request.message_type == "textcard":
        if not request.title:
            raise BadRequestException(message="卡片消息需要标题")
        success = service.send_text_card(
            user_id=request.user_id,
            title=request.title,
            description=request.content,
            url=request.url
        )
    else:
        raise BadRequestException(message=f"不支持的消息类型: {request.message_type}")
    
    if success:
        return SuccessResponse(data=None, message="消息发送成功")
    else:
        raise BadRequestException(message="消息发送失败")


@router.get("/settings")
def get_notification_settings(
    current_user: Personnel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户通知设置
    """
    settings = db.query(NotificationSetting).filter(
        NotificationSetting.personnel_id == current_user.id
    ).first()
    
    if not settings:
        # 创建默认设置
        settings = NotificationSetting(
            personnel_id=current_user.id,
            daily_report_reminder=True,
            evaluation_notification=True,
            pending_evaluation_reminder=True,
            reminder_time="18:00"
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return SuccessResponse(
        data={
            "daily_report_reminder": settings.daily_report_reminder,
            "evaluation_notification": settings.evaluation_notification,
            "pending_evaluation_reminder": settings.pending_evaluation_reminder,
            "reminder_time": settings.reminder_time,
            "wechat_user_id": settings.wechat_user_id
        },
        message="获取通知设置成功"
    )


@router.put("/settings")
def update_notification_settings(
    request: NotificationSettingUpdate,
    current_user: Personnel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户通知设置
    """
    settings = db.query(NotificationSetting).filter(
        NotificationSetting.personnel_id == current_user.id
    ).first()
    
    if not settings:
        settings = NotificationSetting(personnel_id=current_user.id)
        db.add(settings)
    
    settings.daily_report_reminder = request.daily_report_reminder
    settings.evaluation_notification = request.evaluation_notification
    settings.pending_evaluation_reminder = request.pending_evaluation_reminder
    settings.reminder_time = request.reminder_time
    
    db.commit()
    db.refresh(settings)
    
    return SuccessResponse(data=None, message="通知设置更新成功")


@router.post("/settings/wechat-user-id")
def update_wechat_user_id(
    wechat_user_id: str,
    current_user: Personnel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户企业微信ID
    
    用于接收企业微信通知
    """
    settings = db.query(NotificationSetting).filter(
        NotificationSetting.personnel_id == current_user.id
    ).first()
    
    if not settings:
        settings = NotificationSetting(
            personnel_id=current_user.id,
            wechat_user_id=wechat_user_id
        )
        db.add(settings)
    else:
        settings.wechat_user_id = wechat_user_id
    
    db.commit()
    db.refresh(settings)
    
    return SuccessResponse(data=None, message="企业微信ID更新成功")


@router.get("/history")
def get_notification_history(
    page: int = 1,
    page_size: int = 20,
    current_user: Personnel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户通知历史
    """
    offset = (page - 1) * page_size
    
    notifications = db.query(Notification).filter(
        Notification.personnel_id == current_user.id
    ).order_by(Notification.created_at.desc()).offset(offset).limit(page_size).all()
    
    total = db.query(Notification).filter(
        Notification.personnel_id == current_user.id
    ).count()
    
    return SuccessResponse(
        data={
            "items": [
                {
                    "id": n.id,
                    "type": n.type,
                    "title": n.title,
                    "content": n.content,
                    "is_read": n.is_read,
                    "created_at": n.created_at.isoformat() if n.created_at else None
                }
                for n in notifications
            ],
            "total": total,
            "page": page,
            "page_size": page_size
        },
        message="获取通知历史成功"
    )


@router.post("/mark-read/{notification_id}")
def mark_notification_read(
    notification_id: int,
    current_user: Personnel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    标记通知为已读
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.personnel_id == current_user.id
    ).first()
    
    if not notification:
        raise BadRequestException(message="通知不存在")
    
    notification.is_read = True
    db.commit()
    
    return SuccessResponse(data=None, message="已标记为已读")


@router.post("/test/daily-report-reminder")
def test_daily_report_reminder(
    current_user: Personnel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    测试日报提醒通知
    
    发送测试消息到当前用户的企业微信
    """
    service = get_wechat_service()
    if not service:
        raise BadRequestException(message="企业微信服务未初始化")
    
    # 获取用户的企业微信ID
    settings = db.query(NotificationSetting).filter(
        NotificationSetting.personnel_id == current_user.id
    ).first()
    
    if not settings or not settings.wechat_user_id:
        raise BadRequestException(message="未绑定企业微信ID")
    
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    
    success = service.send_daily_report_reminder(
        user_id=settings.wechat_user_id,
        user_name=current_user.name,
        report_date=today
    )
    
    if success:
        return SuccessResponse(data=None, message="测试消息发送成功，请检查企业微信")
    else:
        raise BadRequestException(message="测试消息发送失败")
