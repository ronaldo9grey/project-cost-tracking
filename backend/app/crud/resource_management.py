from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date
from app.models.resource import Personnel, Equipment
from app.schemas.resource_management import (
    PersonnelCreate,
    PersonnelUpdate,
    EquipmentCreate,
    EquipmentUpdate,
    ResourceOverview
)
from passlib.context import CryptContext

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 导入Materials模型和schema
from app.models.resource import Material, IndirectCostType, OutsourcingServiceType
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

# 人员管理CRUD

def get_personnel_list(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    department: Optional[str] = None
) -> List[Personnel]:
    """
    获取人员列表，支持分页、姓名模糊查询和部门过滤
    """
    query = db.query(Personnel).filter(Personnel.is_deleted == False)
    
    # 应用过滤条件
    if name:
        query = query.filter(Personnel.name.ilike(f"%{name}%"))
    if department:
        query = query.filter(Personnel.department == department)
    
    # 应用分页并获取结果
    return query.offset(skip).limit(limit).all()

def get_personnel(db: Session, personnel_id: int) -> Optional[Personnel]:
    """
    根据人员ID获取人员
    """
    return db.query(Personnel).filter(Personnel.id == personnel_id, Personnel.is_deleted == False).first()

def create_personnel(db: Session, personnel: PersonnelCreate) -> Personnel:
    """
    创建新人员
    """
    # 加密密码
    hashed_password = pwd_context.hash(personnel.password)
    
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
    return db_personnel

def update_personnel(db: Session, personnel_id: int, personnel: PersonnelUpdate) -> Optional[Personnel]:
    """
    更新人员信息
    """
    db_personnel = get_personnel(db, personnel_id=personnel_id)
    if db_personnel is None:
        return None
    
    # 获取更新数据
    update_data = personnel.model_dump(exclude_unset=True)
    
    # 如果包含密码，则加密后更新
    if "password" in update_data:
        update_data["password"] = pwd_context.hash(update_data["password"])
    
    # 更新字段
    for field, value in update_data.items():
        setattr(db_personnel, field, value)
    
    db.add(db_personnel)
    db.commit()
    db.refresh(db_personnel)
    return db_personnel

def delete_personnel(db: Session, personnel_id: int) -> bool:
    """
    删除人员（软删除）
    """
    db_personnel = get_personnel(db, personnel_id=personnel_id)
    if db_personnel is None:
        return False
    
    db_personnel.is_deleted = True
    
    db.add(db_personnel)
    db.commit()
    return True

# 设备管理CRUD

def get_equipment_list(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    status: Optional[str] = None,
    location: Optional[str] = None
) -> List[Equipment]:
    """
    获取设备列表，支持分页、名称模糊查询、状态和位置过滤
    """
    query = db.query(Equipment).filter(Equipment.is_deleted == 0)
    
    # 应用过滤条件
    if name:
        query = query.filter(Equipment.name.ilike(f"%{name}%"))
    if status:
        query = query.filter(Equipment.status == status)
    if location:
        query = query.filter(Equipment.location == location)
    
    # 应用分页并获取结果
    return query.offset(skip).limit(limit).all()

def get_equipment(db: Session, equipment_id: int) -> Optional[Equipment]:
    """
    根据设备ID获取设备
    """
    return db.query(Equipment).filter(Equipment.id == equipment_id, Equipment.is_deleted == 0).first()

def create_equipment(db: Session, equipment: EquipmentCreate) -> Equipment:
    """
    创建设备
    """
    db_equipment = Equipment(
        code=equipment.code,
        name=equipment.name,
        model=equipment.model,
        specification=equipment.specification,
        status=equipment.status,
        location=equipment.location,
        maintainer=equipment.maintainer,
        create_time=date.today(),
        update_time=date.today()
    )
    
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

def update_equipment(db: Session, equipment_id: int, equipment: EquipmentUpdate) -> Optional[Equipment]:
    """
    更新设备信息
    """
    db_equipment = get_equipment(db, equipment_id=equipment_id)
    if db_equipment is None:
        return None
    
    # 更新设备基本信息
    update_data = equipment.model_dump(exclude_unset=True)
    
    # 更新字段
    for field, value in update_data.items():
        setattr(db_equipment, field, value)
    
    # 更新时间
    db_equipment.update_time = date.today()
    
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

