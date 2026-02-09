from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer, String
from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from app.core.dependencies import get_db
from app.models.material_cost import MaterialCost
from app.models.labor_cost import LaborCost
from app.models.outsourcing_cost import OutsourcingCost
from app.models.indirect_cost import IndirectCost
from app.models.project import Project
from app.models.resource import Personnel
from app.schemas.cost import (
    MaterialCostCreate, 
    MaterialCostUpdate, 
    MaterialCostResponse,
    LaborCostCreate, 
    LaborCostUpdate, 
    LaborCostResponse,
    OutsourcingCostCreate, 
    OutsourcingCostUpdate, 
    OutsourcingCostResponse,
    IndirectCostCreate, 
    IndirectCostUpdate, 
    IndirectCostResponse
)

router = APIRouter()


def format_datetime(dt):
    """格式化日期时间为 年/月/日 时:分:秒 格式"""
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    return dt.strftime("%Y/%m/%d %H:%M:%S")


# 物料成本相关API
@router.get("/material", response_model=List[MaterialCostResponse])
def get_material_costs(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    project_id: Optional[int] = None
):
    """获取物料成本列表"""
    query = db.query(MaterialCost).filter(MaterialCost.is_deleted == False)
    
    if project_id:
        query = query.filter(MaterialCost.project_id == project_id)
    
    costs = query.offset(skip).limit(limit).all()
    return costs


@router.post("/material", response_model=MaterialCostResponse)
def create_material_cost(cost: MaterialCostCreate, db: Session = Depends(get_db)):
    """创建物料成本"""
    db_cost = MaterialCost(**cost.dict())
    db_cost.total_cost = db_cost.quantity * db_cost.unit_price
    db_cost.actual_total_cost = db_cost.actual_quantity * db_cost.actual_unit_price
    
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    
    # 更新项目成本汇总
    update_project_costs(db, db_cost.project_id)
    
    return db_cost


@router.put("/material/{cost_id}", response_model=MaterialCostResponse)
def update_material_cost(cost_id: int, cost: MaterialCostUpdate, db: Session = Depends(get_db)):
    """更新物料成本"""
    db_cost = db.query(MaterialCost).filter(MaterialCost.id == cost_id, MaterialCost.is_deleted == False).first()
    if not db_cost:
        raise HTTPException(status_code=404, detail="物料成本记录未找到")
    
    update_data = cost.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cost, field, value)
    
    # 重新计算成本
    db_cost.total_cost = db_cost.quantity * db_cost.unit_price
    db_cost.actual_total_cost = db_cost.actual_quantity * db_cost.actual_unit_price
    
    db.commit()
    db.refresh(db_cost)
    
    # 更新项目成本汇总
    update_project_costs(db, db_cost.project_id)
    
    return db_cost


@router.delete("/material/{cost_id}")
def delete_material_cost(cost_id: int, db: Session = Depends(get_db)):
    """删除物料成本"""
    db_cost = db.query(MaterialCost).filter(MaterialCost.id == cost_id, MaterialCost.is_deleted == False).first()
    if not db_cost:
        raise HTTPException(status_code=404, detail="物料成本记录未找到")
    
    project_id = db_cost.project_id
    
    # 软删除
    db_cost.is_deleted = True
    db.commit()
    
    # 更新项目成本汇总
    update_project_costs(db, project_id)
    
    return {"message": "物料成本记录已删除"}


# 人力成本相关API
@router.get("/labor", response_model=List[LaborCostResponse])
def get_labor_costs(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    project_id: Optional[int] = None
):
    """获取人力成本列表"""
    query = db.query(LaborCost).filter(LaborCost.is_deleted == False)
    
    if project_id:
        query = query.filter(LaborCost.project_id == project_id)
    
    costs = query.offset(skip).limit(limit).all()
    return costs


@router.post("/labor", response_model=LaborCostResponse)
def create_labor_cost(cost: LaborCostCreate, db: Session = Depends(get_db)):
    """创建人力成本"""
    db_cost = LaborCost(**cost.dict())
    db_cost.total_cost = db_cost.hours * db_cost.rate_per_hour
    db_cost.actual_total_cost = db_cost.actual_hours * db_cost.actual_rate_per_hour
    
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    
    # 更新项目成本汇总
    update_project_costs(db, db_cost.project_id)
    
    return db_cost


