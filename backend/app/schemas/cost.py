from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


# 物料成本相关模型
class MaterialCostBase(BaseModel):
    material_name: str = Field(..., min_length=1, max_length=100, description="物料名称")
    unit: str = Field(..., min_length=1, max_length=20, description="计量单位")
    quantity: float = Field(..., ge=0, description="预算数量")
    unit_price: float = Field(..., ge=0, description="预算单价")
    actual_quantity: float = Field(..., ge=0, description="实际数量")
    actual_unit_price: float = Field(..., ge=0, description="实际单价")
    cost_date: date = Field(..., description="成本日期")
    description: Optional[str] = Field(None, max_length=500, description="成本描述")


class MaterialCostCreate(MaterialCostBase):
    project_id: int = Field(..., ge=1, description="项目ID")


class MaterialCostUpdate(BaseModel):
    material_name: Optional[str] = Field(None, min_length=1, max_length=100, description="物料名称")
    unit: Optional[str] = Field(None, min_length=1, max_length=20, description="计量单位")
    quantity: Optional[float] = Field(None, ge=0, description="预算数量")
    unit_price: Optional[float] = Field(None, ge=0, description="预算单价")
    actual_quantity: Optional[float] = Field(None, ge=0, description="实际数量")
    actual_unit_price: Optional[float] = Field(None, ge=0, description="实际单价")
    cost_date: Optional[date] = Field(None, description="成本日期")
    description: Optional[str] = Field(None, max_length=500, description="成本描述")


class MaterialCostResponse(MaterialCostBase):
    id: int = Field(..., description="成本ID")
    project_id: int = Field(..., description="项目ID")
    total_cost: float = Field(..., ge=0, description="预算总成本")
    actual_total_cost: float = Field(..., ge=0, description="实际总成本")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


# 人力成本相关模型
class LaborCostBase(BaseModel):
    personnel_name: str = Field(..., min_length=1, max_length=50, description="人员姓名")
    role: str = Field(..., min_length=1, max_length=50, description="人员角色")
    hours: float = Field(..., ge=0, description="预算工时")
    rate_per_hour: float = Field(..., ge=0, description="预算小时费率")
    actual_hours: float = Field(..., ge=0, description="实际工时")
    actual_rate_per_hour: float = Field(..., ge=0, description="实际小时费率")
    cost_date: date = Field(..., description="成本日期")
    description: Optional[str] = Field(None, max_length=500, description="成本描述")


class LaborCostCreate(LaborCostBase):
    project_id: int = Field(..., ge=1, description="项目ID")


class LaborCostUpdate(BaseModel):
    personnel_name: Optional[str] = Field(None, min_length=1, max_length=50, description="人员姓名")
    role: Optional[str] = Field(None, min_length=1, max_length=50, description="人员角色")
    hours: Optional[float] = Field(None, ge=0, description="预算工时")
    rate_per_hour: Optional[float] = Field(None, ge=0, description="预算小时费率")
    actual_hours: Optional[float] = Field(None, ge=0, description="实际工时")
    actual_rate_per_hour: Optional[float] = Field(None, ge=0, description="实际小时费率")
    cost_date: Optional[date] = Field(None, description="成本日期")
    description: Optional[str] = Field(None, max_length=500, description="成本描述")


class LaborCostResponse(LaborCostBase):
    id: int = Field(..., description="成本ID")
    project_id: int = Field(..., description="项目ID")
    total_cost: float = Field(..., ge=0, description="预算总成本")
    actual_total_cost: float = Field(..., ge=0, description="实际总成本")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


# 外包成本相关模型
class OutsourcingCostBase(BaseModel):
    supplier_id: int = Field(..., ge=1, description="供应商ID")
    service_type: str = Field(..., min_length=1, max_length=50, description="服务类型")
    description: Optional[str] = Field(None, max_length=500, description="成本描述")
    budget_amount: float = Field(..., ge=0, description="预算金额")
    actual_amount: float = Field(..., ge=0, description="实际金额")
    cost_date: date = Field(..., description="成本日期")


class OutsourcingCostCreate(OutsourcingCostBase):
    project_id: int = Field(..., ge=1, description="项目ID")


class OutsourcingCostUpdate(BaseModel):
    supplier_id: Optional[int] = Field(None, ge=1, description="供应商ID")
    service_type: Optional[str] = Field(None, min_length=1, max_length=50, description="服务类型")
    description: Optional[str] = Field(None, max_length=500, description="成本描述")
    budget_amount: Optional[float] = Field(None, ge=0, description="预算金额")
    actual_amount: Optional[float] = Field(None, ge=0, description="实际金额")
    cost_date: Optional[date] = Field(None, description="成本日期")


class OutsourcingCostResponse(OutsourcingCostBase):
    id: int = Field(..., description="成本ID")
    project_id: int = Field(..., description="项目ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


# 间接成本相关模型
class IndirectCostBase(BaseModel):
    cost_type: str = Field(..., min_length=1, max_length=50, description="成本类型")
    description: Optional[str] = Field(None, max_length=500, description="成本描述")
    budget_amount: float = Field(..., ge=0, description="预算金额")
    actual_amount: float = Field(..., ge=0, description="实际金额")
    cost_date: date = Field(..., description="成本日期")


class IndirectCostCreate(IndirectCostBase):
    project_id: int = Field(..., ge=1, description="项目ID")


class IndirectCostUpdate(BaseModel):
    cost_type: Optional[str] = Field(None, min_length=1, max_length=50, description="成本类型")
    description: Optional[str] = Field(None, max_length=500, description="成本描述")
    budget_amount: Optional[float] = Field(None, ge=0, description="预算金额")
    actual_amount: Optional[float] = Field(None, ge=0, description="实际金额")
    cost_date: Optional[date] = Field(None, description="成本日期")


class IndirectCostResponse(IndirectCostBase):
    id: int = Field(..., description="成本ID")
    project_id: int = Field(..., description="项目ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


# 成本调整相关模型
class CostAdjustmentBase(BaseModel):
    adjustment_type: str = Field(..., min_length=1, max_length=20, description="调整类型")
    amount: float = Field(..., description="调整金额")
    reason: str = Field(..., min_length=1, max_length=500, description="调整原因")
    adjusted_by: str = Field(..., min_length=1, max_length=50, description="调整人")
    adjusted_at: datetime = Field(..., description="调整时间")


class CostAdjustmentCreate(CostAdjustmentBase):
    project_id: int = Field(..., ge=1, description="项目ID")


class CostAdjustmentResponse(CostAdjustmentBase):
    id: int = Field(..., description="调整ID")
    project_id: int = Field(..., description="项目ID")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True
