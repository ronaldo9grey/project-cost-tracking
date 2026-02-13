from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.dependencies import get_db
from app.models.resource import (
    Role, 
    Personnel, 
    PersonnelRate, 
    Material,
    Equipment,
    EmployeeGroupRelation
)
from app.schemas.resource import (
    RoleCreate, 
    RoleUpdate, 
    RoleResponse,
    PersonnelCreate, 
    UserUpdate, 
    UserResponse,
    PersonnelCreate, 
    PersonnelUpdate, 
    PersonnelResponse,
    PersonnelRateCreate, 
    PersonnelRateUpdate, 
    PersonnelRateResponse,
    EquipmentCreate, 
    EquipmentUpdate, 
    EquipmentResponse,
    EmployeeGroupRelationCreate,
    EmployeeGroupRelationResponse,
    GroupInfo
)
from app.schemas.resource_management import (
    MaterialCreate, 
    MaterialUpdate, 
    MaterialResponse,
    IndirectCostTypeCreate, 
    IndirectCostTypeUpdate, 
    IndirectCostTypeResponse,
    OutsourcingServiceTypeCreate, 
    OutsourcingServiceTypeUpdate, 
    OutsourcingServiceTypeResponse
)
from app.schemas.response import SuccessResponse
from app.crud.resource_management import (
    get_material_list, 
    get_material, 
    create_material, 
    update_material, 
    delete_material,
    get_indirect_cost_type_list, 
    get_indirect_cost_type, 
    create_indirect_cost_type, 
    update_indirect_cost_type, 
    delete_indirect_cost_type,
    get_outsourcing_service_type_list, 
    get_outsourcing_service_type, 
    create_outsourcing_service_type, 
    update_outsourcing_service_type, 
    delete_outsourcing_service_type
)

router = APIRouter()


# 角色管理相关API
@router.get("/roles")
def get_roles(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """获取角色列表"""
    roles = db.query(Role).filter(Role.is_deleted == False).offset(skip).limit(limit).all()
    # 转换为字典列表，避免序列化问题
    roles_dict_list = []
    for role in roles:
        roles_dict = {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "created_at": role.created_at,
            "updated_at": role.updated_at,
            "is_deleted": role.is_deleted
        }
        roles_dict_list.append(roles_dict)
    return SuccessResponse(data=roles_dict_list, message="获取角色列表成功")


@router.post("/roles")
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    """创建角色"""
    # 检查角色名称是否已存在
    existing_role = db.query(Role).filter(Role.name == role.name, Role.is_deleted == False).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="角色名称已存在")
    
    db_role = Role(**role.dict())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    # 返回字典，避免序列化问题
    role_dict = {
        "id": db_role.id,
        "name": db_role.name,
        "description": db_role.description,
        "created_at": db_role.created_at,
        "updated_at": db_role.updated_at,
        "is_deleted": db_role.is_deleted
    }
    return SuccessResponse(data=role_dict, message="创建角色成功")


@router.put("/roles/{role_id}")
def update_role(role_id: int, role: RoleUpdate, db: Session = Depends(get_db)):
    """更新角色"""
    db_role = db.query(Role).filter(Role.id == role_id, Role.is_deleted == False).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="角色未找到")
    
    # 检查角色名称是否已存在（排除当前角色）
    if role.name and role.name != db_role.name:
        existing_role = db.query(Role).filter(Role.name == role.name, Role.is_deleted == False, Role.id != role_id).first()
        if existing_role:
            raise HTTPException(status_code=400, detail="角色名称已存在")
    
    update_data = role.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_role, field, value)
    
    db.commit()
    db.refresh(db_role)
    # 返回字典，避免序列化问题
    role_dict = {
        "id": db_role.id,
        "name": db_role.name,
        "description": db_role.description,
        "created_at": db_role.created_at,
        "updated_at": db_role.updated_at,
        "is_deleted": db_role.is_deleted
    }
    return SuccessResponse(data=role_dict, message="更新角色成功")


@router.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    """删除角色"""
    db_role = db.query(Role).filter(Role.id == role_id, Role.is_deleted == False).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="角色未找到")
    
    # 检查是否有用户关联此角色
    users_with_role = db.query(Personnel).filter(Personnel.role_id == role_id, Personnel.is_deleted == False).count()
    if users_with_role > 0:
        raise HTTPException(status_code=400, detail="该角色已被用户使用，无法删除")
    
    # 软删除
    db_role.is_deleted = True
    db.commit()
    
    return SuccessResponse(data=None, message="角色已删除")


