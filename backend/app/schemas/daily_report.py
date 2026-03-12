from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class DailyWorkItemBase(BaseModel):
    work_content: str
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    task_id: Optional[str] = None
    task_name: Optional[str] = None
    key_work_tracking: Optional[str] = None
    start_time: Optional[str] = None  # 确保是字符串类型
    end_time: Optional[str] = None    # 确保是字符串类型
    hours_spent: Optional[float] = None
    progress_status: Optional[str] = "正常"
    progress_percentage: Optional[float] = 0.0
    delay_hours: Optional[float] = 0.0
    improvement_result: Optional[str] = None
    result: Optional[str] = None
    measures: Optional[str] = None
    evaluation: Optional[str] = None


class DailyWorkItemCreate(DailyWorkItemBase):
    pass


class DailyWorkItemResponse(DailyWorkItemBase):
    id: int
    report_id: int
    
    class Config:
        from_attributes = True
        
    def model_dump(self, **kwargs):
        """重写model_dump方法处理时间字段序列化"""
        # 获取原始数据
        data = super().model_dump(**kwargs)
        
        # 处理时间字段 - 兼容旧数据和datetime.time对象
        for time_field in ['start_time', 'end_time']:
            if time_field in data and data[time_field] is not None:
                # 处理任何类型的time对象
                if hasattr(data[time_field], 'strftime'):
                    # datetime.time 对象或SQLAlchemy Time对象
                    try:
                        data[time_field] = data[time_field].strftime('%H:%M')
                    except:
                        # 如果strftime失败，尝试其他方法
                        data[time_field] = str(data[time_field])
                else:
                    # 其他类型直接转换为字符串
                    data[time_field] = str(data[time_field])
        
        return data


class DailyReportBase(BaseModel):
    report_date: date
    employee_id: str
    employee_name: str
    work_target: Optional[str] = None
    key_work_tracking: Optional[str] = None
    tomorrow_plan: Optional[str] = None
    planned_hours: float = 0


class DailyReportCreate(DailyReportBase):
    pass


class DailyReportWithItemsCreate(BaseModel):
    report: DailyReportCreate
    work_items: List[DailyWorkItemCreate] = []


class DailyReportUpdate(BaseModel):
    work_target: Optional[str] = None
    key_work_tracking: Optional[str] = None
    hours_spent: Optional[float] = None
    progress_status: Optional[str] = None
    progress_percentage: Optional[float] = None
    self_evaluation: Optional[str] = None
    tomorrow_plan: Optional[str] = None
    planned_hours: Optional[float] = None
    status: Optional[str] = None


class DailyReportEvaluate(BaseModel):
    supervisor_score: int = Field(..., ge=0, le=100)
    supervisor_comment: Optional[str] = None


class DailyReportResponse(DailyReportBase):
    id: int
    status: str
    submitted_at: Optional[datetime] = None
    create_time: datetime
    update_time: datetime
    report_mode: str = "free"  # 日报模式: free/goal
    linked_monthly_goal_id: Optional[int] = None
    linked_weekly_goal_id: Optional[int] = None
    work_items: List[DailyWorkItemResponse] = []
    
    class Config:
        from_attributes = True


class DailyReportListResponse(BaseModel):
    items: List[DailyReportResponse]
    total: int
    page: int
    size: int
    total_pages: int


# 优化后的简化列表项响应模型
class DailyReportListItem(BaseModel):
    id: int
    report_date: date
    employee_id: str
    employee_name: str
    work_target: Optional[str] = None
    tomorrow_plan: Optional[str] = None
    planned_hours: float = 0
    actual_hours: float = 0  # 实际工时（从daily_work_items计算）
    status: str
    submitted_at: Optional[datetime] = None
    create_time: datetime
    update_time: datetime


class DailyReportListResponseOptimized(BaseModel):
    items: List[DailyReportListItem]
    total: int
    page: int
    size: int
    total_pages: int


class DailyWorkLogCreate(BaseModel):
    project_id: str
    project_name: str
    task_id: Optional[str] = None
    task_name: Optional[str] = None
    work_date: date
    work_content: Optional[str] = None
    hours: float = Field(..., ge=0)


class DailyWorkLogResponse(BaseModel):
    id: int
    report_id: Optional[int] = None
    project_id: str
    project_name: str
    task_id: Optional[str] = None
    task_name: Optional[str] = None
    employee_id: str
    employee_name: str
    work_date: date
    work_content: Optional[str] = None
    hours: float
    status: str
    create_time: datetime
    
    class Config:
        from_attributes = True


class MyTaskResponse(BaseModel):
    task_id: str
    task_name: str
    project_id: str
    project_name: str
    assignee: Optional[str] = None
    assignee_id: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str
    progress: float
    resource_allocation: Optional[str] = None


# ==================== 简版日报（关联目标模式）Schemas ====================

class GoalLinkedWorkItemCreate(BaseModel):
    """简版日报工作事项创建模型"""
    work_content: str  # 主要工作事项（预填周目标内容，可编辑）
    project_id: Optional[str] = None  # 关联项目ID（必填）
    project_name: Optional[str] = None  # 关联项目名称
    task_id: Optional[str] = None  # 关联任务ID
    task_name: Optional[str] = None  # 关联任务名称
    start_time: Optional[str] = "08:15"  # 默认开始时间
    end_time: Optional[str] = "18:00"  # 默认结束时间
    hours_spent: Optional[float] = 0  # 工时（根据时间自动计算）
    result: Optional[str] = None  # 执行结果
    evaluation: Optional[str] = None  # 自我评价


class GoalLinkedDailyReportCreate(BaseModel):
    """简版日报（关联目标模式）创建请求模型"""
    report_date: date  # 日报日期
    tomorrow_plan: str = "继续推进本周目标"  # 明日计划（默认文案）
    planned_hours: float = 0  # 计划工时
    # 关联目标信息
    linked_monthly_goal_id: int  # 关联的月度目标ID
    linked_weekly_goal_id: int  # 关联的周目标ID
    # 工作事项列表
    work_items: List[GoalLinkedWorkItemCreate] = []


class CurrentWeekGoalResponse(BaseModel):
    """本周目标响应模型（用于简版日报预填）"""
    weekly_goal_id: int
    weekly_goal_title: str
    weekly_goal_content: Optional[str] = None
    monthly_goal_id: int  # 月度目标ID
    month: str  # 月份，如 "2026-03"
    month_title: str  # 月度目标标题
    week_number: int  # 周次 1-5
    start_date: Optional[date] = None  # 周开始日期
    end_date: Optional[date] = None  # 周结束日期


class GoalLinkedReportResponse(DailyReportResponse):
    """简版日报响应模型"""
    linked_monthly_goal_id: Optional[int] = None
    linked_weekly_goal_id: Optional[int] = None
    weekly_goal_title: Optional[str] = None  # 周目标标题（用于展示）