@router.put("/labor/{cost_id}", response_model=LaborCostResponse)
def update_labor_cost(cost_id: int, cost: LaborCostUpdate, db: Session = Depends(get_db)):
    """更新人力成本"""
    db_cost = db.query(LaborCost).filter(LaborCost.id == cost_id, LaborCost.is_deleted == False).first()
    if not db_cost:
        raise HTTPException(status_code=404, detail="人力成本记录未找到")
    
    update_data = cost.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cost, field, value)
    
    # 重新计算成本
    db_cost.total_cost = db_cost.hours * db_cost.rate_per_hour
    db_cost.actual_total_cost = db_cost.actual_hours * db_cost.actual_rate_per_hour
    
    db.commit()
    db.refresh(db_cost)
    
    # 更新项目成本汇总
    update_project_costs(db, db_cost.project_id)
    
    return db_cost


@router.delete("/labor/{cost_id}")
def delete_labor_cost(cost_id: int, db: Session = Depends(get_db)):
    """删除人力成本"""
    db_cost = db.query(LaborCost).filter(LaborCost.id == cost_id, LaborCost.is_deleted == False).first()
    if not db_cost:
        raise HTTPException(status_code=404, detail="人力成本记录未找到")
    
    project_id = db_cost.project_id
    
    # 软删除
    db_cost.is_deleted = True
    db.commit()
    
    # 更新项目成本汇总
    update_project_costs(db, project_id)
    
    return {"message": "人力成本记录已删除"}


# 外包成本相关API
@router.get("/outsourcing", response_model=List[OutsourcingCostResponse])
def get_outsourcing_costs(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    project_id: Optional[int] = None
):
    """获取外包成本列表"""
    query = db.query(OutsourcingCost).filter(OutsourcingCost.is_deleted == False)
    
    if project_id:
        query = query.filter(OutsourcingCost.project_id == project_id)
    
    costs = query.offset(skip).limit(limit).all()
    return costs


@router.post("/outsourcing", response_model=OutsourcingCostResponse)
def create_outsourcing_cost(cost: OutsourcingCostCreate, db: Session = Depends(get_db)):
    """创建外包成本"""
    db_cost = OutsourcingCost(**cost.dict())
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    
    # 更新项目成本汇总
    update_project_costs(db, db_cost.project_id)
    
    return db_cost


@router.put("/outsourcing/{cost_id}", response_model=OutsourcingCostResponse)
def update_outsourcing_cost(cost_id: int, cost: OutsourcingCostUpdate, db: Session = Depends(get_db)):
    """更新外包成本"""
    db_cost = db.query(OutsourcingCost).filter(OutsourcingCost.id == cost_id, OutsourcingCost.is_deleted == False).first()
    if not db_cost:
        raise HTTPException(status_code=404, detail="外包成本记录未找到")
    
    update_data = cost.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cost, field, value)
    
    db.commit()
    db.refresh(db_cost)
    
    # 更新项目成本汇总
    update_project_costs(db, db_cost.project_id)
    
    return db_cost


@router.delete("/outsourcing/{cost_id}")
def delete_outsourcing_cost(cost_id: int, db: Session = Depends(get_db)):
    """删除外包成本"""
    db_cost = db.query(OutsourcingCost).filter(OutsourcingCost.id == cost_id, OutsourcingCost.is_deleted == False).first()
    if not db_cost:
        raise HTTPException(status_code=404, detail="外包成本记录未找到")
    
    project_id = db_cost.project_id
    
    # 软删除
    db_cost.is_deleted = True
    db.commit()
    
    # 更新项目成本汇总
    update_project_costs(db, project_id)
    
    return {"message": "外包成本记录已删除"}


# 间接成本相关API
@router.get("/indirect", response_model=List[IndirectCostResponse])
def get_indirect_costs(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    project_id: Optional[int] = None
):
    """获取间接成本列表"""
    query = db.query(IndirectCost).filter(IndirectCost.is_deleted == False)
    
    if project_id:
        query = query.filter(IndirectCost.project_id == project_id)
    
    costs = query.offset(skip).limit(limit).all()
    return costs


@router.post("/indirect", response_model=IndirectCostResponse)
def create_indirect_cost(cost: IndirectCostCreate, db: Session = Depends(get_db)):
    """创建间接成本"""
    db_cost = IndirectCost(**cost.dict())
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    
    # 更新项目成本汇总
    update_project_costs(db, db_cost.project_id)
    
    return db_cost


