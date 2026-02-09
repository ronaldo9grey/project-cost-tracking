from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime, time


class DailyWorkItemBase(BaseModel):
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    task_id: Optional[str] = None
    task_name: Optional[str] = None
    hours_spent: float = Field(default=0.0, ge=0)
    progress_status: Optional[str] = "正常"
    progress_percentage: float = Field(default=0.0, ge=0, le=100)
    delay_hours: float = Field(default=0.0, ge=0)
    improvement_result: Optional[str] = None
    key_work_tracking: Optional[str] = None
    work_content: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    result: Optional[str] = None
    measures: Optional[str] = None
    evaluation: Optional[str] = None


class DailyWorkItemCreate(DailyWorkItemBase):
    report_id: int


class DailyWorkItemUpdate(BaseModel):
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    task_id: Optional[str] = None
    task_name: Optional[str] = None
    hours_spent: Optional[float] = Field(default=None, ge=0)
    progress_status: Optional[str] = None
    progress_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    delay_hours: Optional[float] = Field(default=None, ge=0)
    improvement_result: Optional[str] = None
    key_work_tracking: Optional[str] = None
    work_content: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    result: Optional[str] = None
    measures: Optional[str] = None
    evaluation: Optional[str] = None
    is_deleted: Optional[bool] = None


class DailyWorkItemResponse(DailyWorkItemBase):
    id: int
    report_id: int
    create_time: datetime
    update_time: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True


class DailyReportEvaluationBase(BaseModel):
    supervisor_score: int = Field(default=0, ge=0, le=100)
    supervisor_comment: Optional[str] = None
    supervisor_id: Optional[str] = None
    supervisor_name: Optional[str] = None


class DailyReportEvaluationCreate(DailyReportEvaluationBase):
    report_id: int


class DailyReportEvaluationUpdate(BaseModel):
    supervisor_score: Optional[int] = Field(default=None, ge=0, le=100)
    supervisor_comment: Optional[str] = None
    supervisor_id: Optional[str] = None
    supervisor_name: Optional[str] = None
    is_deleted: Optional[bool] = None


class DailyReportEvaluationResponse(DailyReportEvaluationBase):
    id: int
    report_id: int
    evaluated_at: Optional[datetime] = None
    create_time: datetime
    update_time: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True


class RefactoredDailyReportCreate(BaseModel):
    report_date: date
    work_target: Optional[str] = None
    key_work_tracking: Optional[str] = None
    tomorrow_plan: Optional[str] = None
    planned_hours: Optional[float] = Field(default=0, ge=0)
    work_items: List[DailyWorkItemBase]


class RefactoredDailyReportUpdate(BaseModel):
    work_target: Optional[str] = None
    key_work_tracking: Optional[str] = None
    tomorrow_plan: Optional[str] = None
    planned_hours: Optional[float] = Field(default=None, ge=0)
    work_items: Optional[List[DailyWorkItemBase]] = None


class RefactoredDailyReportResponse(BaseModel):
    id: int
    report_date: date
    employee_id: str
    employee_name: str
    work_target: Optional[str] = None
    key_work_tracking: Optional[str] = None
    tomorrow_plan: Optional[str] = None
    planned_hours: float
    status: str
    submitted_at: Optional[datetime] = None
    self_evaluation: Optional[str] = None
    create_time: datetime
    update_time: datetime
    work_items: List[DailyWorkItemResponse]
    evaluations: List[DailyReportEvaluationResponse]
    
    class Config:
        from_attributes = True


class DailyReportListResponse(BaseModel):
    items: List[RefactoredDailyReportResponse]
    total: int
    page: int
    size: int
    total_pages: int