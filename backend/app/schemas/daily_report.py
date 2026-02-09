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
