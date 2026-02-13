from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, select, String, Integer
from sqlalchemy.sql import text
from typing import List, Optional, Dict, Any
from app.core.dependencies import get_db, get_pagination_params, PaginationParams
from app.core.exceptions import NotFoundException

router = APIRouter()

# 项目跟踪相关API接口 - 正确的实现：从现有表直接查询

@router.get("/project-tracking/projects", summary="获取项目跟踪列表 - 直接查询原始表")
def get_project_tracking_list(
    project_name: Optional[str] = Query(None, description="项目名称搜索"),
    status: Optional[str] = Query(None, description="项目状态筛选"),
    risk_level: Optional[str] = Query(None, description="风险等级筛选"),
    priority: Optional[str] = Query(None, description="优先级筛选"),
    page: int = Query(1, description="页码"),
    limit: int = Query(50, description="每页数量"),
    db: Session = Depends(get_db)
):
    """
    正确实现：直接从现有表查询项目跟踪数据
    不使用冗余的project_trackings表
    """
    try:
        # 构建查询条件
        conditions = ["p.is_deleted = 0"]
        params = {}
        
        if project_name:
            conditions.append("p.name LIKE :project_name")
            params["project_name"] = f"%{project_name}%"
        
        if status:
            conditions.append("p.status = :status")
            params["status"] = status
        
        # 直接从原始表查询项目跟踪数据
        base_query = f"""
        SELECT 
            p.id as tracking_id,
            p.id as project_id,
            p.name as project_name,
            p.leader,
            p.status as tracking_status,
            p.progress as overall_progress,
            p.end_date as planned_end_date,
            p.updated_at,
            
            -- 任务统计
            COUNT(DISTINCT pt.task_id) as total_tasks,
            COUNT(DISTINCT CASE WHEN pt.status = '已完成' THEN pt.task_id END) as completed_tasks,
            
            -- 延期风险计算
            CASE 
                WHEN p.end_date < date('now') AND p.status != '已完成' THEN '高风险'
                WHEN p.end_date < date('now', '+7 days') THEN '中风险'
                ELSE '低风险'
            END as risk_level,
            
            -- 优先级计算（基于任务数量）
            CASE 
                WHEN COUNT(DISTINCT pt.task_id) > 2 THEN '高'
                WHEN COUNT(DISTINCT pt.task_id) > 1 THEN '中'
                ELSE '低'
            END as priority_level,
            
            -- 日报工时统计（如果存在）
            COALESCE((SELECT SUM(dwi.hours_spent) FROM daily_work_items dwi 
                     WHERE dwi.project_id = CAST(p.id AS TEXT)), 0) as total_work_hours,
            
            -- 参与人员统计
            COALESCE((SELECT COUNT(DISTINCT dr.employee_name) FROM daily_reports dr 
                     WHERE dr.project_id = CAST(p.id AS TEXT)), 0) as involved_employees
            
        FROM projects p
        LEFT JOIN project_tasks pt ON CAST(p.id AS TEXT) = pt.project_id AND pt.is_deleted = 0
        WHERE {' AND '.join(conditions)}
        GROUP BY p.id, p.name, p.leader, p.status, p.progress, p.end_date, p.updated_at
        ORDER BY p.updated_at DESC
        """
        
        # 计算总数
        count_query = f"""
        SELECT COUNT(*) FROM (
            {base_query}
        ) as subquery
        """
        
        # 添加分页
        offset = (page - 1) * limit
        paginated_query = base_query + f" LIMIT {limit} OFFSET {offset}"
        
        # 执行总数查询
        total_result = db.execute(text(count_query), params)
        total_count = total_result.scalar()
        
        # 执行分页查询
        result = db.execute(text(paginated_query), params)
        rows = result.fetchall()
        
        # 获取列名
        columns = [description[0] for description in result.description]
        
        # 转换为字典格式
        items = []
        for row in rows:
            item = dict(zip(columns, row))
            
            # 计算进度（如果progress为0，则基于任务完成度）
            if item['overall_progress'] == 0 and item['total_tasks'] > 0:
                item['overall_progress'] = round(
                    (item['completed_tasks'] / item['total_tasks']) * 100, 1
                )
            
            # 格式化数据
            item['overall_progress'] = float(item['overall_progress'])
            item['total_work_hours'] = float(item['total_work_hours'])
            
            # 如果有风险等级筛选，添加到筛选条件中
            if risk_level and item['risk_level'] != risk_level:
                continue
                
            # 如果有优先级筛选，添加到筛选条件中
            if priority and item['priority_level'] != priority:
                continue
            
            items.append(item)
        
        return {
            "code": 200,
            "message": "获取项目跟踪列表成功",
            "data": {
                "items": items,
                "total": total_count,
                "page": page,
                "limit": limit
            }
        }
        
    except Exception as e:
        print(f"获取项目跟踪列表失败: {str(e)}")
        return {
            "code": 500,
            "message": f"获取项目跟踪列表失败: {str(e)}",
            "data": None
        }