# 用户管理相关API
@router.get("/users")
def get_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    role_id: Optional[int] = None
):
    """获取用户列表"""
    query = db.query(Personnel).filter(Personnel.is_deleted == False)
    
    if role_id:
        query = query.filter(Personnel.role_id == role_id)
    
    users = query.offset(skip).limit(limit).all()
    # 转换为字典列表，避免序列化问题
    users_dict_list = []
    for user in users:
        users_dict = {
            "id": user.id,
            "username": user.employee_id,
            "role_id": user.role_id,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "is_deleted": user.is_deleted
        }
        users_dict_list.append(users_dict)
    return SuccessResponse(data=users_dict_list, message="获取用户列表成功")


@router.post("/users")
def create_user(user: PersonnelCreate, db: Session = Depends(get_db)):
    """创建用户"""
    # 检查用户名是否已存在
    existing_user = db.query(Personnel).filter(Personnel.employee_id == user.employee_id, Personnel.is_deleted == False).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查角色是否存在
    existing_role = db.query(Role).filter(Role.id == user.role_id, Role.is_deleted == False).first()
    if not existing_role:
        raise HTTPException(status_code=400, detail="指定的角色不存在")
    
    import hashlib
    hashed_password = hashlib.md5(user.password.encode()).hexdigest() if user.password else hashlib.md5("123456".encode()).hexdigest()
    
    db_user = Personnel(
        employee_id=user.employee_id,
        name=user.name,
        department=user.department,
        position=user.position,
        phone=user.phone,
        email=user.email,
        password=hashed_password,
        role_id=user.role_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # 返回字典，避免序列化问题
    user_dict = {
        "id": db_user.id,
        "username": db_user.employee_id,
        "role_id": db_user.role_id,
        "created_at": db_user.created_at,
        "updated_at": db_user.updated_at,
        "is_deleted": db_user.is_deleted
    }
    return SuccessResponse(data=user_dict, message="创建用户成功")


@router.put("/users/{user_id}")
def update_user(user_id: int, user: PersonnelUpdate, db: Session = Depends(get_db)):
    """更新用户"""
    db_user = db.query(Personnel).filter(Personnel.id == user_id, Personnel.is_deleted == False).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户未找到")
    
    # 检查用户名是否已存在（排除当前用户）
    if user.employee_id and user.employee_id != db_user.employee_id:
        existing_user = db.query(Personnel).filter(Personnel.employee_id == user.employee_id, Personnel.is_deleted == False, Personnel.id != user_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查角色是否存在
    if user.role_id:
        existing_role = db.query(Role).filter(Role.id == user.role_id, Role.is_deleted == False).first()
        if not existing_role:
            raise HTTPException(status_code=400, detail="指定的角色不存在")
    
    import hashlib
    update_data = user.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password"] = hashlib.md5(update_data["password"].encode()).hexdigest()
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    # 返回字典，避免序列化问题
    user_dict = {
        "id": db_user.id,
        "username": db_user.employee_id,
        "role_id": db_user.role_id,
        "created_at": db_user.created_at,
        "updated_at": db_user.updated_at,
        "is_deleted": db_user.is_deleted
    }
    return SuccessResponse(data=user_dict, message="更新用户成功")


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    db_user = db.query(Personnel).filter(Personnel.id == user_id, Personnel.is_deleted == False).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户未找到")
    
    # 软删除
    db_user.is_deleted = True
    db.commit()
    
    return SuccessResponse(data=None, message="用户已删除")


# 人员管理相关API
@router.get("/personnel")
def get_personnel(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    name: Optional[str] = None,
    employee_id: Optional[str] = None,
    department: Optional[str] = None
):
    """获取人员列表，支持按员工ID和姓名模糊查询"""
    query = db.query(Personnel).filter(Personnel.is_deleted == False)
    
    if name:
        query = query.filter(Personnel.name.ilike(f"%{name}%"))
    if employee_id:
        query = query.filter(Personnel.employee_id.ilike(f"%{employee_id}%"))
    if department:
        query = query.filter(Personnel.department == department)
    
    personnel = query.offset(skip).limit(limit).all()
    # 转换为字典列表
    personnel_dict_list = []
    for p in personnel:
        personnel_dict = {
            "id": p.id,
            "employee_id": p.employee_id,
            "name": p.name,
            "department": p.department,
            "position": p.position,
            "phone": p.phone,
            "email": p.email,
            "created_by_id": p.created_by_id,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "is_deleted": p.is_deleted
        }
        personnel_dict_list.append(personnel_dict)
    return SuccessResponse(data=personnel_dict_list, message="获取人员列表成功")


@router.post("/personnel")
def create_personnel(personnel: PersonnelCreate, db: Session = Depends(get_db)):
    """创建人员"""
    # 检查员工编号是否已存在
    existing_personnel = db.query(Personnel).filter(Personnel.employee_id == personnel.employee_id, Personnel.is_deleted == False).first()
    if existing_personnel:
        raise HTTPException(status_code=400, detail="员工编号已存在")
    
    # 加密密码
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(personnel.password)
    
    # 创建人员
    db_personnel = Personnel(
        employee_id=personnel.employee_id,
        name=personnel.name,
        department=personnel.department,
        position=personnel.position,
        phone=personnel.phone,
        email=personnel.email,
        created_by_id=personnel.created_by_id,
        password=hashed_password,
        role_id=personnel.role_id
    )
    
    db.add(db_personnel)
    db.commit()
    db.refresh(db_personnel)
    # 返回字典，避免序列化问题
    personnel_dict = {
        "id": db_personnel.id,
        "employee_id": db_personnel.employee_id,
        "name": db_personnel.name,
        "department": db_personnel.department,
        "position": db_personnel.position,
        "phone": db_personnel.phone,
        "email": db_personnel.email,
        "created_by_id": db_personnel.created_by_id,
        "created_at": db_personnel.created_at,
        "updated_at": db_personnel.updated_at,
        "is_deleted": db_personnel.is_deleted
    }
    return SuccessResponse(data=personnel_dict, message="创建人员成功")


@router.put("/personnel/{personnel_id}")
def update_personnel(personnel_id: int, personnel: PersonnelUpdate, db: Session = Depends(get_db)):
    """更新人员"""
    db_personnel = db.query(Personnel).filter(Personnel.id == personnel_id, Personnel.is_deleted == False).first()
    if not db_personnel:
        raise HTTPException(status_code=404, detail="人员未找到")
    
    # 获取更新数据
    update_data = personnel.model_dump(exclude_unset=True)
    # 如果包含密码，则加密后更新
    if "password" in update_data:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        update_data["password"] = pwd_context.hash(update_data["password"])
    
    # 更新字段
    for field, value in update_data.items():
        setattr(db_personnel, field, value)
    
    db.commit()
    db.refresh(db_personnel)
    # 返回字典，避免序列化问题
    personnel_dict = {
        "id": db_personnel.id,
        "employee_id": db_personnel.employee_id,
        "name": db_personnel.name,
        "department": db_personnel.department,
        "position": db_personnel.position,
        "phone": db_personnel.phone,
        "email": db_personnel.email,
        "created_by_id": db_personnel.created_by_id,
        "created_at": db_personnel.created_at,
        "updated_at": db_personnel.updated_at,
        "is_deleted": db_personnel.is_deleted
    }
    return SuccessResponse(data=personnel_dict, message="更新人员成功")


@router.delete("/personnel/{personnel_id}")
def delete_personnel(personnel_id: int, db: Session = Depends(get_db)):
    """删除人员"""
    db_personnel = db.query(Personnel).filter(Personnel.id == personnel_id, Personnel.is_deleted == False).first()
    if not db_personnel:
        raise HTTPException(status_code=404, detail="人员未找到")
    
    # 软删除
    db_personnel.is_deleted = True
    db.commit()
    
    return SuccessResponse(data=None, message="人员已删除")


# 人员费率相关API
@router.get("/personnel-rates")
def get_personnel_rates(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    personnel_id: Optional[int] = None
):
    """获取人员费率列表"""
    query = db.query(PersonnelRate).filter(PersonnelRate.is_deleted == False)
    
    if personnel_id:
        query = query.filter(PersonnelRate.personnel_id == personnel_id)
    
    rates = query.offset(skip).limit(limit).all()
    # 转换为字典列表，避免序列化关联模型
    rates_dict_list = []
    for rate in rates:
        rates_dict = {
            "id": rate.id,
            "personnel_id": rate.personnel_id,
            "rate_type": rate.rate_type,
            "rate": rate.rate,
            "effective_date": rate.effective_date,
            "created_at": rate.created_at,
            "updated_at": rate.updated_at,
            "is_deleted": rate.is_deleted
        }
        rates_dict_list.append(rates_dict)
    return SuccessResponse(data=rates_dict_list, message="获取人员费率列表成功")


@router.post("/personnel-rates")
def create_personnel_rate(rate: PersonnelRateCreate, db: Session = Depends(get_db)):
    """创建人员费率"""
    # 检查人员是否存在
    existing_personnel = db.query(Personnel).filter(Personnel.id == rate.personnel_id, Personnel.is_deleted == False).first()
    if not existing_personnel:
        raise HTTPException(status_code=400, detail="指定的人员不存在")
    
    db_rate = PersonnelRate(**rate.dict())
    db.add(db_rate)
    db.commit()
    db.refresh(db_rate)
    # 返回字典，避免序列化问题
    rate_dict = {
        "id": db_rate.id,
        "personnel_id": db_rate.personnel_id,
        "rate_type": db_rate.rate_type,
        "rate": db_rate.rate,
        "effective_date": db_rate.effective_date,
        "created_at": db_rate.created_at,
        "updated_at": db_rate.updated_at,
        "is_deleted": db_rate.is_deleted
    }
    return SuccessResponse(data=rate_dict, message="创建人员费率成功")


@router.put("/personnel-rates/{rate_id}")
def update_personnel_rate(rate_id: int, rate: PersonnelRateUpdate, db: Session = Depends(get_db)):
    """更新人员费率"""
    db_rate = db.query(PersonnelRate).filter(PersonnelRate.id == rate_id, PersonnelRate.is_deleted == False).first()
    if not db_rate:
        raise HTTPException(status_code=404, detail="人员费率未找到")
    
    update_data = rate.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rate, field, value)
    
    db.commit()
    db.refresh(db_rate)
    # 返回字典，避免序列化问题
    rate_dict = {
        "id": db_rate.id,
        "personnel_id": db_rate.personnel_id,
        "rate_type": db_rate.rate_type,
        "rate": db_rate.rate,
        "effective_date": db_rate.effective_date,
        "created_at": db_rate.created_at,
        "updated_at": db_rate.updated_at,
        "is_deleted": db_rate.is_deleted
    }
    return SuccessResponse(data=rate_dict, message="更新人员费率成功")


@router.delete("/personnel-rates/{rate_id}")
def delete_personnel_rate(rate_id: int, db: Session = Depends(get_db)):
    """删除人员费率"""
    db_rate = db.query(PersonnelRate).filter(PersonnelRate.id == rate_id, PersonnelRate.is_deleted == False).first()
    if not db_rate:
        raise HTTPException(status_code=404, detail="人员费率未找到")
    
    # 软删除
    db_rate.is_deleted = True
    db.commit()
    
    return SuccessResponse(data=None, message="人员费率已删除")


# 物料管理相关API
@router.get("/materials")
def get_materials(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    material_name: Optional[str] = None,
    supplier: Optional[str] = None
):
    """获取物料列表"""
    materials = get_material_list(db, skip=skip, limit=limit, material_name=material_name, supplier=supplier)
    # 转换为字典列表，避免序列化问题
    materials_dict_list = []
    for material in materials:
        materials_dict = {
            "material_id": material.material_id,
            "material_name": material.material_name,
            "specification": material.specification,
            "unit": material.unit,
            "stock_quantity": material.stock_quantity,
            "unit_price": material.unit_price,
            "supplier": material.supplier,
            "create_time": material.create_time,
            "update_time": material.update_time,
            "is_deleted": material.is_deleted
        }
        materials_dict_list.append(materials_dict)
    return SuccessResponse(data=materials_dict_list, message="获取物料列表成功")


@router.post("/materials")
def create_new_material(material: MaterialCreate, db: Session = Depends(get_db)):
    """创建物料"""
    # 检查物料编号是否已存在
    existing_material = db.query(Material).filter(Material.material_id == material.material_id, Material.is_deleted == False).first()
    if existing_material:
        raise HTTPException(status_code=400, detail="物料编号已存在")
    
    db_material = create_material(db, material)
    # 返回字典，避免序列化问题
    material_dict = {
        "material_id": db_material.material_id,
        "material_name": db_material.material_name,
        "specification": db_material.specification,
        "unit": db_material.unit,
        "stock_quantity": db_material.stock_quantity,
        "unit_price": db_material.unit_price,
        "supplier": db_material.supplier,
        "create_time": db_material.create_time,
        "update_time": db_material.update_time,
        "is_deleted": db_material.is_deleted
    }
    return SuccessResponse(data=material_dict, message="创建物料成功")


@router.put("/materials/{material_id}")
def update_new_material(material_id: str, material: MaterialUpdate, db: Session = Depends(get_db)):
    """更新物料"""
    db_material = update_material(db, material_id, material)
    if not db_material:
        raise HTTPException(status_code=404, detail="物料未找到")
    # 返回字典，避免序列化问题
    material_dict = {
        "material_id": db_material.material_id,
        "material_name": db_material.material_name,
        "specification": db_material.specification,
        "unit": db_material.unit,
        "stock_quantity": db_material.stock_quantity,
        "unit_price": db_material.unit_price,
        "supplier": db_material.supplier,
        "create_time": db_material.create_time,
        "update_time": db_material.update_time,
        "is_deleted": db_material.is_deleted
    }
    return SuccessResponse(data=material_dict, message="更新物料成功")


@router.delete("/materials/{material_id}")
def delete_new_material(material_id: str, db: Session = Depends(get_db)):
    """删除物料"""
    success = delete_material(db, material_id)
    if not success:
        raise HTTPException(status_code=404, detail="物料未找到")
    return SuccessResponse(data=None, message="物料已删除")


# 间接成本类型相关API
@router.get("/indirect-cost-types")
def get_indirect_cost_types(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    type_name: Optional[str] = None
):
    """获取间接成本类型列表"""
    cost_types = get_indirect_cost_type_list(db, skip=skip, limit=limit, type_name=type_name)
    # 转换为字典列表，避免序列化问题
    cost_types_dict_list = []
    for ct in cost_types:
        cost_type_dict = {
            "id": ct.id,
            "type_name": ct.type_name,
            "description": ct.description,
            "created_at": ct.created_at,
            "updated_at": ct.updated_at,
            "is_deleted": ct.is_deleted
        }
        cost_types_dict_list.append(cost_type_dict)
    return SuccessResponse(data=cost_types_dict_list, message="获取间接成本类型列表成功")


@router.post("/indirect-cost-types")
def create_new_indirect_cost_type(cost_type: IndirectCostTypeCreate, db: Session = Depends(get_db)):
    """创建间接成本类型"""
    # 检查成本类型名称是否已存在
    existing_type = db.query(IndirectCostType).filter(IndirectCostType.type_name == cost_type.type_name, IndirectCostType.is_deleted == False).first()
    if existing_type:
        raise HTTPException(status_code=400, detail="成本类型名称已存在")
    
    db_cost_type = create_indirect_cost_type(db, cost_type)
    # 返回字典，避免序列化问题
    cost_type_dict = {
        "id": db_cost_type.id,
        "type_name": db_cost_type.type_name,
        "description": db_cost_type.description,
        "created_at": db_cost_type.created_at,
        "updated_at": db_cost_type.updated_at,
        "is_deleted": db_cost_type.is_deleted
    }
    return SuccessResponse(data=cost_type_dict, message="创建间接成本类型成功")


@router.put("/indirect-cost-types/{type_id}")
def update_new_indirect_cost_type(type_id: int, cost_type: IndirectCostTypeUpdate, db: Session = Depends(get_db)):
    """更新间接成本类型"""
    db_cost_type = update_indirect_cost_type(db, type_id, cost_type)
    if not db_cost_type:
        raise HTTPException(status_code=404, detail="间接成本类型未找到")
    # 返回字典，避免序列化问题
    cost_type_dict = {
        "id": db_cost_type.id,
        "type_name": db_cost_type.type_name,
        "description": db_cost_type.description,
        "created_at": db_cost_type.created_at,
        "updated_at": db_cost_type.updated_at,
        "is_deleted": db_cost_type.is_deleted
    }
    return SuccessResponse(data=cost_type_dict, message="更新间接成本类型成功")


@router.delete("/indirect-cost-types/{type_id}")
def delete_new_indirect_cost_type(type_id: int, db: Session = Depends(get_db)):
    """删除间接成本类型"""
    success = delete_indirect_cost_type(db, type_id)
    if not success:
        raise HTTPException(status_code=404, detail="间接成本类型未找到")
    return SuccessResponse(data=None, message="间接成本类型已删除")


# 外包服务类型相关API
@router.get("/outsourcing-service-types")
def get_outsourcing_service_types(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    type_name: Optional[str] = None
):
    """获取外包服务类型列表"""
    service_types = get_outsourcing_service_type_list(db, skip=skip, limit=limit, type_name=type_name)
    # 转换为字典列表，避免序列化问题
    service_types_dict_list = []
    for st in service_types:
        service_type_dict = {
            "id": st.id,
            "type_name": st.type_name,
            "description": st.description,
            "created_at": st.created_at,
            "updated_at": st.updated_at,
            "is_deleted": st.is_deleted
        }
        service_types_dict_list.append(service_type_dict)
    return SuccessResponse(data=service_types_dict_list, message="获取外包服务类型列表成功")


@router.post("/outsourcing-service-types")
def create_new_outsourcing_service_type(service_type: OutsourcingServiceTypeCreate, db: Session = Depends(get_db)):
    """创建外包服务类型"""
    # 检查服务类型名称是否已存在
    existing_type = db.query(OutsourcingServiceType).filter(OutsourcingServiceType.type_name == service_type.type_name, OutsourcingServiceType.is_deleted == False).first()
    if existing_type:
        raise HTTPException(status_code=400, detail="服务类型名称已存在")
    
    db_service_type = create_outsourcing_service_type(db, service_type)
    # 返回字典，避免序列化问题
    service_type_dict = {
        "id": db_service_type.id,
        "type_name": db_service_type.type_name,
        "description": db_service_type.description,
        "created_at": db_service_type.created_at,
        "updated_at": db_service_type.updated_at,
        "is_deleted": db_service_type.is_deleted
    }
    return SuccessResponse(data=service_type_dict, message="创建外包服务类型成功")


@router.put("/outsourcing-service-types/{type_id}")
def update_new_outsourcing_service_type(type_id: int, service_type: OutsourcingServiceTypeUpdate, db: Session = Depends(get_db)):
    """更新外包服务类型"""
    db_service_type = update_outsourcing_service_type(db, type_id, service_type)
    if not db_service_type:
        raise HTTPException(status_code=404, detail="外包服务类型未找到")
    # 返回字典，避免序列化问题
    service_type_dict = {
        "id": db_service_type.id,
        "type_name": db_service_type.type_name,
        "description": db_service_type.description,
        "created_at": db_service_type.created_at,
        "updated_at": db_service_type.updated_at,
        "is_deleted": db_service_type.is_deleted
    }
    return SuccessResponse(data=service_type_dict, message="更新外包服务类型成功")


@router.delete("/outsourcing-service-types/{type_id}")
def delete_new_outsourcing_service_type(type_id: int, db: Session = Depends(get_db)):
    """删除外包服务类型"""
    success = delete_outsourcing_service_type(db, type_id)
    if not success:
        raise HTTPException(status_code=404, detail="外包服务类型未找到")
    return SuccessResponse(data=None, message="外包服务类型已删除")


# 设备管理相关API
@router.get("/equipment")
def get_equipment(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None
):
    """获取设备列表"""
    query = db.query(Equipment).filter(Equipment.is_deleted == False)
    
    if status:
        query = query.filter(Equipment.status == status)
    
    equipment = query.offset(skip).limit(limit).all()
    # 转换为字典列表，避免序列化问题
    equipment_dict_list = []
    for eq in equipment:
        equipment_dict = {
            "id": eq.id,
            "name": eq.name,
            "model": eq.model,
            "serial_number": eq.serial_number,
            "status": eq.status,
            "purchase_date": eq.purchase_date,
            "purchase_price": eq.purchase_price,
            "location": eq.location,
            "description": eq.description,
            "created_at": eq.created_at,
            "updated_at": eq.updated_at,
            "is_deleted": eq.is_deleted
        }
        equipment_dict_list.append(equipment_dict)
    return SuccessResponse(data=equipment_dict_list, message="获取设备列表成功")


@router.post("/equipment")
def create_equipment(equipment: EquipmentCreate, db: Session = Depends(get_db)):
    """创建设备"""
    db_equipment = Equipment(**equipment.dict())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    # 返回字典，避免序列化问题
    equipment_dict = {
        "id": db_equipment.id,
        "name": db_equipment.name,
        "model": db_equipment.model,
        "serial_number": db_equipment.serial_number,
        "status": db_equipment.status,
        "purchase_date": db_equipment.purchase_date,
        "purchase_price": db_equipment.purchase_price,
        "location": db_equipment.location,
        "description": db_equipment.description,
        "created_at": db_equipment.created_at,
        "updated_at": db_equipment.updated_at,
        "is_deleted": db_equipment.is_deleted
    }
    return SuccessResponse(data=equipment_dict, message="创建设备成功")


@router.put("/equipment/{equipment_id}")
def update_equipment(equipment_id: int, equipment: EquipmentUpdate, db: Session = Depends(get_db)):
    """更新设备"""
    db_equipment = db.query(Equipment).filter(Equipment.id == equipment_id, Equipment.is_deleted == False).first()
    if not db_equipment:
        raise HTTPException(status_code=404, detail="设备未找到")
    
    update_data = equipment.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_equipment, field, value)
    
    db.commit()
    db.refresh(db_equipment)
    # 返回字典，避免序列化问题
    equipment_dict = {
        "id": db_equipment.id,
        "name": db_equipment.name,
        "model": db_equipment.model,
        "serial_number": db_equipment.serial_number,
        "status": db_equipment.status,
        "purchase_date": db_equipment.purchase_date,
        "purchase_price": db_equipment.purchase_price,
        "location": db_equipment.location,
        "description": db_equipment.description,
        "created_at": db_equipment.created_at,
        "updated_at": db_equipment.updated_at,
        "is_deleted": db_equipment.is_deleted
    }
    return SuccessResponse(data=equipment_dict, message="更新设备成功")


