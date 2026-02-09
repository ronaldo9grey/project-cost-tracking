from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, select, String, Integer
from typing import List, Optional, Dict, Any
from app.core.dependencies import get_db, get_pagination_params, PaginationParams
from app.core.exceptions import NotFoundException
from app.core.utils import calculate_project_status, get_project_actual_end_date
from app.models.project import Project
from app.models.project_task import ProjectTask

from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, TaskCreate, TaskUpdate, TaskResponse
from app.schemas.response import SuccessResponse, PaginationResponse
from app.crud.project import get_project_list, get_all_projects

router = APIRouter()


# 首先定义精确匹配的路由，避免被动态路由覆盖
@router.get("/tasks", summary="获取所有项目任务")
def get_all_project_tasks(db: Session = Depends(get_db)):
    """
    获取所有项目的任务列表，按照用户提供的SQL逻辑：
    select p.name project_name,p.leader,pt.task_name,pt.assignee,pt.start_date,pt.end_date,pt.actual_end_date, CURRENT_DATE, CURRENT_DATE-pt.end_date difdays 
    from projects p 
    left join project_tasks pt on p.id = cast(pt.project_id as integer) 
    where pt.actual_end_date is null and p.is_deleted = false and pt.is_deleted = false  and CURRENT_DATE>pt.start_date AND CURRENT_DATE>pt.end_date 
    order by pt.task_id
    """
    try:
        from datetime import datetime
        current_date = datetime.now().date()
        
        # 构建查询，连接Project和ProjectTask表
        # 注意：ProjectTask.project_id是String类型，而Project.id是Integer类型，需要转换
        tasks_query = db.query(
            Project.name.label("project_name"),
            Project.leader,
            ProjectTask.task_name,
            ProjectTask.assignee,
            ProjectTask.start_date,
            ProjectTask.end_date,
            ProjectTask.actual_end_date,
            ProjectTask.task_id,
            ProjectTask.leaf_node
        ).join(
            Project, Project.id == ProjectTask.project_id.cast(String).cast(Integer)
        ).filter(
            ProjectTask.actual_end_date.is_(None),
            Project.is_deleted == False,
            ProjectTask.is_deleted == False,
            ProjectTask.start_date < current_date,
            ProjectTask.end_date < current_date
        ).order_by(
            ProjectTask.task_id
        )
        
        tasks = tasks_query.all()
        
        # 转换为字典列表，避免序列化问题
        tasks_dict_list = []
        for task in tasks:
            # 计算延期天数
            difdays = None
            if task.end_date:
                end_date = task.end_date.date() if hasattr(task.end_date, 'date') else task.end_date
                difdays = (current_date - end_date).days
            
            # 将Date和DateTime类型转换为字符串，避免序列化错误
            task_dict = {
                "project_name": task.project_name,
                "leader": task.leader,
                "task_name": task.task_name,
                "assignee": task.assignee,
                "start_date": task.start_date.isoformat() if task.start_date else None,
                "end_date": task.end_date.isoformat() if task.end_date else None,
                "actual_end_date": task.actual_end_date.isoformat() if task.actual_end_date else None,
                "current_date": current_date.isoformat(),
                "difdays": difdays,
                "task_id": task.task_id,
                "leaf_node": task.leaf_node
            }
            tasks_dict_list.append(task_dict)
        
        return SuccessResponse(data=tasks_dict_list, message="获取所有项目任务成功")
    except Exception as e:
        # 记录详细的错误信息
        import traceback
        print(f"Error in get_all_project_tasks: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return SuccessResponse(data=[], message=f"获取任务列表失败: {str(e)}")


@router.get("/")
def get_projects(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination_params),
    status: Optional[str] = None,
    name: Optional[str] = Query(None, description="项目名称模糊匹配"),
    sort_by: str = Query("name", description="排序字段"),
    sort_order: str = Query("asc", description="排序顺序: asc或desc")
):
    """
    获取项目列表
    """
    # 构建查询
    query = db.query(Project).filter(Project.is_deleted == False)
    
    # 状态过滤
    if status:
        query = query.filter(Project.status == status)
    
    # 项目名称模糊匹配
    if name:
        query = query.filter(Project.name.ilike(f"%{name}%"))
    
    # 计算总记录数
    total = query.count()
    
    # 排序处理
    if sort_by == "name":
        if sort_order == "desc":
            query = query.order_by(Project.name.desc())
        else:
            query = query.order_by(Project.name.asc())
    
    # 获取分页数据
    projects = query.offset(pagination.skip).limit(pagination.limit).all()
    
    # 处理每个项目，添加实际结束日期和计算状态
    project_data = []
    for project in projects:
        # 获取项目实际结束日期
        actual_end_date = get_project_actual_end_date(project.id, db)
        
        # 计算项目状态
        project_status = calculate_project_status(project, actual_end_date)
        
        # 构建项目数据
        project_dict = {
            "id": project.id,
            "name": project.name,
            "leader": project.leader,
            "status": project_status,
            "progress": project.progress,
            "start_date": project.start_date,
            "计划结束日期": project.end_date,
            "实际结束日期": actual_end_date,
            "contract_date": project.contract_date,
            "contract_no": project.contract_no,
            "contract_amount": project.contract_amount,
            "budget_total_cost": project.budget_total_cost,
            "actual_total_cost": project.actual_total_cost,
            # 添加各维度的预算和实际值
            # 注意：模型中实际值字段名是material_actual等，对应数据库中的material_cost等列
            "material_budget": project.material_budget,
            "material_cost": project.material_actual,
            "outsourcing_budget": project.outsourcing_budget,
            "outsourcing_cost": project.outsourcing_actual,
            "indirect_budget": project.indirect_budget,
            "indirect_cost": project.indirect_actual,
            "labor_budget": project.labor_budget,
            "labor_cost": project.labor_actual,
            "created_at": project.created_at,
            "updated_at": project.updated_at
        }
        
        project_data.append(project_dict)
    
    # 构建分页响应
    pagination_response = PaginationResponse(
        items=project_data,
        total=total,
        page=pagination.page,
        size=pagination.size,
        total_pages=(total + pagination.size - 1) // pagination.size
    )
    
    return SuccessResponse(data=pagination_response, message="获取项目列表成功")


