from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

# 人员管理模型

class PersonnelBase(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=50, description="员工编号")
    name: str = Field(..., min_length=1, max_length=100, description="人员姓名")
    department: Optional[str] = Field(None, max_length=100, description="所属部门")
    position: Optional[str] = Field(None, max_length=100, description="职位")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    
    class Config:
        from_attributes = True

class PersonnelCreate(PersonnelBase):
    created_by_id: Optional[int] = Field(None, description="创建人ID")
    password: str = Field(default="123456", min_length=6, max_length=255, description="密码")
    role_id: Optional[int] = Field(None, description="角色ID")

class PersonnelUpdate(BaseModel):
    employee_id: Optional[str] = Field(None, min_length=1, max_length=50, description="员工编号")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="人员姓名")
    department: Optional[str] = Field(None, max_length=100, description="所属部门")
    position: Optional[str] = Field(None, max_length=100, description="职位")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    password: Optional[str] = Field(None, min_length=6, max_length=255, description="密码")
    role_id: Optional[int] = Field(None, description="角色ID")
    
    class Config:
        from_attributes = True

class PersonnelResponse(PersonnelBase):
    id: int = Field(..., description="人员ID")
    created_by_id: Optional[int] = Field(None, description="创建人ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    is_deleted: bool = Field(..., description="是否删除")
    
    class Config:
        from_attributes = True

# 设备管理模型

class EquipmentBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=100, description="设备编号")
    name: str = Field(..., min_length=1, max_length=255, description="设备名称")
    model: str = Field(..., min_length=1, max_length=255, description="设备型号")
    specification: Optional[str] = Field(None, description="设备规格")
    status: str = Field(default="在用", description="设备状态")
    location: Optional[str] = Field(None, max_length=255, description="设备位置")
    maintainer: Optional[str] = Field(None, max_length=100, description="维护人员")
    
    class Config:
        from_attributes = True

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=100, description="设备编号")
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="设备名称")
    model: Optional[str] = Field(None, min_length=1, max_length=255, description="设备型号")
    specification: Optional[str] = Field(None, description="设备规格")
    status: Optional[str] = Field(None, description="设备状态")
    location: Optional[str] = Field(None, max_length=255, description="设备位置")
    maintainer: Optional[str] = Field(None, max_length=100, description="维护人员")
    
    class Config:
        from_attributes = True

class EquipmentResponse(EquipmentBase):
    id: int = Field(..., description="设备ID")
    purchase_date: Optional[date] = Field(None, description="购买日期")
    create_time: Optional[date] = Field(None, description="创建时间")
    update_time: Optional[date] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True

# 物料管理模型

class MaterialBase(BaseModel):
    material_id: str = Field(..., min_length=1, max_length=50, description="物料编号")
    material_name: str = Field(..., min_length=1, max_length=200, description="物料名称")
    specification: Optional[str] = Field(None, max_length=200, description="规格")
    unit: Optional[str] = Field(None, max_length=50, description="单位")
    stock_quantity: Optional[float] = Field(0.0, description="库存数量")
    unit_price: Optional[float] = Field(0.0, description="单价")
    supplier: Optional[str] = Field(None, max_length=200, description="供应商")
    
    class Config:
        from_attributes = True

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    material_id: Optional[str] = Field(None, min_length=1, max_length=50, description="物料编号")
    material_name: Optional[str] = Field(None, min_length=1, max_length=200, description="物料名称")
    specification: Optional[str] = Field(None, max_length=200, description="规格")
    unit: Optional[str] = Field(None, max_length=50, description="单位")
    stock_quantity: Optional[float] = Field(None, description="库存数量")
    unit_price: Optional[float] = Field(None, description="单价")
    supplier: Optional[str] = Field(None, max_length=200, description="供应商")
    
    class Config:
        from_attributes = True

class MaterialResponse(MaterialBase):
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")
    is_deleted: bool = Field(..., description="是否删除")
    
    class Config:
        from_attributes = True

# 间接成本类型模型

class IndirectCostTypeBase(BaseModel):
    type_name: str = Field(..., min_length=1, max_length=100, description="成本类型名称")
    description: Optional[str] = Field(None, description="成本类型描述")
    
    class Config:
        from_attributes = True

class IndirectCostTypeCreate(IndirectCostTypeBase):
    pass

class IndirectCostTypeUpdate(BaseModel):
    type_name: Optional[str] = Field(None, min_length=1, max_length=100, description="成本类型名称")
    description: Optional[str] = Field(None, description="成本类型描述")
    
    class Config:
        from_attributes = True

class IndirectCostTypeResponse(IndirectCostTypeBase):
    id: int = Field(..., description="成本类型ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    is_deleted: bool = Field(..., description="是否删除")
    
    class Config:
        from_attributes = True

# 外包服务类型模型

class OutsourcingServiceTypeBase(BaseModel):
    type_name: str = Field(..., min_length=1, max_length=100, description="服务类型名称")
    description: Optional[str] = Field(None, description="服务类型描述")
    
    class Config:
        from_attributes = True

class OutsourcingServiceTypeCreate(OutsourcingServiceTypeBase):
    pass

class OutsourcingServiceTypeUpdate(BaseModel):
    type_name: Optional[str] = Field(None, min_length=1, max_length=100, description="服务类型名称")
    description: Optional[str] = Field(None, description="服务类型描述")
    
    class Config:
        from_attributes = True

class OutsourcingServiceTypeResponse(OutsourcingServiceTypeBase):
    id: int = Field(..., description="服务类型ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    is_deleted: bool = Field(..., description="是否删除")
    
    class Config:
        from_attributes = True

# 资源概览模型

class ResourceOverview(BaseModel):
    total_personnel: int = Field(..., description="总人员数")
    total_equipment: int = Field(..., description="总设备数")
    allocated_personnel: int = Field(..., description="已分配人员数")
    allocated_equipment: int = Field(..., description="已分配设备数")
    idle_personnel: int = Field(..., description="闲置人员数")
    idle_equipment: int = Field(..., description="闲置设备数")
    personnel_by_department: dict[str, int] = Field(..., description="部门人员分布")
    equipment_by_status: dict[str, int] = Field(..., description="设备状态分布")
    
    class Config:
        from_attributes = True