@router.delete("/equipment/{equipment_id}")
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    """删除设备"""
    db_equipment = db.query(Equipment).filter(Equipment.id == equipment_id, Equipment.is_deleted == False).first()
    if not db_equipment:
        raise HTTPException(status_code=404, detail="设备未找到")
    
    # 软删除
    db_equipment.is_deleted = True
    db.commit()
    
    return SuccessResponse(data=None, message="设备已删除")


# 员工分组关系相关API
@router.get("/employee-group-relations")
def get_employee_group_relations(db: Session = Depends(get_db)):
    """获取员工分组关系列表"""
    relations = db.query(EmployeeGroupRelation).all()
    # 转换为字典列表
    relations_dict_list = []
    for relation in relations:
        relation_dict = {
            "id": relation.id,
            "group_name": relation.group_name,
            "group_description": relation.group_description,
            "relation_type": relation.relation_type,
            "employee_id": relation.employee_id,
            "employee_name": relation.employee_name,
            "department": relation.department,
            "position": relation.position,
            "supervisor_position": relation.supervisor_position,
            "is_primary": relation.is_primary,
            "created_at": relation.created_at,
            "updated_at": relation.updated_at,
            "created_by": relation.created_by,
            "remarks": relation.remarks
        }
        relations_dict_list.append(relation_dict)
    return SuccessResponse(data=relations_dict_list, message="获取员工分组关系列表成功")


