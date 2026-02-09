from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import date
from app.models.project import Project
from app.models.material_cost import MaterialCost
from app.models.outsourcing_cost import OutsourcingCost
from app.models.indirect_cost import IndirectCost
from app.models.labor_cost import LaborCost
from app.schemas.cost_analysis import (
    MaterialCostCreate,
    MaterialCostUpdate,
    OutsourcingCostCreate,
    OutsourcingCostUpdate,
    IndirectCostCreate,
    IndirectCostUpdate,
    LaborCostCreate,
    LaborCostUpdate
)

# 物料成本CRUD

def get_material_costs(
    db: Session,
    project_id: int,
    skip: int = 0,
    limit: int = 10
) -> List[MaterialCost]:
    """
    获取项目的物料成本列表
    """
    return db.query(MaterialCost)
        .filter(MaterialCost.project_id == project_id, MaterialCost.is_deleted == 0)
        .offset(skip)
        .limit(limit)
        .all()

def get_material_cost(db: Session, cost_id: int) -> Optional[MaterialCost]:
    """
    根据成本ID获取物料成本
    """
    return db.query(MaterialCost).filter(MaterialCost.id == cost_id, MaterialCost.is_deleted == 0).first()

def create_material_cost(db: Session, cost: MaterialCostCreate) -> MaterialCost:
    """
    创建物料成本记录
    """
    # 计算总金额
    total_amount = cost.quantity * cost.unit_price
    
    db_cost = MaterialCost(
        project_id=cost.project_id,
        material_name=cost.material_name,
        specification=cost.specification,
        unit=cost.unit,
        quantity=cost.quantity,
        unit_price=cost.unit_price,
        total_amount=total_amount,
        cost_date=cost.cost_date or date.today(),
        supplier_id=cost.supplier_id,
        supplier_name=cost.supplier_name,
        remark=cost.remark,
        create_time=date.today(),
        update_time=date.today()
    )
    
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    
    # 更新项目的实际物料成本
    update_project_material_actual(db, cost.project_id)
    
    return db_cost

def update_material_cost(db: Session, cost_id: int, cost: MaterialCostUpdate) -> Optional[MaterialCost]:
    """
    更新物料成本记录
    """
    db_cost = get_material_cost(db, cost_id=cost_id)
    if db_cost is None:
        return None
    
    # 更新成本记录
    update_data = cost.model_dump(exclude_unset=True)
    
    # 如果更新了数量或单价，重新计算总金额
    if "quantity" in update_data or "unit_price" in update_data:
        quantity = update_data.get("quantity", db_cost.quantity)
        unit_price = update_data.get("unit_price", db_cost.unit_price)
        update_data["total_amount"] = quantity * unit_price
    
    # 更新字段
    for field, value in update_data.items():
        setattr(db_cost, field, value)
    
    db_cost.update_time = date.today()
    
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    
    # 更新项目的实际物料成本
    update_project_material_actual(db, db_cost.project_id)
    
    return db_cost

def delete_material_cost(db: Session, cost_id: int) -> bool:
    """
    删除物料成本记录
    """
    db_cost = get_material_cost(db, cost_id=cost_id)
    if db_cost is None:
        return False
    
    project_id = db_cost.project_id
    db_cost.is_deleted = 1
    db_cost.update_time = date.today()
    
    db.add(db_cost)
    db.commit()
    
    # 更新项目的实际物料成本
    update_project_material_actual(db, project_id)
    
    return True

# 外包成本CRUD

def get_outsourcing_costs(
    db: Session,
    project_id: int,
    skip: int = 0,
    limit: int = 10
) -> List[OutsourcingCost]:
    """
    获取项目的外包成本列表
    """
    return db.query(OutsourcingCost)
        .filter(OutsourcingCost.project_id == project_id, OutsourcingCost.is_deleted == 0)
        .offset(skip)
        .limit(limit)
        .all()

def get_outsourcing_cost(db: Session, cost_id: int) -> Optional[OutsourcingCost]:
    """
    根据成本ID获取外包成本
    """
    return db.query(OutsourcingCost).filter(OutsourcingCost.id == cost_id, OutsourcingCost.is_deleted == 0).first()

