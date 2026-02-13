from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


# 角色相关模型
class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="角色名称")
    description: Optional[str] = Field(None, max_length=200, description="角色描述")


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="角色名称")
    description: Optional[str] = Field(None, max_length=200, description="角色描述")


class RoleResponse(RoleBase):
    id: int = Field(..., description="角色ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


# 用户相关模型
class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    role_id: int = Field(..., ge=1, description="角色ID")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=50, description="用户名")
    role_id: Optional[int] = Field(None, ge=1, description="角色ID")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="密码")


class UserResponse(UserBase):
    id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


# 人员相关模型
class PersonnelBase(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=50, description="员工编号")
    name: str = Field(..., min_length=1, max_length=100, description="人员姓名")
    department: Optional[str] = Field(None, max_length=100, description="所属部门")
    position: Optional[str] = Field(None, max_length=100, description="职位")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    email: Optional[str] = Field(None, max_length=100, description="电子邮箱")


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
    email: Optional[str] = Field(None, max_length=100, description="电子邮箱")
    password: Optional[str] = Field(None, min_length=6, max_length=255, description="密码")
    role_id: Optional[int] = Field(None, description="角色ID")


class PersonnelResponse(PersonnelBase):
    id: int = Field(..., description="人员ID")
    created_by_id: Optional[int] = Field(None, description="创建人ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    is_deleted: bool = Field(..., description="是否删除")
    
    class Config:
        from_attributes = True


# 人员费率相关模型
class PersonnelRateBase(BaseModel):
    personnel_id: int = Field(..., ge=1, description="人员ID")
    rate_type: str = Field(..., min_length=1, max_length=20, description="费率类型")
    rate: float = Field(..., ge=0, description="费率")
    effective_date: date = Field(..., description="生效日期")


class PersonnelRateCreate(PersonnelRateBase):
    pass


class PersonnelRateUpdate(BaseModel):
    rate_type: Optional[str] = Field(None, min_length=1, max_length=20, description="费率类型")
    rate: Optional[float] = Field(None, ge=0, description="费率")
    effective_date: Optional[date] = Field(None, description="生效日期")


class PersonnelRateResponse(PersonnelRateBase):
    id: int = Field(..., description="费率ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


# 物料相关模型
class MaterialBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="物料名称")
    specification: Optional[str] = Field(None, max_length=100, description="物料规格")
    unit: str = Field(..., min_length=1, max_length=20, description="计量单位")
    unit_price: float = Field(..., ge=0, description="单价")
    description: Optional[str] = Field(None, max_length=500, description="物料描述")


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="物料名称")
    specification: Optional[str] = Field(None, max_length=100, description="物料规格")
    unit: Optional[str] = Field(None, min_length=1, max_length=20, description="计量单位")
    unit_price: Optional[float] = Field(None, ge=0, description="单价")
    description: Optional[str] = Field(None, max_length=500, description="物料描述")


class MaterialResponse(MaterialBase):
    id: int = Field(..., description="物料ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


# 设备相关模型
class EquipmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="设备名称")
    model: Optional[str] = Field(None, max_length=50, description="设备型号")
    serial_number: Optional[str] = Field(None, max_length=50, description="序列号")
    status: str = Field(..., min_length=1, max_length=20, description="设备状态")
    purchase_date: Optional[date] = Field(None, description="购买日期")
    purchase_price: Optional[float] = Field(None, ge=0, description="购买价格")
    location: Optional[str] = Field(None, max_length=100, description="存放位置")
    description: Optional[str] = Field(None, max_length=500, description="设备描述")


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="设备名称")
    model: Optional[str] = Field(None, max_length=50, description="设备型号")
    serial_number: Optional[str] = Field(None, max_length=50, description="序列号")
    status: Optional[str] = Field(None, min_length=1, max_length=20, description="设备状态")
    purchase_date: Optional[date] = Field(None, description="购买日期")
    purchase_price: Optional[float] = Field(None, ge=0, description="购买价格")
    location: Optional[str] = Field(None, max_length=100, description="存放位置")
    description: Optional[str] = Field(None, max_length=500, description="设备描述")


class EquipmentResponse(EquipmentBase):
    id: int = Field(..., description="设备ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


# 员工分组关系相关模型
class EmployeeGroupRelationBase(BaseModel):
    group_name: str = Field(..., min_length=1, max_length=100, description="分组名称")
    group_description: Optional[str] = Field(None, description="分组描述")
    relation_type: str = Field(..., description="关系类型 (member/supervisor)")
    employee_id: Optional[str] = Field(None, max_length=50, description="员工编号")
    employee_name: Optional[str] = Field(None, max_length=100, description="员工姓名")
    department: Optional[str] = Field(None, max_length=100, description="所属部门")
    position: Optional[str] = Field(None, max_length=100, description="职位")
    supervisor_position: Optional[str] = Field(None, max_length=100, description="上级职位")
    is_primary: bool = Field(default=False, description="是否主要上级")
    created_by: Optional[str] = Field(None, max_length=50, description="创建人")
    remarks: Optional[str] = Field(None, description="备注")


class EmployeeGroupRelationCreate(EmployeeGroupRelationBase):
    pass


class EmployeeGroupRelationResponse(EmployeeGroupRelationBase):
    id: int = Field(..., description="关系ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class GroupInfo(BaseModel):
    """分组信息"""
    group_name: str = Field(..., description="分组名称")
    group_description: Optional[str] = Field(None, description="分组描述")
    members: List[dict] = Field(default_factory=list, description="成员列表")
    supervisors: List[dict] = Field(default_factory=list, description="上级列表")
    
    class Config:
        from_attributes = True