def delete_equipment(db: Session, equipment_id: int) -> bool:
    """
    删除设备（软删除）
    """
    db_equipment = get_equipment(db, equipment_id=equipment_id)
    if db_equipment is None:
        return False
    
    db_equipment.is_deleted = 1
    db_equipment.update_time = date.today()
    
    db.add(db_equipment)
    db.commit()
    return True

# 资源概览

def get_resource_overview(db: Session) -> ResourceOverview:
    """
    获取资源概览信息
    """
    # 计算总人员数
    total_personnel = db.query(func.count(Personnel.id)).filter(Personnel.is_deleted == 0).scalar() or 0
    
    # 计算总设备数
    total_equipment = db.query(func.count(Equipment.id)).filter(Equipment.is_deleted == 0).scalar() or 0
    
    # 计算已分配人员数（假设status != '离职' 即为已分配）
    allocated_personnel = db.query(func.count(Personnel.id)).filter(
        Personnel.is_deleted == 0, Personnel.status != '离职'
    ).scalar() or 0
    
    # 计算已分配设备数（假设status == '在用' 即为已分配）
    allocated_equipment = db.query(func.count(Equipment.id)).filter(
        Equipment.is_deleted == 0, Equipment.status == '在用'
    ).scalar() or 0
    
    # 计算闲置人员数
    idle_personnel = total_personnel - allocated_personnel
    
    # 计算闲置设备数
    idle_equipment = total_equipment - allocated_equipment
    
    # 计算部门人员分布
    department_counts = db.query(
        Personnel.department,
        func.count(Personnel.id).label('count')
    ).filter(Personnel.is_deleted == 0).group_by(Personnel.department).all()
    
    personnel_by_department = {dept: count for dept, count in department_counts}
    
    # 计算设备状态分布
    status_counts = db.query(
        Equipment.status,
        func.count(Equipment.id).label('count')
    ).filter(Equipment.is_deleted == 0).group_by(Equipment.status).all()
    
    equipment_by_status = {status: count for status, count in status_counts}
    
    return ResourceOverview(
        total_personnel=total_personnel,
        total_equipment=total_equipment,
        allocated_personnel=allocated_personnel,
        allocated_equipment=allocated_equipment,
        idle_personnel=idle_personnel,
        idle_equipment=idle_equipment,
        personnel_by_department=personnel_by_department,
        equipment_by_status=equipment_by_status
    )

# 物料管理CRUD

def get_material_list(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    material_name: Optional[str] = None,
    supplier: Optional[str] = None
) -> List[Material]:
    """
    获取物料列表，支持分页、名称模糊查询和供应商过滤
    """
    query = db.query(Material).filter(Material.is_deleted == False)
    
    # 应用过滤条件
    if material_name:
        query = query.filter(Material.material_name.ilike(f"%{material_name}%"))
    if supplier:
        query = query.filter(Material.supplier == supplier)
    
    # 应用分页并获取结果
    return query.offset(skip).limit(limit).all()

def get_material(db: Session, material_id: str) -> Optional[Material]:
    """
    根据物料ID获取物料
    """
    return db.query(Material).filter(Material.material_id == material_id, Material.is_deleted == False).first()

def create_material(db: Session, material: MaterialCreate) -> Material:
    """
    创建新物料
    """
    db_material = Material(
        material_id=material.material_id,
        material_name=material.material_name,
        specification=material.specification,
        unit=material.unit,
        stock_quantity=material.stock_quantity,
        unit_price=material.unit_price,
        supplier=material.supplier
    )
    
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

def update_material(db: Session, material_id: str, material: MaterialUpdate) -> Optional[Material]:
    """
    更新物料信息
    """
    db_material = get_material(db, material_id=material_id)
    if db_material is None:
        return None
    
    # 获取更新数据
    update_data = material.model_dump(exclude_unset=True)
    
    # 更新字段
    for field, value in update_data.items():
        setattr(db_material, field, value)
    
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

def delete_material(db: Session, material_id: str) -> bool:
    """
    删除物料（软删除）
    """
    db_material = get_material(db, material_id=material_id)
    if db_material is None:
        return False
    
    db_material.is_deleted = True
    
    db.add(db_material)
    db.commit()
    return True

# 间接成本类型CRUD