@router.put("/indirect/{cost_id}", response_model=IndirectCostResponse)
def update_indirect_cost(cost_id: int, cost: IndirectCostUpdate, db: Session = Depends(get_db)):
    """更新间接成本"""
    db_cost = db.query(IndirectCost).filter(IndirectCost.id == cost_id, IndirectCost.is_deleted == False).first()
    if not db_cost:
        raise HTTPException(status_code=404, detail="间接成本记录未找到")
    
    update_data = cost.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cost, field, value)
    
    db.commit()
    db.refresh(db_cost)
    
    # 更新项目成本汇总
    update_project_costs(db, db_cost.project_id)
    
    return db_cost


@router.delete("/indirect/{cost_id}")
def delete_indirect_cost(cost_id: int, db: Session = Depends(get_db)):
    """删除间接成本"""
    db_cost = db.query(IndirectCost).filter(IndirectCost.id == cost_id, IndirectCost.is_deleted == False).first()
    if not db_cost:
        raise HTTPException(status_code=404, detail="间接成本记录未找到")
    
    project_id = db_cost.project_id
    
    # 软删除
    db_cost.is_deleted = True
    db.commit()
    
    # 更新项目成本汇总
    update_project_costs(db, project_id)
    
    return {"message": "间接成本记录已删除"}


# 批量创建成本记录API
@router.post("/material/batch", status_code=201)
def batch_create_material_costs(
    costs: List[dict],
    db: Session = Depends(get_db)
):
    """批量创建物料成本记录"""
    created_costs = []
    project_ids = set()
    
    try:
        for cost in costs:
            if "project_id" not in cost or not cost["project_id"]:
                continue
            if "material_id" not in cost or not cost["material_id"]:
                continue
            if "name" not in cost or not cost["name"]:
                continue
            
            db_cost = MaterialCost(**cost)
            db.add(db_cost)
            created_costs.append(db_cost)
            project_ids.add(cost["project_id"])
        
        db.commit()
        
        for project_id in project_ids:
            update_project_costs(db, project_id)
        
        return {"message": "物料成本记录创建成功", "count": len(created_costs)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"物料成本记录创建失败: {str(e)}")


@router.post("/labor/batch", status_code=201)
def batch_create_labor_costs(
    costs: List[dict],
    db: Session = Depends(get_db)
):
    """批量创建人力成本记录"""
    created_costs = []
    project_ids = set()
    
    try:
        for cost in costs:
            if "employee_id" not in cost or not cost["employee_id"]:
                continue
            if "project_id" not in cost or not cost["project_id"]:
                continue
            
            db_cost = LaborCost(**cost)
            db.add(db_cost)
            created_costs.append(db_cost)
            project_ids.add(cost["project_id"])
        
        db.commit()
        
        for project_id in project_ids:
            update_project_costs(db, project_id)
        
        return {"message": "人力成本记录创建成功", "count": len(created_costs)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"人力成本记录创建失败: {str(e)}")


@router.post("/outsourcing/batch", status_code=201)
def batch_create_outsourcing_costs(
    costs: List[dict],
    db: Session = Depends(get_db)
):
    """批量创建外包成本记录"""
    created_costs = []
    project_ids = set()
    
    try:
        for cost in costs:
            if "project_id" not in cost or not cost["project_id"]:
                continue
            if "service_type" not in cost or not cost["service_type"]:
                continue
            
            db_cost = OutsourcingCost(**cost)
            db.add(db_cost)
            created_costs.append(db_cost)
            project_ids.add(cost["project_id"])
        
        db.commit()
        
        for project_id in project_ids:
            update_project_costs(db, project_id)
        
        return {"message": "外包成本记录创建成功", "count": len(created_costs)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"外包成本记录创建失败: {str(e)}")