def create_outsourcing_cost(db: Session, cost: OutsourcingCostCreate) -> OutsourcingCost:
    """
    创建外包成本记录
    """
    db_cost = OutsourcingCost(
        project_id=cost.project_id,
        outsourcing_type=cost.outsourcing_type,
        service_name=cost.service_name,
        service_content=cost.service_content,
        amount=cost.amount,
        cost_date=cost.cost_date or date.today(),
        supplier_id=cost.supplier_id,
        supplier_name=cost.supplier_name,
        remark=cost.remark,
        create_time=date.today(),
        update_time=date.today()
    )
    
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    
    # 更新项目的实际外包成本
    update_project_outsourcing_actual(db, cost.project_id)
    
    return db_cost

def update_outsourcing_cost(db: Session, cost_id: int, cost: OutsourcingCostUpdate) -> Optional[OutsourcingCost]:
    """
    更新外包成本记录
    """
    db_cost = get_outsourcing_cost(db, cost_id=cost_id)
    if db_cost is None:
        return None
    
    # 更新成本记录
    update_data = cost.model_dump(exclude_unset=True)
    
    # 更新字段
    for field, value in update_data.items():
        setattr(db_cost, field, value)
    
    db_cost.update_time = date.today()
    
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    
    # 更新项目的实际外包成本
    update_project_outsourcing_actual(db, db_cost.project_id)
    
    return db_cost

def delete_outsourcing_cost(db: Session, cost_id: int) -> bool:
    """
    删除外包成本记录
    """
    db_cost = get_outsourcing_cost(db, cost_id=cost_id)
    if db_cost is None:
        return False
    
    project_id = db_cost.project_id
    db_cost.is_deleted = 1
    db_cost.update_time = date.today()
    
    db.add(db_cost)
    db.commit()
    
    # 更新项目的实际外包成本
    update_project_outsourcing_actual(db, project_id)
    
    return True

# 间接成本CRUD

def get_indirect_costs(
    db: Session,
    project_id: int,
    skip: int = 0,
    limit: int = 10
) -> List[IndirectCost]:
    """
    获取项目的间接成本列表
    """
    return db.query(IndirectCost)
        .filter(IndirectCost.project_id == project_id, IndirectCost.is_deleted == 0)
        .offset(skip)
        .limit(limit)
        .all()

def get_indirect_cost(db: Session, cost_id: int) -> Optional[IndirectCost]:
    """
    根据成本ID获取间接成本
    """
    return db.query(IndirectCost).filter(IndirectCost.id == cost_id, IndirectCost.is_deleted == 0).first()

def create_indirect_cost(db: Session, cost: IndirectCostCreate) -> IndirectCost:
    """
    创建间接成本记录
    """
    db_cost = IndirectCost(
        project_id=cost.project_id,
        cost_type=cost.cost_type,
        cost_name=cost.cost_name,
        amount=cost.amount,
        cost_date=cost.cost_date or date.today(),
        remark=cost.remark,
        create_time=date.today(),
        update_time=date.today()
    )
    
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    
    # 更新项目的实际间接成本
    update_project_indirect_actual(db, cost.project_id)
    
    return db_cost

def update_indirect_cost(db: Session, cost_id: int, cost: IndirectCostUpdate) -> Optional[IndirectCost]:
    """
    更新间接成本记录
    """
    db_cost = get_indirect_cost(db, cost_id=cost_id)
    if db_cost is None:
        return None
    
    # 更新成本记录
    update_data = cost.model_dump(exclude_unset=True)
    
    # 更新字段
    for field, value in update_data.items():
        setattr(db_cost, field, value)
    
    db_cost.update_time = date.today()
    
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    
    # 更新项目的实际间接成本
    update_project_indirect_actual(db, db_cost.project_id)
    
    return db_cost