def get_indirect_cost_type_list(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    type_name: Optional[str] = None
) -> List[IndirectCostType]:
    """
    获取间接成本类型列表，支持分页和名称模糊查询
    """
    query = db.query(IndirectCostType).filter(IndirectCostType.is_deleted == False)
    
    # 应用过滤条件
    if type_name:
        query = query.filter(IndirectCostType.type_name.ilike(f"%{type_name}%"))
    
    # 应用分页并获取结果
    return query.offset(skip).limit(limit).all()

def get_indirect_cost_type(db: Session, type_id: int) -> Optional[IndirectCostType]:
    """
    根据成本类型ID获取间接成本类型
    """
    return db.query(IndirectCostType).filter(IndirectCostType.id == type_id, IndirectCostType.is_deleted == False).first()

def create_indirect_cost_type(db: Session, cost_type: IndirectCostTypeCreate) -> IndirectCostType:
    """
    创建新间接成本类型
    """
    db_cost_type = IndirectCostType(
        type_name=cost_type.type_name,
        description=cost_type.description
    )
    
    db.add(db_cost_type)
    db.commit()
    db.refresh(db_cost_type)
    return db_cost_type

def update_indirect_cost_type(db: Session, type_id: int, cost_type: IndirectCostTypeUpdate) -> Optional[IndirectCostType]:
    """
    更新间接成本类型信息
    """
    db_cost_type = get_indirect_cost_type(db, type_id=type_id)
    if db_cost_type is None:
        return None
    
    # 获取更新数据
    update_data = cost_type.model_dump(exclude_unset=True)
    
    # 更新字段
    for field, value in update_data.items():
        setattr(db_cost_type, field, value)
    
    db.add(db_cost_type)
    db.commit()
    db.refresh(db_cost_type)
    return db_cost_type

def delete_indirect_cost_type(db: Session, type_id: int) -> bool:
    """
    删除间接成本类型（软删除）
    """
    db_cost_type = get_indirect_cost_type(db, type_id=type_id)
    if db_cost_type is None:
        return False
    
    db_cost_type.is_deleted = True
    
    db.add(db_cost_type)
    db.commit()
    return True

# 外包服务类型CRUD

def get_outsourcing_service_type_list(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    type_name: Optional[str] = None
) -> List[OutsourcingServiceType]:
    """
    获取外包服务类型列表，支持分页和名称模糊查询
    """
    query = db.query(OutsourcingServiceType).filter(OutsourcingServiceType.is_deleted == False)
    
    # 应用过滤条件
    if type_name:
        query = query.filter(OutsourcingServiceType.type_name.ilike(f"%{type_name}%"))
    
    # 应用分页并获取结果
    return query.offset(skip).limit(limit).all()

def get_outsourcing_service_type(db: Session, type_id: int) -> Optional[OutsourcingServiceType]:
    """
    根据服务类型ID获取外包服务类型
    """
    return db.query(OutsourcingServiceType).filter(OutsourcingServiceType.id == type_id, OutsourcingServiceType.is_deleted == False).first()

def create_outsourcing_service_type(db: Session, service_type: OutsourcingServiceTypeCreate) -> OutsourcingServiceType:
    """
    创建新外包服务类型
    """
    db_service_type = OutsourcingServiceType(
        type_name=service_type.type_name,
        description=service_type.description
    )
    
    db.add(db_service_type)
    db.commit()
    db.refresh(db_service_type)
    return db_service_type

def update_outsourcing_service_type(db: Session, type_id: int, service_type: OutsourcingServiceTypeUpdate) -> Optional[OutsourcingServiceType]:
    """
    更新外包服务类型信息
    """
    db_service_type = get_outsourcing_service_type(db, type_id=type_id)
    if db_service_type is None:
        return None
    
    # 获取更新数据
    update_data = service_type.model_dump(exclude_unset=True)
    
    # 更新字段
    for field, value in update_data.items():
        setattr(db_service_type, field, value)
    
    db.add(db_service_type)
    db.commit()
    db.refresh(db_service_type)
    return db_service_type

def delete_outsourcing_service_type(db: Session, type_id: int) -> bool:
    """
    删除外包服务类型（软删除）
    """
    db_service_type = get_outsourcing_service_type(db, type_id=type_id)
    if db_service_type is None:
        return False
    
    db_service_type.is_deleted = True
    
    db.add(db_service_type)
    db.commit()
    return True