@router.post("/indirect/batch", status_code=201)
def batch_create_indirect_costs(
    costs: List[dict],
    db: Session = Depends(get_db)
):
    """批量创建间接成本记录"""
    created_costs = []
    project_ids = set()
    
    try:
        for cost in costs:
            if "project_id" not in cost or not cost["project_id"]:
                continue
            if "cost_type" not in cost or not cost["cost_type"]:
                continue
            
            db_cost = IndirectCost(**cost)
            db.add(db_cost)
            created_costs.append(db_cost)
            project_ids.add(cost["project_id"])
        
        db.commit()
        
        for project_id in project_ids:
            update_project_costs(db, project_id)
        
        return {"message": "间接成本记录创建成功", "count": len(created_costs)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"间接成本记录创建失败: {str(e)}")


@router.get("/labor/workload")
def get_employee_workload(db: Session = Depends(get_db)):
    """获取人员工作量分布"""
    try:
        result = db.query(
            Personnel.name,
            func.sum(LaborCost.actual_hours).label('actual_hours')
        ).join(
            Personnel, 
            func.cast(Personnel.id, String) == LaborCost.employee_id
        ).filter(
            LaborCost.is_deleted == False,
            Personnel.is_deleted == False
        ).group_by(
            Personnel.id, Personnel.name
        ).order_by(
            Personnel.name
        ).all()
        
        workload_data = []
        for row in result:
            workload_data.append({
                "name": row.name,
                "actual_hours": float(row.actual_hours) if row.actual_hours else 0.0
            })
        
        return {"code": 200, "data": workload_data, "message": "获取人员工作量成功"}
    except Exception as e:
        return {"code": 500, "data": [], "message": f"获取人员工作量失败: {str(e)}"}


def update_project_costs(db: Session, project_id: Union[int, str]):
    """更新项目成本汇总"""
    try:
        project_id_int = int(project_id)
        
        project = db.query(Project).filter(Project.id == project_id_int).first()
        if not project:
            return
        
        project_id_str = str(project_id_int)
        
        material_budget = float(db.query(func.sum(MaterialCost.total_price)).filter(
            MaterialCost.project_id == project_id_str,
            MaterialCost.is_deleted == False,
            MaterialCost.cost_type == '预算'
        ).scalar() or 0.0)
        
        material_actual = float(db.query(func.sum(MaterialCost.total_price)).filter(
            MaterialCost.project_id == project_id_str,
            MaterialCost.is_deleted == False,
            MaterialCost.cost_type == '实际'
        ).scalar() or 0.0)
        
        outsourcing_budget = float(db.query(func.sum(OutsourcingCost.total_price)).filter(
            OutsourcingCost.project_id == project_id_str,
            OutsourcingCost.is_deleted == False,
            OutsourcingCost.cost_type == '预算'
        ).scalar() or 0.0)
        
        outsourcing_actual = float(db.query(func.sum(OutsourcingCost.total_price)).filter(
            OutsourcingCost.project_id == project_id_str,
            OutsourcingCost.is_deleted == False,
            OutsourcingCost.cost_type == '实际'
        ).scalar() or 0.0)
        
        indirect_budget = float(db.query(func.sum(IndirectCost.total_price)).filter(
            IndirectCost.project_id == project_id_str,
            IndirectCost.is_deleted == False,
            IndirectCost.cost_type_flag == '预算'
        ).scalar() or 0.0)
        
        indirect_actual = float(db.query(func.sum(IndirectCost.total_price)).filter(
            IndirectCost.project_id == project_id_str,
            IndirectCost.is_deleted == False,
            IndirectCost.cost_type_flag == '实际'
        ).scalar() or 0.0)
        
        labor_budget = float(db.query(func.sum(LaborCost.budget_cost)).filter(
            LaborCost.project_id == project_id_str,
            LaborCost.is_deleted == False
        ).scalar() or 0.0)
        
        labor_actual = float(db.query(func.sum(LaborCost.actual_cost)).filter(
            LaborCost.project_id == project_id_str,
            LaborCost.is_deleted == False
        ).scalar() or 0.0)
        
        budget_total_cost = material_budget + outsourcing_budget + indirect_budget + labor_budget
        actual_total_cost = material_actual + outsourcing_actual + indirect_actual + labor_actual
        
        project.material_budget = float(material_budget)
        project.material_actual = float(material_actual)
        project.outsourcing_budget = float(outsourcing_budget)
        project.outsourcing_actual = float(outsourcing_actual)
        project.indirect_budget = float(indirect_budget)
        project.indirect_actual = float(indirect_actual)
        project.labor_budget = float(labor_budget)
        project.labor_actual = float(labor_actual)
        project.budget_total_cost = float(budget_total_cost)
        project.actual_total_cost = float(actual_total_cost)
        
        db.commit()
    except Exception as e:
        db.rollback()