@router.post("/group-members")
def create_group_member(member: EmployeeGroupRelationCreate, db: Session = Depends(get_db)):
    """添加分组成员"""
    if member.relation_type != 'member':
        raise HTTPException(status_code=400, detail="请使用正确的接口添加上级")
    
    # 检查是否已存在相同的关系
    existing = db.query(EmployeeGroupRelation).filter(
        EmployeeGroupRelation.group_name == member.group_name,
        EmployeeGroupRelation.employee_id == member.employee_id,
        EmployeeGroupRelation.relation_type == 'member'
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="该员工已在分组中")
    
    db_member = EmployeeGroupRelation(**member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    
    # 返回字典
    member_dict = {
        "id": db_member.id,
        "group_name": db_member.group_name,
        "group_description": db_member.group_description,
        "relation_type": db_member.relation_type,
        "employee_id": db_member.employee_id,
        "employee_name": db_member.employee_name,
        "department": db_member.department,
        "position": db_member.position,
        "supervisor_position": db_member.supervisor_position,
        "is_primary": db_member.is_primary,
        "created_at": db_member.created_at,
        "updated_at": db_member.updated_at,
        "created_by": db_member.created_by,
        "remarks": db_member.remarks
    }
    return SuccessResponse(data=member_dict, message="添加分组成员成功")


@router.post("/groups")
def create_empty_group(group_data: dict, db: Session = Depends(get_db)):
    """创建空分组（只创建分组记录，不添加成员）"""
    group_name = group_data.get("group_name")
    group_description = group_data.get("group_description", "")
    
    if not group_name:
        raise HTTPException(status_code=400, detail="分组名称不能为空")
    
    # 检查分组是否已存在
    existing = db.query(EmployeeGroupRelation).filter(
        EmployeeGroupRelation.group_name == group_name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="分组名称已存在")
    
    # 创建一个空分组记录（使用一个虚拟员工ID来标识）
    empty_group = EmployeeGroupRelation(
        group_name=group_name,
        group_description=group_description,
        relation_type="member",  # 使用member类型作为分组标识
        employee_id="GROUP_EMPTY",
        employee_name="空分组",
        department="",
        position="",
        is_primary=False
    )
    
    db.add(empty_group)
    db.commit()
    db.refresh(empty_group)
    
    # 返回字典
    group_dict = {
        "id": empty_group.id,
        "group_name": empty_group.group_name,
        "group_description": empty_group.group_description,
        "relation_type": empty_group.relation_type,
        "employee_id": empty_group.employee_id,
        "employee_name": empty_group.employee_name,
        "department": empty_group.department,
        "position": empty_group.position,
        "supervisor_position": empty_group.supervisor_position,
        "is_primary": empty_group.is_primary,
        "created_at": empty_group.created_at,
        "updated_at": empty_group.updated_at,
        "created_by": empty_group.created_by,
        "remarks": empty_group.remarks
    }
    return SuccessResponse(data=group_dict, message="创建分组成功")


@router.post("/group-supervisors")
def create_group_supervisor(supervisor: EmployeeGroupRelationCreate, db: Session = Depends(get_db)):
    """添加分组上级"""
    if supervisor.relation_type != 'supervisor':
        raise HTTPException(status_code=400, detail="请使用正确的接口添加成员")
    
    # 检查是否已存在相同的关系
    existing = db.query(EmployeeGroupRelation).filter(
        EmployeeGroupRelation.group_name == supervisor.group_name,
        EmployeeGroupRelation.employee_id == supervisor.employee_id,
        EmployeeGroupRelation.relation_type == 'supervisor'
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="该上级已在分组中")
    
    # 检查分组的上级数量是否超过3个
    supervisor_count = db.query(EmployeeGroupRelation).filter(
        EmployeeGroupRelation.group_name == supervisor.group_name,
        EmployeeGroupRelation.relation_type == 'supervisor'
    ).count()
    
    if supervisor_count >= 3:
        raise HTTPException(status_code=400, detail="一个分组最多只能有3个上级")
    
    db_supervisor = EmployeeGroupRelation(**supervisor.dict())
    db.add(db_supervisor)
    db.commit()
    db.refresh(db_supervisor)
    
    # 返回字典
    supervisor_dict = {
        "id": db_supervisor.id,
        "group_name": db_supervisor.group_name,
        "group_description": db_supervisor.group_description,
        "relation_type": db_supervisor.relation_type,
        "employee_id": db_supervisor.employee_id,
        "employee_name": db_supervisor.employee_name,
        "department": db_supervisor.department,
        "position": db_supervisor.position,
        "supervisor_position": db_supervisor.supervisor_position,
        "is_primary": db_supervisor.is_primary,
        "created_at": db_supervisor.created_at,
        "updated_at": db_supervisor.updated_at,
        "created_by": db_supervisor.created_by,
        "remarks": db_supervisor.remarks
    }
    return SuccessResponse(data=supervisor_dict, message="添加分组上级成功")


@router.put("/group-relations/{relation_id}")
def update_group_relation(relation_id: int, update_data: dict, db: Session = Depends(get_db)):
    """更新员工分组关系（主要用于设置主上级）"""
    db_relation = db.query(EmployeeGroupRelation).filter(EmployeeGroupRelation.id == relation_id).first()
    if not db_relation:
        raise HTTPException(status_code=404, detail="关系记录未找到")
    
    # 如果要设置为主上级，先将同一分组的所有其他上级设为非主上级
    if update_data.get("is_primary") is True:
        # 找到同一分组的所有上级关系
        same_group_relations = db.query(EmployeeGroupRelation).filter(
            EmployeeGroupRelation.group_name == db_relation.group_name,
            EmployeeGroupRelation.relation_type == "supervisor",
            EmployeeGroupRelation.id != relation_id
        ).all()
        
        # 将其他上级设为非主上级
        for relation in same_group_relations:
            relation.is_primary = False
    
    # 更新指定的关系
    for field, value in update_data.items():
        if hasattr(db_relation, field):
            setattr(db_relation, field, value)
    
    db.commit()
    db.refresh(db_relation)
    
    # 返回字典
    relation_dict = {
        "id": db_relation.id,
        "group_name": db_relation.group_name,
        "group_description": db_relation.group_description,
        "relation_type": db_relation.relation_type,
        "employee_id": db_relation.employee_id,
        "employee_name": db_relation.employee_name,
        "department": db_relation.department,
        "position": db_relation.position,
        "supervisor_position": db_relation.supervisor_position,
        "is_primary": db_relation.is_primary,
        "created_at": db_relation.created_at,
        "updated_at": db_relation.updated_at,
        "created_by": db_relation.created_by,
        "remarks": db_relation.remarks
    }
    return SuccessResponse(data=relation_dict, message="更新关系成功")


@router.delete("/group-relations/{relation_id}")
def delete_group_relation(relation_id: int, db: Session = Depends(get_db)):
    """删除分组关系记录"""
    db_relation = db.query(EmployeeGroupRelation).filter(EmployeeGroupRelation.id == relation_id).first()
    if not db_relation:
        raise HTTPException(status_code=404, detail="关系记录未找到")
    
    db.delete(db_relation)
    db.commit()
    
    return SuccessResponse(data=None, message="关系记录已删除")


@router.delete("/groups/{group_name}")
def delete_entire_group(group_name: str, db: Session = Depends(get_db)):
    """删除整个分组（删除所有相关记录）"""
    relations = db.query(EmployeeGroupRelation).filter(EmployeeGroupRelation.group_name == group_name).all()
    
    if not relations:
        raise HTTPException(status_code=404, detail="分组不存在")
    
    for relation in relations:
        db.delete(relation)
    
    db.commit()
    
    return SuccessResponse(data=None, message=f"分组 '{group_name}' 及其所有关系已删除")


@router.put("/groups/{group_name}/description")
def update_group_description(group_name: str, description_data: dict, db: Session = Depends(get_db)):
    """更新分组描述"""
    description = description_data.get("description")
    
    if description is None:
        raise HTTPException(status_code=400, detail="缺少描述内容")
    
    # 更新所有相关记录的描述
    relations = db.query(EmployeeGroupRelation).filter(EmployeeGroupRelation.group_name == group_name).all()
    
    if not relations:
        raise HTTPException(status_code=404, detail="分组不存在")
    
    for relation in relations:
        relation.group_description = description
    
    db.commit()
    
    return SuccessResponse(data=None, message=f"分组 '{group_name}' 描述已更新")
