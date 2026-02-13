from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import time


class DailyTaskCompletionBase(BaseModel):
    """日清表基础Schema"""
    
    # === 第一部分：关联任务信息 ===
    project_id: Optional[str] = Field(None, description="项目ID")
    project_name: Optional[str] = Field(None, description="项目名称")
    task_id: Optional[str] = Field(None, description="任务ID")
    task_name: Optional[str] = Field(None, description="任务名称")
    task_source: str = Field("custom", description="任务来源：my_tasks-我的任务, custom-自定义")
    
    # === 第二部分：工作内容 ===
    start_time: Optional[time] = Field(None, description="开始时间")
    end_time: Optional[time] = Field(None, description="结束时间")
    hours_spent: float = Field(0.0, description="实际耗时")
    planned_hours: float = Field(0.0, description="计划耗时")
    
    # 进度相关
    progress_status: str = Field("正常", description="进度状态：正常/延期/提前")
    progress_percentage: float = Field(0.0, description="完成百分比")
    delay_hours: float = Field(0.0, description="延期小时数")
    
    # 工作内容
    work_content: Optional[str] = Field(None, description="具体工作内容")
    key_work_tracking: Optional[str] = Field(None, description="重点工作跟踪")
    result: Optional[str] = Field(None, description="工作结果")
    measures: Optional[str] = Field(None, description="改进措施")
    
    # 评价相关
    self_evaluation: Optional[str] = Field(None, description="自评：A/B/C/D")
    supervisor_evaluation: Optional[str] = Field(None, description="主管评价：A/B/C/D")
    evaluation_comment: Optional[str] = Field(None, description="评价说明")
    
    # 明天计划
    tomorrow_plan: Optional[str] = Field(None, description="明天工作计划")
    
    # 状态
    status: str = Field("进行中", description="任务状态：进行中/已完成/暂停/取消")
    is_key_work: bool = Field(False, description="是否重点工作")


class DailyTaskCompletionCreate(DailyTaskCompletionBase):
    """创建日清表Schema"""
    report_id: int = Field(..., description="日报ID")


class DailyTaskCompletionUpdate(BaseModel):
    """更新日清表Schema"""
    
    # === 第一部分：关联任务信息 ===
    project_id: Optional[str] = Field(None, description="项目ID")
    project_name: Optional[str] = Field(None, description="项目名称")
    task_id: Optional[str] = Field(None, description="任务ID")
    task_name: Optional[str] = Field(None, description="任务名称")
    task_source: Optional[str] = Field(None, description="任务来源")
    
    # === 第二部分：工作内容 ===
    start_time: Optional[time] = Field(None, description="开始时间")
    end_time: Optional[time] = Field(None, description="结束时间")
    hours_spent: Optional[float] = Field(None, description="实际耗时")
    planned_hours: Optional[float] = Field(None, description="计划耗时")
    
    # 进度相关
    progress_status: Optional[str] = Field(None, description="进度状态")
    progress_percentage: Optional[float] = Field(None, description="完成百分比")
    delay_hours: Optional[float] = Field(None, description="延期小时数")
    
    # 工作内容
    work_content: Optional[str] = Field(None, description="具体工作内容")
    key_work_tracking: Optional[str] = Field(None, description="重点工作跟踪")
    result: Optional[str] = Field(None, description="工作结果")
    measures: Optional[str] = Field(None, description="改进措施")
    
    # 评价相关
    self_evaluation: Optional[str] = Field(None, description="自评")
    supervisor_evaluation: Optional[str] = Field(None, description="主管评价")
    evaluation_comment: Optional[str] = Field(None, description="评价说明")
    
    # 明天计划
    tomorrow_plan: Optional[str] = Field(None, description="明天工作计划")
    
    # 状态
    status: Optional[str] = Field(None, description="任务状态")
    is_key_work: Optional[bool] = Field(None, description="是否重点工作")


class DailyTaskCompletionResponse(BaseModel):
    """日清表响应Schema"""
    id: int
    report_id: int
    
    # === 第一部分：关联任务信息 ===
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    task_id: Optional[str] = None
    task_name: Optional[str] = None
    task_source: str = "custom"
    
    # === 第二部分：工作内容 ===
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    hours_spent: float = 0.0
    planned_hours: float = 0.0
    
    # 进度相关
    progress_status: str = "正常"
    progress_percentage: float = 0.0
    delay_hours: float = 0.0
    
    # 工作内容
    work_content: Optional[str] = None
    key_work_tracking: Optional[str] = None
    result: Optional[str] = None
    measures: Optional[str] = None
    
    # 评价相关
    self_evaluation: Optional[str] = None
    supervisor_evaluation: Optional[str] = None
    evaluation_comment: Optional[str] = None
    
    # 明天计划
    tomorrow_plan: Optional[str] = None
    
    # 状态
    status: str = "进行中"
    is_key_work: bool = False
    
    # 时间戳
    create_time: str
    update_time: str
    is_deleted: bool = False
    
    class Config:
        from_attributes = True


class DailyTaskCompletionListResponse(BaseModel):
    """日清表列表响应Schema"""
    items: List[DailyTaskCompletionResponse]
    total: int
    page: int
    size: int
    total_pages: int