# 成本分析综合API

@router.get("/analysis/overview")
def get_cost_overview(
    project_id: Optional[int] = Query(None, description="项目ID，不传则返回所有项目概览"),
    db: Session = Depends(get_db)
):
    """获取项目成本概览"""
    try:
        if project_id:
            project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
            if not project:
                return {"code": 404, "data": None, "message": "项目不存在"}
            
            budget_execution_rate = 0.0
            if project.budget_total_cost and project.budget_total_cost > 0:
                budget_execution_rate = round((project.actual_total_cost / project.budget_total_cost) * 100, 2)
            
            return {
                "code": 200,
                "data": {
                    "project_id": project.id,
                    "project_name": project.name,
                    "total_budget": float(project.budget_total_cost or 0),
                    "total_actual": float(project.actual_total_cost or 0),
                    "remaining_budget": float((project.budget_total_cost or 0) - (project.actual_total_cost or 0)),
                    "budget_execution_rate": budget_execution_rate,
                    "material_budget": float(project.material_budget or 0),
                    "material_actual": float(project.material_actual or 0),
                    "outsourcing_budget": float(project.outsourcing_budget or 0),
                    "outsourcing_actual": float(project.outsourcing_actual or 0),
                    "indirect_budget": float(project.indirect_budget or 0),
                    "indirect_actual": float(project.indirect_actual or 0),
                    "labor_budget": float(project.labor_budget or 0),
                    "labor_actual": float(project.labor_actual or 0)
                },
                "message": "获取成本概览成功"
            }
        else:
            projects = db.query(Project).filter(Project.is_deleted == False).all()
            overview_list = []
            for project in projects:
                budget_execution_rate = 0.0
                if project.budget_total_cost and project.budget_total_cost > 0:
                    budget_execution_rate = round((project.actual_total_cost / project.budget_total_cost) * 100, 2)
                
                overview_list.append({
                    "project_id": project.id,
                    "project_name": project.name,
                    "total_budget": float(project.budget_total_cost or 0),
                    "total_actual": float(project.actual_total_cost or 0),
                    "remaining_budget": float((project.budget_total_cost or 0) - (project.actual_total_cost or 0)),
                    "budget_execution_rate": budget_execution_rate,
                    "material_actual": float(project.material_actual or 0),
                    "outsourcing_actual": float(project.outsourcing_actual or 0),
                    "indirect_actual": float(project.indirect_actual or 0),
                    "labor_actual": float(project.labor_actual or 0)
                })
            
            return {
                "code": 200,
                "data": overview_list,
                "message": "获取所有项目成本概览成功"
            }
    except Exception as e:
        return {"code": 500, "data": None, "message": f"获取成本概览失败: {str(e)}"}