def delete_indirect_cost(db: Session, cost_id: int) -> bool:
    """
    删除间接成本记录
    """
    db_cost = get_indirect_cost(db, cost_id=cost_id)
    if db_cost is None:
        return False
    
    project_id = db_cost.project_id
    db_cost.is_deleted = 1
    db_cost.update_time = date.today()
    
    db.add(db_cost)
    db.commit()
    
    # 更新项目的实际间接成本
    update_project_indirect_actual(db, project_id)
    
    return True

# 人力成本CRUD

def get_labor_costs(
    db: Session,
    project_id: int,
    skip: int = 0,
    limit: int = 10
) -> List[LaborCost]:
    """
    获取项目的人力成本列表
    """
    return db.query(LaborCost)
        .filter(LaborCost.project_id == project_id, LaborCost.is_deleted == 0)
        .offset(skip)
        .limit(limit)
        .all()

def get_labor_cost(db: Session, cost_id: int) -> Optional[LaborCost]:
    """
    根据成本ID获取人力成本
    """
    return db.query(LaborCost).filter(LaborCost.id == cost_id, LaborCost.is_deleted == 0).first()

def create_labor_cost(db: Session, cost: LaborCostCreate) -> LaborCost:
    """
    创建人力成本记录
    """
    # 计算总金额
    total_amount = cost.work_hours * cost.hourly_rate
    
    db_cost = LaborCost(
        project_id=cost.project_id,
        personnel_id=cost.personnel_id,
        personnel_name=cost.personnel_name,
        department=cost.department,
        position=cost.position,
        work_hours=cost.work_hours,
        hourly_rate=cost.hourly_rate,
        total_amount=total_amount,
        work_date=cost.work_date or date.today(),
        work_content=cost.work_content,
        remark=cost.remark,
        create_time=date.today(),
        update_time=date.today()
    )
    
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    
    # 更新项目的实际人力成本
    update_project_labor_actual(db, cost.project_id)
    
    return db_cost

def update_labor_cost(db: Session, cost_id: int, cost: LaborCostUpdate) -> Optional[LaborCost]:
    """
    更新人力成本记录
    """
    db_cost = get_labor_cost(db, cost_id=cost_id)
    if db_cost is None:
        return None
    
    # 更新成本记录
    update_data = cost.model_dump(exclude_unset=True)
    
    # 如果更新了工时或小时费率，重新计算总金额
    if "work_hours" in update_data or "hourly_rate" in update_data:
        work_hours = update_data.get("work_hours", db_cost.work_hours)
        hourly_rate = update_data.get("hourly_rate", db_cost.hourly_rate)
        update_data["total_amount"] = work_hours * hourly_rate
    
    # 更新字段
    for field, value in update_data.items():
        setattr(db_cost, field, value)
    
    db_cost.update_time = date.today()
    
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    
    # 更新项目的实际人力成本
    update_project_labor_actual(db, db_cost.project_id)
    
    return db_cost

def delete_labor_cost(db: Session, cost_id: int) -> bool:
    """
    删除人力成本记录
    """
    db_cost = get_labor_cost(db, cost_id=cost_id)
    if db_cost is None:
        return False
    
    project_id = db_cost.project_id
    db_cost.is_deleted = 1
    db_cost.update_time = date.today()
    
    db.add(db_cost)
    db.commit()
    
    # 更新项目的实际人力成本
    update_project_labor_actual(db, project_id)
    
    return True

# 辅助函数：更新项目的实际成本

def update_project_cost_summary(db: Session, project_id: int) -> None:
    """
    更新项目的成本汇总信息
    """
    # 计算各成本类型的总实际成本
    total_material_cost = db.query(func.sum(MaterialCost.total_amount))
        .filter(MaterialCost.project_id == project_id, MaterialCost.is_deleted == 0)
        .scalar() or 0
    
    total_labor_cost = db.query(func.sum(LaborCost.total_amount))
        .filter(LaborCost.project_id == project_id, LaborCost.is_deleted == 0)
        .scalar() or 0
    
    total_outsourcing_cost = db.query(func.sum(OutsourcingCost.amount))
        .filter(OutsourcingCost.project_id == project_id, OutsourcingCost.is_deleted == 0)
        .scalar() or 0
    
    total_indirect_cost = db.query(func.sum(IndirectCost.amount))
        .filter(IndirectCost.project_id == project_id, IndirectCost.is_deleted == 0)
        .scalar() or 0
    
    total_actual_cost = total_material_cost + total_labor_cost + total_outsourcing_cost + total_indirect_cost
    
    # 更新Project表中的各成本字段
    db.query(Project)
        .filter(Project.id == project_id)
        .update({
            Project.material_actual: total_material_cost,
            Project.labor_actual: total_labor_cost,
            Project.outsourcing_actual: total_outsourcing_cost,
            Project.indirect_actual: total_indirect_cost,
            Project.actual_total_cost: total_actual_cost,
            Project.updated_at: func.now()
        })
    
    db.commit()