@router.get("/project-tracking/projects/{project_id}", summary="获取项目跟踪详情")
def get_project_tracking_detail(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    获取项目跟踪详情 - 基于原始表数据
    """
    try:
        # 获取项目基本信息
        project_query = """
        SELECT * FROM projects
        WHERE id = :project_id AND is_deleted = 0
        """
        
        project_result = db.execute(text(project_query), {"project_id": project_id})
        project = project_result.fetchone()
        
        if not project:
            return {
                "code": 404,
                "message": "项目不存在",
                "data": None
            }
        
        # 获取项目任务
        tasks_query = """
        SELECT * FROM project_tasks
        WHERE project_id = :project_id AND is_deleted = 0
        ORDER BY create_time DESC
        """
        
        tasks_result = db.execute(text(tasks_query), {"project_id": str(project_id)})
        task_rows = tasks_result.fetchall()
        
        # 转换为字典格式
        tasks = []
        for row in task_rows:
            task = {
                "task_id": row.task_id,
                "task_name": row.task_name,
                "assignee": row.assignee,
                "status": row.status,
                "progress": float(row.progress or 0),
                "start_date": row.start_date,
                "end_date": row.end_date,
                "actual_hours": float(row.actual_hours or 0),
                "planned_hours": float(row.planned_hours or 0)
            }
            tasks.append(task)
        
        # 获取日报工作项
        work_items_query = """
        SELECT dwi.*, dr.employee_name, dr.report_date
        FROM daily_work_items dwi
        LEFT JOIN daily_reports dr ON dwi.report_id = dr.id
        WHERE dwi.project_id = :project_id AND dwi.is_deleted = 0
        ORDER BY dr.report_date DESC
        """
        
        work_result = db.execute(text(work_items_query), {"project_id": str(project_id)})
        work_rows = work_result.fetchall()
        
        # 转换为字典格式
        work_items = []
        for row in work_rows:
            work_item = {
                "id": row.id,
                "task_name": row.task_name,
                "employee_name": row.employee_name,
                "report_date": row.report_date,
                "hours_spent": float(row.hours_spent or 0),
                "progress_percentage": float(row.progress_percentage or 0),
                "work_content": row.work_content,
                "evaluation": row.evaluation
            }
            work_items.append(work_item)
        
        # 整合项目详情数据
        detail = {
            "project_info": {
                "project_id": project.id,
                "project_name": project.name,
                "leader": project.leader,
                "status": project.status,
                "progress": float(project.progress or 0),
                "start_date": project.start_date,
                "end_date": project.end_date,
                "budget_total_cost": float(project.budget_total_cost or 0),
                "actual_total_cost": float(project.actual_total_cost or 0),
                "description": project.describe
            },
            "task_statistics": {
                "total_tasks": len(tasks),
                "completed_tasks": len([t for t in tasks if t['status'] == '已完成']),
                "in_progress_tasks": len([t for t in tasks if t['status'] == '进行中']),
                "not_started_tasks": len([t for t in tasks if t['status'] == '未开始'])
            },
            "tasks": tasks,
            "daily_work_items": work_items
        }
        
        return {
            "code": 200,
            "message": "获取项目跟踪详情成功",
            "data": detail
        }
        
    except Exception as e:
        print(f"获取项目跟踪详情失败: {str(e)}")
        return {
            "code": 500,
            "message": f"获取项目跟踪详情失败: {str(e)}",
            "data": None
        }
