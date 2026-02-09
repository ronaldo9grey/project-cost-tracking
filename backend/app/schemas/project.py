from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


# 项目基础模型
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="项目名称")
    describe: Optional[str] = Field(None, description="项目描述")
    leader: str = Field(..., min_length=1, max_length=100, description="项目负责人")
    leader_id: Optional[int] = Field(None, description="负责人ID")
    status: str = Field(..., min_length=1, max_length=50, description="项目状态")
    start_date: Optional[date] = Field(None, description="项目开始日期")
    end_date: Optional[date] = Field(None, description="项目结束日期")


# 创建项目请求模型
class ProjectCreate(ProjectBase):
    contract_date: Optional[date] = Field(None, description="合同日期")
    contract_no: Optional[str] = Field(None, max_length=100, description="合同编号")
    tax_rate: Optional[float] = Field(0.13, ge=0, description="税率")
    contract_amount: Optional[float] = Field(0.0, ge=0, description="合同金额")
    revenue: Optional[float] = Field(0.0, ge=0, description="收入")
    target_profit: Optional[float] = Field(0.0, ge=0, description="目标利润")
    actual_profit: Optional[float] = Field(0.0, ge=0, description="实际利润")
    created_by_id: Optional[int] = Field(None, description="创建人ID")
    # 成本相关
    budget_total_cost: Optional[float] = Field(0.0, ge=0, description="预算总成本")
    actual_total_cost: Optional[float] = Field(0.0, ge=0, description="实际总成本")
    material_budget: Optional[float] = Field(0.0, ge=0, description="物料预算")
    material_actual: Optional[float] = Field(0.0, ge=0, description="实际物料成本")
    outsourcing_budget: Optional[float] = Field(0.0, ge=0, description="外包预算")
    outsourcing_actual: Optional[float] = Field(0.0, ge=0, description="实际外包成本")
    indirect_budget: Optional[float] = Field(0.0, ge=0, description="间接预算")
    indirect_actual: Optional[float] = Field(0.0, ge=0, description="实际间接成本")
    labor_budget: Optional[float] = Field(0.0, ge=0, description="人力预算")
    labor_actual: Optional[float] = Field(0.0, ge=0, description="实际人力成本")


# 更新项目请求模型
class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="项目名称")
    leader: Optional[str] = Field(None, min_length=1, max_length=100, description="项目负责人")
    leader_id: Optional[int] = Field(None, description="负责人ID")
    status: Optional[str] = Field(None, min_length=1, max_length=50, description="项目状态")
    progress: Optional[int] = Field(None, ge=0, le=100, description="项目进度")
    start_date: Optional[date] = Field(None, description="项目开始日期")
    end_date: Optional[date] = Field(None, description="项目结束日期")
    contract_date: Optional[date] = Field(None, description="合同日期")
    contract_no: Optional[str] = Field(None, max_length=100, description="合同编号")
    tax_rate: Optional[float] = Field(None, ge=0, description="税率")
    contract_amount: Optional[float] = Field(None, ge=0, description="合同金额")
    revenue: Optional[float] = Field(None, ge=0, description="收入")
    target_profit: Optional[float] = Field(None, ge=0, description="目标利润")
    actual_profit: Optional[float] = Field(None, ge=0, description="实际利润")
    # 成本相关
    budget_total_cost: Optional[float] = Field(None, ge=0, description="预算总成本")
    actual_total_cost: Optional[float] = Field(None, ge=0, description="实际总成本")
    material_budget: Optional[float] = Field(None, ge=0, description="物料预算")
    material_actual: Optional[float] = Field(None, ge=0, description="实际物料成本")
    outsourcing_budget: Optional[float] = Field(None, ge=0, description="外包预算")
    outsourcing_actual: Optional[float] = Field(None, ge=0, description="实际外包成本")
    indirect_budget: Optional[float] = Field(None, ge=0, description="间接预算")
    indirect_actual: Optional[float] = Field(None, ge=0, description="实际间接成本")
    labor_budget: Optional[float] = Field(None, ge=0, description="人力预算")
    labor_actual: Optional[float] = Field(None, ge=0, description="实际人力成本")


# 项目响应模型
class ProjectResponse(ProjectBase):
    id: int = Field(..., description="项目ID")
    progress: int = Field(..., ge=0, le=100, description="项目进度")
    contract_date: Optional[date] = Field(None, description="合同日期")
    contract_no: Optional[str] = Field(None, description="合同编号")
    tax_rate: float = Field(..., ge=0, description="税率")
    contract_amount: float = Field(..., ge=0, description="合同金额")
    revenue: float = Field(..., ge=0, description="收入")
    target_profit: float = Field(..., ge=0, description="目标利润")
    actual_profit: float = Field(..., ge=0, description="实际利润")
    created_by_id: Optional[int] = Field(None, description="创建人ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    is_deleted: bool = Field(..., description="是否删除")
    # 成本相关
    budget_total_cost: float = Field(..., ge=0, description="预算总成本")
    actual_total_cost: float = Field(..., ge=0, description="实际总成本")
    material_budget: float = Field(..., ge=0, description="物料预算")
    material_actual: float = Field(..., ge=0, description="实际物料成本")
    outsourcing_budget: float = Field(..., ge=0, description="外包预算")
    outsourcing_actual: float = Field(..., ge=0, description="实际外包成本")
    indirect_budget: float = Field(..., ge=0, description="间接预算")
    indirect_actual: float = Field(..., ge=0, description="实际间接成本")
    labor_budget: float = Field(..., ge=0, description="人力预算")
    labor_actual: float = Field(..., ge=0, description="实际人力成本")
    
    class Config:
        from_attributes = True


# 任务基础模型
class TaskBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="任务名称")
    description: Optional[str] = Field(None, max_length=500, description="任务描述")
    start_date: date = Field(..., description="任务开始日期")
    end_date: date = Field(..., description="任务结束日期")
    status: str = Field(..., min_length=1, max_length=20, description="任务状态")
    progress: float = Field(..., ge=0, le=100, description="任务进度")
    assigned_to: Optional[str] = Field(None, max_length=50, description="任务负责人")


# 创建任务请求模型
class TaskCreate(TaskBase):
    pass


# 更新任务请求模型
class TaskUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="任务名称")
    description: Optional[str] = Field(None, max_length=500, description="任务描述")
    start_date: Optional[date] = Field(None, description="任务开始日期")
    end_date: Optional[date] = Field(None, description="任务结束日期")
    status: Optional[str] = Field(None, min_length=1, max_length=20, description="任务状态")
    progress: Optional[float] = Field(None, ge=0, le=100, description="任务进度")
    assigned_to: Optional[str] = Field(None, max_length=50, description="任务负责人")


# 任务响应模型
class TaskResponse(TaskBase):
    id: int = Field(..., description="任务ID")
    project_id: int = Field(..., description="项目ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True



