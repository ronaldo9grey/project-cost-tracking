from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


# ==================== 月度目标 Schemas ====================

class MonthlyGoalBase(BaseModel):
    """月度目标基础模型"""
    month: str = Field(..., description="月份 (格式: 2026-02)", max_length=7)
    title: str = Field(..., description="目标标题", max_length=500)
    content: Optional[str] = Field(None, description="工作内容")
    status: Optional[str] = Field("draft", description="状态: draft/published/completed")
    progress_rate: Optional[Decimal] = Field(Decimal("0"), description="完成进度 0-100")


class MonthlyGoalCreate(MonthlyGoalBase):
    """创建月度目标请求模型"""
    pass


class MonthlyGoalUpdate(BaseModel):
    """更新月度目标请求模型"""
    month: Optional[str] = Field(None, description="月份 (格式: 2026-02)", max_length=7)
    title: Optional[str] = Field(None, description="目标标题", max_length=500)
    content: Optional[str] = Field(None, description="工作内容")
    status: Optional[str] = Field(None, description="状态: draft/published/completed")
    progress_rate: Optional[Decimal] = Field(None, description="完成进度 0-100")


class MonthlyGoalPublish(BaseModel):
    """发布月度目标请求模型"""
    pass


class MonthlyGoalProgressUpdate(BaseModel):
    """更新月度目标进度请求模型"""
    progress_rate: Decimal = Field(..., description="完成进度 0-100", ge=0, le=100)


class MonthlyGoalResponse(MonthlyGoalBase):
    """月度目标响应模型"""
    id: int
    user_id: str
    user_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    weekly_goal_count: Optional[int] = Field(0, description="周目标数量")
    
    class Config:
        from_attributes = True


class MonthlyGoalListResponse(BaseModel):
    """月度目标列表响应模型"""
    items: List[MonthlyGoalResponse]
    total: int
    page: int
    size: int
    total_pages: int


class MonthlyGoalDetailResponse(MonthlyGoalResponse):
    """月度目标详情响应模型（包含周目标）"""
    weekly_goals: List["WeeklyGoalResponse"] = []


# ==================== 周目标 Schemas ====================

class WeeklyGoalBase(BaseModel):
    """周目标基础模型"""
    week_number: int = Field(..., description="周次 (1-5)", ge=1, le=5)
    title: str = Field(..., description="周目标标题", max_length=500)
    content: Optional[str] = Field(None, description="工作内容")
    progress_rate: Optional[Decimal] = Field(Decimal("0"), description="完成进度 0-100")
    status: Optional[str] = Field("pending", description="状态: pending/in_progress/completed")
    start_date: Optional[date] = Field(None, description="周开始日期")
    end_date: Optional[date] = Field(None, description="周结束日期")


class WeeklyGoalCreate(WeeklyGoalBase):
    """创建周目标请求模型"""
    pass


class WeeklyGoalUpdate(BaseModel):
    """更新周目标请求模型"""
    week_number: Optional[int] = Field(None, description="周次 (1-5)", ge=1, le=5)
    title: Optional[str] = Field(None, description="周目标标题", max_length=500)
    content: Optional[str] = Field(None, description="工作内容")
    progress_rate: Optional[Decimal] = Field(None, description="完成进度 0-100")
    status: Optional[str] = Field(None, description="状态: pending/in_progress/completed")
    start_date: Optional[date] = Field(None, description="周开始日期")
    end_date: Optional[date] = Field(None, description="周结束日期")


class WeeklyGoalProgressUpdate(BaseModel):
    """更新周目标进度请求模型"""
    progress_rate: Decimal = Field(..., description="完成进度 0-100", ge=0, le=100)


class WeeklyGoalResponse(WeeklyGoalBase):
    """周目标响应模型"""
    id: int
    goal_id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True


class WeeklyGoalListResponse(BaseModel):
    """周目标列表响应模型"""
    items: List[WeeklyGoalResponse]
    total: int


class WeeklyGoalWithMonthlyInfoResponse(WeeklyGoalResponse):
    """周目标响应模型（包含月度目标信息）"""
    monthly_goal_month: Optional[str] = None
    monthly_goal_title: Optional[str] = None


class CurrentWeekGoalResponse(BaseModel):
    """当前周目标响应模型（用于日报填报）"""
    weekly_goal: Optional[WeeklyGoalResponse] = None
    month: Optional[str] = None
    month_title: Optional[str] = None
    week_number: Optional[int] = None


# ==================== 日报目标关联 Schemas ====================

class DailyReportGoalBase(BaseModel):
    """日报目标关联基础模型"""
    weekly_goal_id: int = Field(..., description="周目标ID")
    project_id: Optional[str] = Field(None, description="项目ID")
    project_name: Optional[str] = Field(None, description="项目名称")
    task_node_id: Optional[str] = Field(None, description="任务节点ID")
    task_node_name: Optional[str] = Field(None, description="任务节点名称")
    notes: Optional[str] = Field(None, description="填报说明")
    completion_rate: Optional[Decimal] = Field(Decimal("0"), description="该任务完成度")


class DailyReportGoalCreate(DailyReportGoalBase):
    """创建日报目标关联请求模型"""
    pass


class DailyReportGoalUpdate(BaseModel):
    """更新日报目标关联请求模型"""
    weekly_goal_id: Optional[int] = Field(None, description="周目标ID")
    project_id: Optional[str] = Field(None, description="项目ID")
    project_name: Optional[str] = Field(None, description="项目名称")
    task_node_id: Optional[str] = Field(None, description="任务节点ID")
    task_node_name: Optional[str] = Field(None, description="任务节点名称")
    notes: Optional[str] = Field(None, description="填报说明")
    completion_rate: Optional[Decimal] = Field(None, description="该任务完成度")


class DailyReportGoalResponse(DailyReportGoalBase):
    """日报目标关联响应模型"""
    id: int
    daily_report_id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True


class DailyReportGoalWithDetailsResponse(DailyReportGoalResponse):
    """日报目标关联响应模型（包含详细信息）"""
    weekly_goal_title: Optional[str] = None
    weekly_goal_content: Optional[str] = None
    monthly_goal_month: Optional[str] = None


class DailyReportGoalListResponse(BaseModel):
    """日报目标关联列表响应模型"""
    items: List[DailyReportGoalResponse]
    total: int


# 解决前向引用
MonthlyGoalDetailResponse.model_rebuild()
