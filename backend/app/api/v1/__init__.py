"""
API V1 模块初始化
"""
from .auth import router as auth
from .projects import router as projects
from .cost import router as cost
from .supplier import router as supplier
from .resource import router as resource
from .daily_report import router as daily_report
from .ai_chat import router as ai_chat
from .daily_report_analysis import router as daily_report_analysis
from .project_tracking import router as project_tracking
from .daily_report_evaluation import router as daily_report_evaluation
from .ai_daily_report import router as ai_daily_report
from .notification import router as notification
from .wechat_official import router as wechat_official

__all__ = [
    'auth',
    'projects',
    'cost',
    'supplier',
    'resource',
    'daily_report',
    'ai_chat',
    'daily_report_analysis',
    'project_tracking',
    'daily_report_evaluation',
    'ai_daily_report',
    'notification',
    'wechat_official'
]