# 保留原有函数名，但内部调用新函数，确保向后兼容
def update_project_material_actual(db: Session, project_id: int) -> None:
    """
    更新项目的实际物料成本
    """
    update_project_cost_summary(db, project_id)

def update_project_outsourcing_actual(db: Session, project_id: int) -> None:
    """
    更新项目的实际外包成本
    """
    update_project_cost_summary(db, project_id)

def update_project_indirect_actual(db: Session, project_id: int) -> None:
    """
    更新项目的实际间接成本
    """
    update_project_cost_summary(db, project_id)

def update_project_labor_actual(db: Session, project_id: int) -> None:
    """
    更新项目的实际人力成本
    """
    update_project_cost_summary(db, project_id)

# 批量创建成本记录函数

def batch_create_material_costs(db: Session, costs: List[dict]) -> List[MaterialCost]:
    """
    批量创建物料成本记录
    """
    created_costs = []
    for cost_data in costs:
        # 创建物料成本对象
        cost_create = MaterialCostCreate(**cost_data)
        created_cost = create_material_cost(db, cost_create)
        created_costs.append(created_cost)
    return created_costs

def batch_create_labor_costs(db: Session, costs: List[dict]) -> List[LaborCost]:
    """
    批量创建人力成本记录
    """
    created_costs = []
    for cost_data in costs:
        # 创建人力成本对象
        cost_create = LaborCostCreate(**cost_data)
        created_cost = create_labor_cost(db, cost_create)
        created_costs.append(created_cost)
    return created_costs

def batch_create_outsourcing_costs(db: Session, costs: List[dict]) -> List[OutsourcingCost]:
    """
    批量创建外包成本记录
    """
    created_costs = []
    for cost_data in costs:
        # 创建外包成本对象
        cost_create = OutsourcingCostCreate(**cost_data)
        created_cost = create_outsourcing_cost(db, cost_create)
        created_costs.append(created_cost)
    return created_costs

def batch_create_indirect_costs(db: Session, costs: List[dict]) -> List[IndirectCost]:
    """
    批量创建间接成本记录
    """
    created_costs = []
    for cost_data in costs:
        # 创建间接成本对象
        cost_create = IndirectCostCreate(**cost_data)
        created_cost = create_indirect_cost(db, cost_create)
        created_costs.append(created_cost)
    return created_costs

# 成本分析辅助函数

def get_project_cost_overview(db: Session, project_id: int) -> Dict[str, Any]:
    """
    获取项目成本概览
    """
    project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
    if not project:
        return {}
    
    # 计算预算执行率
    budget_execution_rate = 0
    if project.budget > 0:
        budget_execution_rate = (project.actual_cost / project.budget) * 100
    
    return {
        "project_id": project.id,
        "project_name": project.name,
        "total_budget": project.budget,
        "total_actual": project.actual_cost,
        "remaining_budget": project.budget - project.actual_cost,
        "budget_execution_rate": round(budget_execution_rate, 2),
        "material_budget": project.material_budget,
        "material_actual": project.material_actual,
        "outsourcing_budget": project.outsourcing_budget,
        "outsourcing_actual": project.outsourcing_actual,
        "indirect_budget": project.indirect_budget,
        "indirect_actual": project.indirect_actual,
        "labor_budget": project.labor_budget,
        "labor_actual": project.labor_actual
    }