@router.get("/analysis/category")
def get_cost_by_category(
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    """按分类获取成本明细"""
    try:
        project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
        if not project:
            return {"code": 404, "data": None, "message": "项目不存在"}
        
        material_costs = db.query(MaterialCost).filter(
            MaterialCost.project_id == str(project_id),
            MaterialCost.is_deleted == False
        ).all()
        
        labor_costs = db.query(LaborCost).filter(
            LaborCost.project_id == str(project_id),
            LaborCost.is_deleted == False
        ).all()
        
        outsourcing_costs = db.query(OutsourcingCost).filter(
            OutsourcingCost.project_id == str(project_id),
            OutsourcingCost.is_deleted == False
        ).all()
        
        indirect_costs = db.query(IndirectCost).filter(
            IndirectCost.project_id == str(project_id),
            IndirectCost.is_deleted == False
        ).all()
        
        def cost_to_dict(cost, cost_type):
            return {
                "id": cost.cost_id if hasattr(cost, 'cost_id') else cost.id,
                "cost_type": cost_type,
                "amount": float(cost.total_price if hasattr(cost, 'total_price') else (cost.actual_cost if hasattr(cost, 'actual_cost') else cost.amount)),
                "date": format_datetime(cost.create_time),
                "description": getattr(cost, 'remark', None) or getattr(cost, 'description', None),
                "create_time": format_datetime(cost.create_time)
            }
        
        details = []
        for cost in material_costs:
            details.append(cost_to_dict(cost, "物料成本"))
        for cost in labor_costs:
            details.append(cost_to_dict(cost, "人力成本"))
        for cost in outsourcing_costs:
            details.append(cost_to_dict(cost, "外包成本"))
        for cost in indirect_costs:
            details.append(cost_to_dict(cost, "间接成本"))
        
        category_summary = {
            "material": {
                "budget": float(project.material_budget or 0),
                "actual": float(project.material_actual or 0),
                "count": len(material_costs)
            },
            "labor": {
                "budget": float(project.labor_budget or 0),
                "actual": float(project.labor_actual or 0),
                "count": len(labor_costs)
            },
            "outsourcing": {
                "budget": float(project.outsourcing_budget or 0),
                "actual": float(project.outsourcing_actual or 0),
                "count": len(outsourcing_costs)
            },
            "indirect": {
                "budget": float(project.indirect_budget or 0),
                "actual": float(project.indirect_actual or 0),
                "count": len(indirect_costs)
            }
        }
        
        return {
            "code": 200,
            "data": {
                "category_summary": category_summary,
                "details": details
            },
            "message": "获取成本分类成功"
        }
    except Exception as e:
        return {"code": 500, "data": None, "message": f"获取成本分类失败: {str(e)}"}


@router.get("/analysis/details")
def get_cost_details(
    project_id: int = Query(..., description="项目ID"),
    cost_type: Optional[str] = Query(None, description="成本类型筛选"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """获取成本明细列表（支持分页）"""
    try:
        all_details = []
        
        if cost_type is None or cost_type == "物料成本":
            material_costs = db.query(MaterialCost).filter(
                MaterialCost.project_id == str(project_id),
                MaterialCost.is_deleted == False
            ).all()
            for cost in material_costs:
                all_details.append({
                    "id": cost.cost_id,
                    "cost_type": "物料成本",
                    "name": cost.name,
                    "description": cost.remark,
                    "amount": float(cost.total_price or 0),
                    "date": format_datetime(cost.create_time),
                    "create_time": format_datetime(cost.create_time)
                })
        
        if cost_type is None or cost_type == "人力成本":
            labor_costs = db.query(LaborCost).filter(
                LaborCost.project_id == str(project_id),
                LaborCost.is_deleted == False
            ).all()
            for cost in labor_costs:
                all_details.append({
                    "id": cost.cost_id if hasattr(cost, 'cost_id') else cost.id,
                    "cost_type": "人力成本",
                    "name": None,
                    "description": cost.remark,
                    "amount": float(cost.actual_cost or 0),
                    "date": format_datetime(cost.create_time),
                    "create_time": format_datetime(cost.create_time)
                })
        
        if cost_type is None or cost_type == "外包成本":
            outsourcing_costs = db.query(OutsourcingCost).filter(
                OutsourcingCost.project_id == str(project_id),
                OutsourcingCost.is_deleted == False
            ).all()
            for cost in outsourcing_costs:
                all_details.append({
                    "id": cost.cost_id if hasattr(cost, 'cost_id') else cost.id,
                    "cost_type": "外包成本",
                    "name": None,
                    "description": cost.remark,
                    "amount": float(cost.total_price if hasattr(cost, 'total_price') else cost.amount),
                    "date": format_datetime(cost.create_time),
                    "create_time": format_datetime(cost.create_time)
                })
        
        if cost_type is None or cost_type == "间接成本":
            indirect_costs = db.query(IndirectCost).filter(
                IndirectCost.project_id == str(project_id),
                IndirectCost.is_deleted == False
            ).all()
            for cost in indirect_costs:
                all_details.append({
                    "id": cost.cost_id if hasattr(cost, 'cost_id') else cost.id,
                    "cost_type": "间接成本",
                    "name": None,
                    "description": cost.remark,
                    "amount": float(cost.total_price if hasattr(cost, 'total_price') else cost.amount),
                    "date": format_datetime(cost.create_time),
                    "create_time": format_datetime(cost.create_time)
                })
        
        all_details.sort(key=lambda x: x["create_time"] or "", reverse=True)
        
        total = len(all_details)
        paginated_details = all_details[skip:skip + limit]
        
        return {
            "code": 200,
            "data": {
                "items": paginated_details,
                "total": total,
                "skip": skip,
                "limit": limit
            },
            "message": "获取成本明细成功"
        }
    except Exception as e:
        return {"code": 500, "data": None, "message": f"获取成本明细失败: {str(e)}"}


@router.get("/analysis/chart-data")
def get_chart_data(
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    """获取图表数据"""
    try:
        project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
        if not project:
            return {"code": 404, "data": None, "message": "项目不存在"}
        
        material_actual = float(project.material_actual or 0)
        labor_actual = float(project.labor_actual or 0)
        outsourcing_actual = float(project.outsourcing_actual or 0)
        indirect_actual = float(project.indirect_actual or 0)
        
        material_budget = float(project.material_budget or 0)
        labor_budget = float(project.labor_budget or 0)
        outsourcing_budget = float(project.outsourcing_budget or 0)
        indirect_budget = float(project.indirect_budget or 0)
        
        pie_data = [
            {"value": material_actual, "name": "物料成本"},
            {"value": labor_actual, "name": "人力成本"},
            {"value": outsourcing_actual, "name": "外包成本"},
            {"value": indirect_actual, "name": "间接成本"}
        ]
        
        bar_data = {
            "categories": ["物料成本", "人力成本", "外包成本", "间接成本"],
            "budget": [material_budget, labor_budget, outsourcing_budget, indirect_budget],
            "actual": [material_actual, labor_actual, outsourcing_actual, indirect_actual]
        }
        
        return {
            "code": 200,
            "data": {
                "pie_chart": pie_data,
                "bar_chart": bar_data
            },
            "message": "获取图表数据成功"
        }
    except Exception as e:
        return {"code": 500, "data": None, "message": f"获取图表数据失败: {str(e)}"}


@router.get("/analysis/execution-rate")
def get_budget_execution_analysis(
    project_id: int = Query(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    """预算执行率分析"""
    try:
        project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
        if not project:
            return {"code": 404, "data": None, "message": "项目不存在"}
        
        categories = ["material", "labor", "outsourcing", "indirect"]
        category_names = ["物料成本", "人力成本", "外包成本", "间接成本"]
        
        execution_analysis = []
        for cat, name in zip(categories, category_names):
            budget_field = f"{cat}_budget"
            actual_field = f"{cat}_actual"
            
            budget = float(getattr(project, budget_field, 0) or 0)
            actual = float(getattr(project, actual_field, 0) or 0)
            
            variance = budget - actual
            execution_rate = 0.0
            if budget > 0:
                execution_rate = round((actual / budget) * 100, 2)
            
            status = "正常"
            if execution_rate > 100:
                status = "超支"
            elif execution_rate > 90:
                status = "警告"
            elif budget == 0 and actual > 0:
                status = "无预算"
            
            execution_analysis.append({
                "category": name,
                "field": cat,
                "budget": budget,
                "actual": actual,
                "variance": round(variance, 2),
                "execution_rate": execution_rate,
                "status": status
            })
        
        total_budget = float(project.budget_total_cost or 0)
        total_actual = float(project.actual_total_cost or 0)
        total_variance = total_budget - total_actual
        total_execution_rate = 0.0
        if total_budget > 0:
            total_execution_rate = round((total_actual / total_budget) * 100, 2)
        
        return {
            "code": 200,
            "data": {
                "project_id": project.id,
                "project_name": project.name,
                "total_budget": total_budget,
                "total_actual": total_actual,
                "total_variance": round(total_variance, 2),
                "total_execution_rate": total_execution_rate,
                "categories": execution_analysis
            },
            "message": "获取预算执行率分析成功"
        }
    except Exception as e:
        return {"code": 500, "data": None, "message": f"获取预算执行率分析失败: {str(e)}"}


@router.get("/analysis/trend")
def get_cost_trend(
    project_id: int = Query(..., description="项目ID"),
    period: str = Query("month", description="时间周期: month-按月, quarter-按季度, year-按年"),
    db: Session = Depends(get_db)
):
    """成本趋势分析"""
    try:
        project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
        if not project:
            return {"code": 404, "data": None, "message": "项目不存在"}
        
        all_costs = []
        
        material_costs = db.query(MaterialCost).filter(
            MaterialCost.project_id == str(project_id),
            MaterialCost.is_deleted == False
        ).all()
        for cost in material_costs:
            all_costs.append({
                "type": "material",
                "amount": float(cost.total_price or 0),
                "date": cost.create_time
            })
        
        labor_costs = db.query(LaborCost).filter(
            LaborCost.project_id == str(project_id),
            LaborCost.is_deleted == False
        ).all()
        for cost in labor_costs:
            all_costs.append({
                "type": "labor",
                "amount": float(cost.actual_cost or 0),
                "date": cost.create_time
            })
        
        outsourcing_costs = db.query(OutsourcingCost).filter(
            OutsourcingCost.project_id == str(project_id),
            OutsourcingCost.is_deleted == False
        ).all()
        for cost in outsourcing_costs:
            all_costs.append({
                "type": "outsourcing",
                "amount": float(cost.total_price if hasattr(cost, 'total_price') else cost.amount),
                "date": cost.create_time
            })
        
        indirect_costs = db.query(IndirectCost).filter(
            IndirectCost.project_id == str(project_id),
            IndirectCost.is_deleted == False
        ).all()
        for cost in indirect_costs:
            all_costs.append({
                "type": "indirect",
                "amount": float(cost.total_price if hasattr(cost, 'total_price') else cost.amount),
                "date": cost.create_time
            })
        
        trend_data = {}
        for cost in all_costs:
            date = cost["date"]
            if not date:
                continue
                
            if period == "month":
                key = f"{date.year}-{date.month:02d}"
            elif period == "quarter":
                quarter = (date.month - 1) // 3 + 1
                key = f"{date.year}-Q{quarter}"
            else:
                key = str(date.year)
            
            if key not in trend_data:
                trend_data[key] = {"material": 0, "labor": 0, "outsourcing": 0, "indirect": 0, "total": 0, "date": key}
            
            trend_data[key][cost["type"]] += cost["amount"]
            trend_data[key]["total"] += cost["amount"]
        
        sorted_trends = sorted(trend_data.values(), key=lambda x: x["date"])
        
        return {
            "code": 200,
            "data": {
                "project_id": project.id,
                "project_name": project.name,
                "period": period,
                "trends": sorted_trends,
                "summary": {
                    "total_material": sum(t["material"] for t in sorted_trends),
                    "total_labor": sum(t["labor"] for t in sorted_trends),
                    "total_outsourcing": sum(t["outsourcing"] for t in sorted_trends),
                    "total_indirect": sum(t["indirect"] for t in sorted_trends),
                    "grand_total": sum(t["total"] for t in sorted_trends)
                }
            },
            "message": "获取成本趋势成功"
        }
    except Exception as e:
        return {"code": 500, "data": None, "message": f"获取成本趋势失败: {str(e)}"}


@router.get("/analysis/comparison")
def get_project_comparison(
    project_ids: str = Query(..., description="项目ID列表，用逗号分隔"),
    db: Session = Depends(get_db)
):
    """多项目成本对比分析"""
    try:
        ids = [int(x.strip()) for x in project_ids.split(",")]
        
        projects_data = []
        for pid in ids:
            project = db.query(Project).filter(Project.id == pid, Project.is_deleted == False).first()
            if project:
                projects_data.append({
                    "project_id": project.id,
                    "project_name": project.name,
                    "total_budget": float(project.budget_total_cost or 0),
                    "total_actual": float(project.actual_total_cost or 0),
                    "material_actual": float(project.material_actual or 0),
                    "labor_actual": float(project.labor_actual or 0),
                    "outsourcing_actual": float(project.outsourcing_actual or 0),
                    "indirect_actual": float(project.indirect_actual or 0),
                    "budget_execution_rate": round(
                        (project.actual_total_cost / project.budget_total_cost * 100) 
                        if project.budget_total_cost and project.budget_total_cost > 0 else 0, 2
                    )
                })
        
        return {
            "code": 200,
            "data": {
                "projects": projects_data,
                "comparison": {
                    "by_budget": sorted(projects_data, key=lambda x: x["total_budget"], reverse=True),
                    "by_actual": sorted(projects_data, key=lambda x: x["total_actual"], reverse=True),
                    "by_execution_rate": sorted(projects_data, key=lambda x: x["budget_execution_rate"], reverse=True)
                }
            },
            "message": "获取项目对比成功"
        }
    except Exception as e:
        return {"code": 500, "data": None, "message": f"获取项目对比失败: {str(e)}"}