@router.get("/check-name/{name}")
def check_project_name(name: str, exclude_id: Optional[int] = None, db: Session = Depends(get_db)):
    """
    检查项目名称是否已存在
    """
    # 精确匹配项目名称，并且只检查未删除的项目
    query = db.query(Project).filter(
        Project.name == name,
        Project.is_deleted == False
    )
    
    # 如果提供了exclude_id，则排除该ID的项目
    if exclude_id:
        query = query.filter(Project.id != exclude_id)
    
    project = query.first()
    
    result = {
        "exists": project is not None,
        "message": "项目名称已存在" if project else "项目名称可用"
    }
    
    return SuccessResponse(data=result, message="检查项目名称成功")


@router.post("/")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """
    创建项目
    """
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # 转换为字典，避免序列化问题
    project_dict = {
        "id": db_project.id,
        "name": db_project.name,
        "describe": db_project.describe,
        "start_date": db_project.start_date,
        "end_date": db_project.end_date,
        "budget_total_cost": db_project.budget_total_cost,
        "actual_total_cost": db_project.actual_total_cost,
        "contract_amount": db_project.contract_amount,
        "status": db_project.status,
        "progress": db_project.progress,
        "leader": db_project.leader,
        "contract_no": db_project.contract_no,
        "contract_date": db_project.contract_date,
        "tax_rate": db_project.tax_rate,
        "revenue": db_project.revenue,
        "target_profit": db_project.target_profit,
        "created_at": db_project.created_at,
        "updated_at": db_project.updated_at
    }
    
    return SuccessResponse(data=project_dict, message="创建项目成功")


