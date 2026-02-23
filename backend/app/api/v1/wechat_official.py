"""
微信公众号API
"""

from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.dependencies import get_db
from app.core.exceptions import BadRequestException, NotFoundException
from app.services.wechat_official import (
    WeChatOfficialService,
    wechat_official_service,
    init_wechat_official_service,
    get_wechat_official_service
)
from app.models.resource import Personnel
from app.models.notification import NotificationSetting
from app.api.v1.auth import get_current_user
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/wechat-official", tags=["微信公众号"])


class WeChatOfficialConfig(BaseModel):
    """公众号配置"""
    app_id: str
    app_secret: str


class WeChatAuthCallback(BaseModel):
    """微信授权回调"""
    code: str
    state: Optional[str] = ""


class WeChatTemplateRequest(BaseModel):
    """发送模板消息请求"""
    openid: str
    template_type: str  # daily_report_reminder, evaluation_notification, pending_evaluation
    data: dict


@router.post("/init")
def init_service(config: WeChatOfficialConfig):
    """
    初始化公众号服务
    """
    try:
        service = WeChatOfficialService(
            app_id=config.app_id,
            app_secret=config.app_secret
        )
        # 测试获取token
        service._get_base_access_token()
        
        # 保存配置到全局
        init_wechat_official_service(config.app_id, config.app_secret)
        
        return SuccessResponse(data=None, message="公众号服务初始化成功")
    except Exception as e:
        raise BadRequestException(message=f"初始化失败：{str(e)}")


@router.get("/auth-url")
def get_auth_url(redirect_uri: str, scope: str = "snsapi_base", state: str = ""):
    """
    获取微信授权URL
    
    前端调用此接口获取授权URL，然后跳转
    """
    service = get_wechat_official_service()
    if not service:
        raise BadRequestException(message="公众号服务未初始化")
    
    auth_url = service.get_auth_url(redirect_uri, scope, state)
    
    return SuccessResponse(
        data={"auth_url": auth_url},
        message="获取成功"
    )


@router.post("/auth/callback")
def wechat_auth_callback(
    callback: WeChatAuthCallback,
    db: Session = Depends(get_db)
):
    """
    微信授权回调处理
    
    用户授权后，微信会重定向到callback页面，前端将code传给此接口
    """
    service = get_wechat_official_service()
    if not service:
        raise BadRequestException(message="公众号服务未初始化")
    
    try:
        # 通过code获取openid和access_token
        access_token, openid = service.get_access_token_by_code(callback.code)
        
        # 获取用户信息（如果是snsapi_userinfo授权）
        try:
            user_info = service.get_user_info(access_token, openid)
            nickname = user_info.get('nickname', '')
            headimgurl = user_info.get('headimgurl', '')
        except:
            nickname = ''
            headimgurl = ''
        
        # 查找或创建用户
        # 这里简化处理，实际应该根据业务逻辑关联用户
        # 可以通过手机号绑定、或者让用户登录后绑定openid
        
        # 保存openid到通知设置
        # 注意：这里需要先有用户登录，才能把openid绑定到该用户
        # 更好的做法是先登录，再引导用户微信授权绑定
        
        return SuccessResponse(
            data={
                "openid": openid,
                "nickname": nickname,
                "headimgurl": headimgurl
            },
            message="微信授权成功"
        )
    except Exception as e:
        raise BadRequestException(message=f"授权处理失败：{str(e)}")


@router.post("/bind-openid")
def bind_wechat_openid(
    openid: str,
    current_user: Personnel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    绑定微信openid到当前用户
    
    用户先登录系统，然后微信授权，最后绑定openid
    """
    settings = db.query(NotificationSetting).filter(
        NotificationSetting.personnel_id == current_user.id
    ).first()
    
    if not settings:
        settings = NotificationSetting(
            personnel_id=current_user.id,
            wechat_official_openid=openid
        )
        db.add(settings)
    else:
        settings.wechat_official_openid = openid
    
    db.commit()
    db.refresh(settings)
    
    return SuccessResponse(data=None, message="微信绑定成功")


@router.get("/jsapi-config")
def get_jsapi_config(url: str):
    """
    获取JS-SDK配置
    
    前端调用微信JS-SDK（分享、拍照等）前需要获取配置
    """
    service = get_wechat_official_service()
    if not service:
        raise BadRequestException(message="公众号服务未初始化")
    
    config = service.get_jsapi_config(url)
    
    return SuccessResponse(data=config, message="获取成功")


@router.post("/send-template-message")
def send_template_message(
    request: WeChatTemplateRequest,
    current_user: Personnel = Depends(get_current_user)
):
    """
    发送模板消息（管理员或系统调用）
    """
    service = get_wechat_official_service()
    if not service:
        raise BadRequestException(message="公众号服务未初始化")
    
    from app.core.config import settings
    domain = getattr(settings, 'DOMAIN', 'https://your-domain.com')
    
    template = service.TEMPLATES.get(request.template_type)
    if not template:
        raise BadRequestException(message=f"未知的消息类型: {request.template_type}")
    
    success = service.send_template_message(
        openid=request.openid,
        template_id=template['id'],
        url=f"{domain}{template['url']}",
        data=request.data
    )
    
    if success:
        return SuccessResponse(data=None, message="消息发送成功")
    else:
        raise BadRequestException(message="消息发送失败")


@router.post("/test/daily-report-reminder")
def test_daily_report_reminder(
    current_user: Personnel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    测试日报提醒（发送给当前用户）
    """
    service = get_wechat_official_service()
    if not service:
        raise BadRequestException(message="公众号服务未初始化")
    
    # 获取用户的openid
    settings = db.query(NotificationSetting).filter(
        NotificationSetting.personnel_id == current_user.id
    ).first()
    
    if not settings or not settings.wechat_official_openid:
        raise BadRequestException(message="未绑定微信公众号，请先绑定")
    
    from app.core.config import settings as app_settings
    from datetime import datetime
    
    domain = getattr(app_settings, 'DOMAIN', 'https://your-domain.com')
    today = datetime.now().strftime('%Y-%m-%d')
    
    success = service.send_daily_report_reminder(
        openid=settings.wechat_official_openid,
        user_name=current_user.name,
        report_date=today,
        domain=domain
    )
    
    if success:
        return SuccessResponse(data=None, message="测试消息发送成功，请检查微信公众号")
    else:
        raise BadRequestException(message="发送失败，请检查模板配置")


@router.post("/test/evaluation-notification")
def test_evaluation_notification(
    current_user: Personnel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    测试评价通知（发送给当前用户）
    """
    service = get_wechat_official_service()
    if not service:
        raise BadRequestException(message="公众号服务未初始化")
    
    settings = db.query(NotificationSetting).filter(
        NotificationSetting.personnel_id == current_user.id
    ).first()
    
    if not settings or not settings.wechat_official_openid:
        raise BadRequestException(message="未绑定微信公众号")
    
    from app.core.config import settings as app_settings
    from datetime import datetime
    
    domain = getattr(app_settings, 'DOMAIN', 'https://your-domain.com')
    today = datetime.now().strftime('%Y-%m-%d')
    
    success = service.send_evaluation_notification(
        openid=settings.wechat_official_openid,
        user_name=current_user.name,
        evaluator_name="测试评价人",
        rating="B",
        evaluation_date=today,
        domain=domain
    )
    
    if success:
        return SuccessResponse(data=None, message="测试评价通知发送成功")
    else:
        raise BadRequestException(message="发送失败")
