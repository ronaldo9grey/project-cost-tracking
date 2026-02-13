from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class WorkItemResponse(BaseModel):
    """工作项目响应"""
    work_content: str = Field(..., description="工作内容")
    start_time: str = Field(..., description="开始时间")
    end_time: str = Field(..., description="结束时间")
    result: str = Field(..., description="工作结果")
    evaluation: str = Field(default="", description="工作评价")
    
    class Config:
        from_attributes = True


class EvaluationResponse(BaseModel):
    """评价响应"""
    supervisor_score: int = Field(..., description="评分")
    supervisor_comment: str = Field(default="", description="评价内容")
    supervisor_id: str = Field(..., description="评价人ID")
    supervisor_name: str = Field(..., description="评价人姓名")
    evaluated_at: datetime = Field(..., description="评价时间")
    
    @validator('supervisor_score', pre=True, always=True)
    def convert_score_to_abc(cls, v):
        """将整数转换为ABCDE字符串"""
        if isinstance(v, str):
            return v
        # 转换整数到ABCDE
        int_to_abc = {
            5: 'A',  # 超目标达成
            4: 'B',  # 按目标达成  
            3: 'C',  # 达成目标80%
            2: 'D',  # 达成目标50%-80%
            1: 'E'   # 小于目标50%
        }
        return int_to_abc.get(v, 'E')
    
    class Config:
        from_attributes = True


class SubordinateReportResponse(BaseModel):
    """管辖员工日报响应"""
    id: int = Field(..., description="日报ID")
    report_date: str = Field(..., description="日报日期")
    employee_id: str = Field(..., description="员工ID")
    employee_name: str = Field(..., description="员工姓名")
    department: Optional[str] = Field(default="", description="部门")
    position: Optional[str] = Field(default="", description="职位")
    tomorrow_plan: Optional[str] = Field(default="", description="明日计划")
    planned_hours: float = Field(default=0.0, description="计划工时")
    work_items: List[WorkItemResponse] = Field(default_factory=list, description="工作项目")
    evaluation: Optional[EvaluationResponse] = Field(default=None, description="评价信息")
    
    class Config:
        from_attributes = True


class EvaluationStatsResponse(BaseModel):
    """评价统计数据响应"""
    pending: int = Field(..., description="待评价数量")
    evaluated: int = Field(..., description="已评价数量")
    progress: float = Field(..., description="评价进度(%)")
    
    class Config:
        from_attributes = True


class CreateEvaluationRequest(BaseModel):
    """创建评价请求"""
    report_id: int = Field(..., description="日报ID")
    supervisor_score: str = Field(..., description="评分(A-E等级)")
    supervisor_comment: Optional[str] = Field(default="", description="评价内容")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": 123,
                "supervisor_score": "B",
                "supervisor_comment": "工作认真负责，建议继续保持"
            }
        }
    
    @validator('supervisor_score')
    def convert_score_to_int(cls, v):
        """将ABCDE字符串转换为整数"""
        score_mapping = {
            'A': 5,  # 超目标达成
            'B': 4,  # 按目标达成  
            'C': 3,  # 达成目标80%
            'D': 2,  # 达成目标50%-80%
            'E': 1   # 小于目标50%
        }
        if v not in score_mapping:
            raise ValueError(f"无效的评分等级: {v}，必须是 A, B, C, D, E 之一")
        return score_mapping[v]


class UpdateEvaluationRequest(BaseModel):
    """更新评价请求"""
    supervisor_score: Optional[str] = Field(None, description="评分(A-E等级)")
    supervisor_comment: Optional[str] = Field(None, description="评价内容")
    
    class Config:
        json_schema_extra = {
            "example": {
                "supervisor_score": "A",
                "supervisor_comment": "工作表现出色，给予优秀评价"
            }
        }
    
    @validator('supervisor_score')
    def convert_score_to_int(cls, v):
        """将ABCDE字符串转换为整数"""
        if v is None:
            return v
        score_mapping = {
            'A': 5,  # 超目标达成
            'B': 4,  # 按目标达成  
            'C': 3,  # 达成目标80%
            'D': 2,  # 达成目标50%-80%
            'E': 1   # 小于目标50%
        }
        if v not in score_mapping:
            raise ValueError(f"无效的评分等级: {v}，必须是 A, B, C, D, E 之一")
        return score_mapping[v]


class EvaluationHistoryResponse(BaseModel):
    """评价历史响应"""
    items: List[EvaluationResponse] = Field(default_factory=list, description="评价记录列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")
    
    class Config:
        from_attributes = True