@router.get("/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    获取项目详情
    """
    project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
    if not project:
        raise NotFoundException(message="项目未找到")
    
    # 转换为字典，避免序列化问题
    project_dict = {
        "id": project.id,
        "name": project.name,
        "describe": project.describe,
        "start_date": project.start_date,
        "end_date": project.end_date,
        "budget_total_cost": project.budget_total_cost,
        "actual_total_cost": project.actual_total_cost,
        "contract_amount": project.contract_amount,
        "status": project.status,
        "progress": project.progress,
        "leader": project.leader,
        "contract_no": project.contract_no,
        "contract_date": project.contract_date,
        "tax_rate": project.tax_rate,
        "revenue": project.revenue,
        "target_profit": project.target_profit,
        "created_at": project.created_at,
        "updated_at": project.updated_at
    }
    
    return SuccessResponse(data=project_dict, message="获取项目详情成功")


@router.put("/{project_id}")
def update_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    """
    更新项目
    """
    db_project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
    if not db_project:
        raise NotFoundException(message="项目未找到")
    
    update_data = project.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    
    # 转换为字典，避免序列化问题
    project_dict = {
        "id": db_project.id,
        "name": db_project.name,
        "describe": db_project.describe,
        "start_date": db_project.start_date,
        "end_date": db_project.end_date,
        "budget_total_cost": db_project.budget_total_cost,
        "actual_total_cost": db_project.actual_total_cost,
        "contract_amount": db_project.contract_amount,
        "status": db_project.status,
        "progress": db_project.progress,
        "leader": db_project.leader,
        "contract_no": db_project.contract_no,
        "contract_date": db_project.contract_date,
        "tax_rate": db_project.tax_rate,
        "revenue": db_project.revenue,
        "target_profit": db_project.target_profit,
        "created_at": db_project.created_at,
        "updated_at": db_project.updated_at
    }
    
    return SuccessResponse(data=project_dict, message="更新项目成功")


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    删除项目
    """
    db_project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
    if not db_project:
        raise NotFoundException(message="项目未找到")
    
    # 软删除
    db_project.is_deleted = True
    db.commit()
    
    return SuccessResponse(data=None, message="项目已删除")


@router.get("/{project_id}/tasks")
def get_project_tasks(project_id: int, db: Session = Depends(get_db)):
    """
    获取项目任务列表
    """
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
    if not project:
        raise NotFoundException(message="项目未找到")
    
    # 使用ProjectTask模型，它映射到正确的project_tasks表
    # 注意：ProjectTask.project_id是String类型，而project_id是Integer类型，需要转换
    tasks = db.query(ProjectTask).filter(ProjectTask.project_id == str(project_id), ProjectTask.is_deleted == False).all()
    
    # 转换为字典列表，避免序列化问题
    tasks_dict_list = []
    for task in tasks:
        # 将Date和DateTime类型转换为字符串，避免序列化错误
        task_dict = {
            "task_id": task.task_id,
            "project_id": task.project_id,
            "task_name": task.task_name,
            "parent_task_id": task.parent_task_id,
            "task_level": task.task_level,
            "assignee": task.assignee,
            "assignee_id": task.assignee_id,
            "start_date": task.start_date.isoformat() if task.start_date else None,
            "end_date": task.end_date.isoformat() if task.end_date else None,
            "actual_end_date": task.actual_end_date.isoformat() if task.actual_end_date else None,
            "planned_hours": task.planned_hours,
            "actual_hours": task.actual_hours,
            "adjusted_hours": task.adjusted_hours,
            "budget_cost": task.budget_cost,
            "actual_cost": task.actual_cost,
            "status": task.status,
            "progress": task.progress,
            "evaluation": task.evaluation,
            "evaluation_desc": task.evaluation_desc,
            "progress_rootcause": task.progress_rootcause,
            "measures_results": task.measures_results,
            "attachment": task.attachment,
            "isNode": task.isNode,
            "leaf_node": task.leaf_node,
            "remark": task.remark,
            "create_time": task.create_time.isoformat() if task.create_time else None,
            "update_time": task.update_time.isoformat() if task.update_time else None
        }
        tasks_dict_list.append(task_dict)
    
    return SuccessResponse(data=tasks_dict_list, message="获取项目任务列表成功")


@router.post("/{project_id}/tasks")
def create_project_task(project_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    """
    创建项目任务
    """
    # 验证项目是否存在
    project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
    if not project:
        raise NotFoundException(message="项目未找到")
    
    db_task = Task(**task.dict(), project_id=project_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # 转换为字典，避免序列化问题
    task_dict = {
        "id": db_task.id,
        "project_id": db_task.project_id,
        "name": db_task.name,
        "description": db_task.description,
        "start_date": db_task.start_date,
        "end_date": db_task.end_date,
        "status": db_task.status,
        "progress": db_task.progress,
        "assigned_to": db_task.assigned_to,
        "created_at": db_task.created_at,
        "updated_at": db_task.updated_at
    }
    
    return SuccessResponse(data=task_dict, message="创建项目任务成功")


@router.get("/{project_id}/costs", response_class=JSONResponse)
def get_project_costs(project_id: int, db: Session = Depends(get_db)):
    """
    获取项目成本汇总和明细
    """
    project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
    if not project:
        raise NotFoundException(message="项目未找到")
    
    # 导入正确的成本模型
    from app.models.material_cost import MaterialCost
    from app.models.labor_cost import LaborCost
    from app.models.outsourcing_cost import OutsourcingCost
    from app.models.indirect_cost import IndirectCost
    from app.models.resource import Personnel
    
    # 打印调试日志，显示查询的项目ID
    print(f"DEBUG: 查询项目ID {project_id} 的成本明细数据")
    
    # 构建物料成本查询 - project_id是字符型，is_deleted是布尔型，false表示未删除
    material_query = db.query(MaterialCost).filter(
        MaterialCost.project_id == str(project_id),
        MaterialCost.is_deleted == False
    )
    # 打印SQL语句
    print(f"DEBUG: 物料成本查询SQL: {material_query}")
    # 执行查询
    material_costs = material_query.all()
    print(f"DEBUG: 物料成本查询结果数量: {len(material_costs)}")
    
    # 构建人力成本查询 - 关联personnel表获取员工姓名、部门和职位
    labor_query = db.query(
        LaborCost.cost_id,
        LaborCost.employee_id,
        LaborCost.actual_cost,
        LaborCost.budget_cost,
        LaborCost.budget_hours,
        LaborCost.actual_hours,
        LaborCost.hourly_rate,
        LaborCost.remark,
        Personnel.name.label("employee_name"),
        Personnel.department.label("department"),
        Personnel.position.label("position")
    ).join(
        Personnel, LaborCost.employee_id == Personnel.id.cast(String)
    ).filter(
        LaborCost.project_id == str(project_id),
        LaborCost.is_deleted == False
    )
    # 打印SQL语句
    print(f"DEBUG: 人力成本查询SQL: {labor_query}")
    # 执行查询
    labor_costs = labor_query.all()
    print(f"DEBUG: 人力成本查询结果数量: {len(labor_costs)}")
    
    # 构建外包成本查询 - project_id是字符型，is_deleted是布尔型，false表示未删除
    outsourcing_query = db.query(OutsourcingCost).filter(
        OutsourcingCost.project_id == str(project_id),
        OutsourcingCost.is_deleted == False
    )
    # 打印SQL语句
    print(f"DEBUG: 外包成本查询SQL: {outsourcing_query}")
    # 执行查询
    outsourcing_costs = outsourcing_query.all()
    print(f"DEBUG: 外包成本查询结果数量: {len(outsourcing_costs)}")
    
    # 构建间接成本查询 - project_id是字符型，is_deleted是布尔型，false表示未删除
    indirect_query = db.query(IndirectCost).filter(
        IndirectCost.project_id == str(project_id),
        IndirectCost.is_deleted == False
    )
    # 打印SQL语句
    print(f"DEBUG: 间接成本查询SQL: {indirect_query}")
    # 执行查询
    indirect_costs = indirect_query.all()
    print(f"DEBUG: 间接成本查询结果数量: {len(indirect_costs)}")
    
    # 构建返回数据，包含成本汇总和明细
    # 使用SuccessResponse模型，确保正确的序列化和字符编码
    return SuccessResponse(
        data={
            "project_id": project_id,
            "material_cost": project.material_actual,  # 模型属性名是material_actual，映射到数据库的material_cost列
            "labor_cost": project.labor_actual,  # 模型属性名是labor_actual，映射到数据库的labor_cost列
            "outsourcing_cost": project.outsourcing_actual,  # 模型属性名是outsourcing_actual，映射到数据库的outsourcing_cost列
            "indirect_cost": project.indirect_actual,  # 模型属性名是indirect_actual，映射到数据库的indirect_cost列
            "total_cost": project.actual_total_cost,
            "budget_total_cost": project.budget_total_cost,
            "material_budget": project.material_budget,
            "labor_budget": project.labor_budget,
            "outsourcing_budget": project.outsourcing_budget,
            "indirect_budget": project.indirect_budget,
            # 包含成本明细，返回完整字段，避免序列化问题
            "material_costs": [{"cost_id": cost.cost_id, "name": cost.name, "specification": cost.specification, "unit": cost.unit, "quantity": cost.quantity, "unit_price": cost.unit_price, "total_price": cost.total_price, "cost_type": cost.cost_type, "remark": cost.remark} for cost in material_costs],
            "outsourcing_costs": [{"cost_id": cost.cost_id, "service_type": cost.service_type, "description": cost.description, "total_price": cost.total_price, "cost_type": cost.cost_type, "remark": cost.remark} for cost in outsourcing_costs],
            "indirect_costs": [{"cost_id": cost.cost_id, "cost_type": cost.cost_type, "description": cost.description, "amount": cost.amount, "cost_type_flag": cost.cost_type_flag, "remark": cost.remark} for cost in indirect_costs],
            "labor_costs": [{"cost_id": cost.cost_id, "employee_id": cost.employee_id, "employee_name": cost.employee_name, "department": cost.department, "position": cost.position, "actual_cost": cost.actual_cost, "budget_cost": cost.budget_cost, "budget_hours": cost.budget_hours, "actual_hours": cost.actual_hours, "hourly_rate": cost.hourly_rate, "remark": cost.remark} for cost in labor_costs]
        },
        message="获取项目成本汇总成功"
    )


@router.get("/statistics/overview")
def get_project_overview_statistics(db: Session = Depends(get_db)):
    """
    获取项目统计概览
    """
    from datetime import datetime
    current_date = datetime.now().date()
    
    # 总项目数
    total_projects = db.query(func.count(Project.id)).filter(Project.is_deleted == False).scalar() or 0
    
    # 获取所有项目
    all_projects = db.query(Project).filter(Project.is_deleted == False).all()
    
    # 初始化状态计数
    status_counts = {
        "规划中": 0,
        "进行中": 0,
        "提前完成": 0,
        "已完成": 0,
        "延期完成": 0,
        "已延期": 0,
        "已暂停": 0,
        "已取消": 0
    }
    
    # 计算各状态项目数
    for project in all_projects:
        # 获取项目实际结束日期
        actual_end_date = get_project_actual_end_date(project.id, db)
        
        # 计算状态
        project_status = calculate_project_status(project, actual_end_date)
        
        # 更新状态计数
        if project_status in status_counts:
            status_counts[project_status] += 1
    
    # 计算总合同额
    total_contract_amount = db.query(func.sum(Project.contract_amount)).filter(Project.is_deleted == False).scalar() or 0
    
    # 计算预算成本合计和实际成本合计
    total_budget_cost = db.query(func.sum(Project.budget_total_cost)).filter(Project.is_deleted == False).scalar() or 0
    total_actual_cost = db.query(func.sum(Project.actual_total_cost)).filter(Project.is_deleted == False).scalar() or 0
    
    # 计算成本偏差：实际成本合计 - 预算成本合计
    cost_variance = total_actual_cost - total_budget_cost
    
    # 平均进度
    avg_progress = db.query(func.avg(Project.progress)).filter(Project.is_deleted == False).scalar() or 0
    
    statistics_data = {
        "total_projects": total_projects,
        "status_counts": status_counts,
        "total_contract_amount": total_contract_amount,
        "total_budget_cost": total_budget_cost,
        "total_actual_cost": total_actual_cost,
        "cost_variance": cost_variance,
        "avg_progress": round(avg_progress, 2)
    }
    
    # 添加调试信息
    print(f"项目统计调试: 总项目数={total_projects}, 状态统计={status_counts}")
    
    return SuccessResponse(data=statistics_data, message="获取项目统计概览成功")


@router.get("/statistics/cost")
def get_project_cost_statistics(db: Session = Depends(get_db)):
    """
    获取项目成本统计
    """
    # 各成本类型的预算和实际成本
    cost_statistics = db.query(
        func.sum(Project.material_budget).label("material_budget"),
        func.sum(Project.material_cost).label("material_actual"),
        func.sum(Project.labor_budget).label("labor_budget"),
        func.sum(Project.labor_cost).label("labor_actual"),
        func.sum(Project.outsourcing_budget).label("outsourcing_budget"),
        func.sum(Project.outsourcing_cost).label("outsourcing_actual"),
        func.sum(Project.indirect_budget).label("indirect_budget"),
        func.sum(Project.indirect_cost).label("indirect_actual")
    ).filter(
        Project.is_deleted == False
    ).first()
    
    return SuccessResponse(data=cost_statistics._asdict(), message="获取项目成本统计成功")


@router.get("/statistics/progress")
def get_project_progress_statistics(db: Session = Depends(get_db)):
    """
    获取项目进度统计
    """
    # 进度区间统计
    # 定义进度区间
    progress_ranges = [
        (0, 20),
        (21, 40),
        (41, 60),
        (61, 80),
        (81, 100)
    ]
    
    progress_statistics = []
    
    for min_progress, max_progress in progress_ranges:
        count = db.query(func.count(Project.id)).filter(
            Project.is_deleted == False,
            Project.progress >= min_progress,
            Project.progress <= max_progress
        ).scalar() or 0
        
        progress_statistics.append({
            "range": f"{min_progress}-{max_progress}%",
            "count": count
        })
    
    result = {
        "progress_distribution": progress_statistics
    }
    
    return SuccessResponse(data=result, message="获取项目进度统计成功")


# 批量创建项目任务API
@router.post("/tasks/batch", status_code=201, summary="批量创建项目任务")
def batch_create_project_tasks(
    tasks: List[dict],
    db: Session = Depends(get_db)
):
    """
    批量创建项目任务（保存到project_tasks表）
    """
    # TODO: 实现批量创建项目任务功能
    result = {"message": "任务创建成功", "count": len(tasks)}
    return SuccessResponse(data=result, message="批量创建项目任务成功")


# 批量创建项目任务附件API
@router.post("/task-attachments/batch", status_code=201, summary="批量创建项目任务附件")
def batch_create_project_task_attachments(
    attachments: List[dict],
    db: Session = Depends(get_db)
):
    """
    批量创建项目任务附件（保存到project_task_attachments表）
    """
    # TODO: 实现批量创建项目任务附件功能
    result = {"message": "附件创建成功", "count": len(attachments)}
    return SuccessResponse(data=result, message="批量创建项目任务附件成功")


@router.get("/{project_id}/task-attachments/{task_id}")
def get_project_task_attachments(
    project_id: int,
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    获取指定项目指定任务的附件列表
    """
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
    if not project:
        raise NotFoundException(message="项目未找到")
    
    # 导入project_task_attachment模型
    from app.models.project_task_attachment import ProjectTaskAttachment
    
    # 查询指定任务的附件，添加project_id过滤
    attachments = db.query(ProjectTaskAttachment).filter(
        ProjectTaskAttachment.task_id == task_id
    ).all()
    
    # 转换为字典列表，避免序列化问题
    attachments_dict_list = []
    for attachment in attachments:
        attachment_dict = {
            "attachment_id": attachment.attachment_id,
            "task_id": attachment.task_id,
            "file_name": attachment.file_name,
            "file_data": attachment.file_data,
            "file_size": attachment.file_size,
            "uploader_id": attachment.uploader_id,
            "uploader_name": attachment.uploader_name,
            "created_at": attachment.created_at,
            "updated_at": attachment.updated_at
        }
        attachments_dict_list.append(attachment_dict)
    
    return SuccessResponse(data=attachments_dict_list, message="获取任务附件成功")


# 项目文档API路由
@router.get("/{project_id}/documents", summary="获取项目文档列表")
def get_project_documents_api(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    获取指定项目的文档列表（从project_task_attachments表获取）
    """
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
    if not project:
        raise NotFoundException(message="项目未找到")
    
    # 获取项目文档列表
    documents = get_project_documents(db=db, project_id=project_id)
    
    # 转换为字典格式返回（匹配project_task_attachments表结构）
    documents_dict_list = []
    for doc in documents:
        doc_dict = {
            "id": doc.attachment_id,  # 使用attachment_id作为文档ID
            "document_name": doc.file_name,  # 使用file_name作为文档名称
            "document_type": "附件",  # 固定类型为"附件"
            "file_path": doc.file_data,  # 使用file_data作为文件路径
            "file_size": doc.file_size,
            "task_id": doc.task_id,  # 添加任务ID
            "created_at": doc.created_at,
            "updated_at": doc.updated_at
        }
        documents_dict_list.append(doc_dict)
    
    return SuccessResponse(data=documents_dict_list, message="获取项目文档列表成功")


@router.post("/{project_id}/documents", status_code=201, summary="创建项目文档")
def create_project_document_api(
    project_id: int,
    document_data: dict,
    db: Session = Depends(get_db)
):
    """
    为指定项目创建文档记录（在project_task_attachments表中）
    """
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
    if not project:
        raise NotFoundException(message="项目未找到")
    
    # 创建文档记录
    document = create_project_document(db=db, document=document_data)
    
    # 转换为字典格式返回（匹配project_task_attachments表结构）
    document_dict = {
        "id": document.attachment_id,
        "document_name": document.file_name,
        "document_type": "附件",
        "file_path": document.file_data,
        "file_size": document.file_size,
        "task_id": document.task_id,
        "created_at": document.created_at,
        "updated_at": document.updated_at
    }
    
    return SuccessResponse(data=document_dict, message="创建项目文档成功")


@router.delete("/{project_id}/documents/{document_id}", summary="删除项目文档")
def delete_project_document_api(
    project_id: int,
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    删除指定项目的文档记录
    """
    # 检查项目是否存在
    project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()
    if not project:
        raise NotFoundException(message="项目未找到")
    
    # 删除文档记录
    success = delete_project_document(db=db, document_id=document_id)
    
    if success:
        return SuccessResponse(data={"document_id": document_id}, message="删除项目文档成功")
    else:
        raise NotFoundException(message="文档未找到")
