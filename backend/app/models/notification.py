"""
通知相关模型
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Notification(Base):
    """通知记录表"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey("personnel.id"), nullable=False, comment="接收人ID")
    type = Column(String(50), nullable=False, comment="通知类型: daily_report, evaluation, system")
    title = Column(String(200), nullable=False, comment="通知标题")
    content = Column(Text, comment="通知内容")
    is_read = Column(Boolean, default=False, comment="是否已读")
    wechat_msg_id = Column(String(100), comment="企业微信消息ID")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    read_at = Column(DateTime, comment="阅读时间")


class NotificationSetting(Base):
    """用户通知设置表"""
    __tablename__ = "notification_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey("personnel.id"), unique=True, nullable=False, comment="人员ID")
    
    # 企业微信配置
    wechat_user_id = Column(String(100), comment="企业微信用户ID")
    
    # 小程序配置
    mini_program_openid = Column(String(100), comment="小程序openid")
    
    # 微信公众号配置
    wechat_official_openid = Column(String(100), comment="微信公众号openid")
    
    # 通知开关
    daily_report_reminder = Column(Boolean, default=True, comment="日报填写提醒")
    evaluation_notification = Column(Boolean, default=True, comment="评价通知")
    pending_evaluation_reminder = Column(Boolean, default=True, comment="待评价提醒")
    
    # 提醒时间设置
    reminder_time = Column(String(10), default="18:00", comment="日报提醒时间")
    
    # 其他设置
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
