from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timedelta
from app.core.dependencies import get_db
from app.schemas.response import SuccessResponse

# 创建路由
router = APIRouter(tags=["project_tracking"])

# 辅助函数
def safe_str(value):
    """安全转换为字符串"""
    if value is None:
        return ""
    return str(value)

def safe_float(value):
    """安全转换为浮点数"""
    if value is None:
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

@router.get("/project-tracking-list")
async def get_project_tracking_list(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=100, description="每页数量"),
    project_name: Optional[str] = Query(None, description="项目名称过滤"),
    db: Session = Depends(get_db)
):
    """
    简化实现：直接从现有表查询项目跟踪数据
    """
    try:
        # 简化查询，只查询项目信息，避免重复
        query = """
        SELECT 
            p.id as project_id,
            p.name as project_name,
            p.leader,
            p.start_date as project_start_date,
            p.end_date as project_end_date,
            p.progress as overall_progress,
            p.status as project_status,
            p.updated_at,
            -- 简化的任务信息
            NULL as task_id,
            NULL as task_name,
            NULL as task_assignee,
            NULL as task_status,
            NULL as task_progress,
            0 as budget_cost,
            0 as actual_cost
        FROM projects p
        WHERE p.is_deleted = FALSE
        ORDER BY p.id
        LIMIT :limit OFFSET :offset
        """
        
        # 执行查询
        offset = (page - 1) * limit
        params = {"limit": limit, "offset": offset}
        result = db.execute(text(query), params)
        rows = result.fetchall()
        
        # 处理结果
        items = []
        for row in rows:
            # 简化风险计算 - 基于项目状态
            risk_level = "低风险"
            project_end_date = safe_str(row[4]) if row[4] else None
            project_status = row[6] if row[6] else ""
            
            # 根据项目状态判断风险
            if "延期" in project_status:
                risk_level = "高风险"
            elif "未开始" in project_status:
                risk_level = "中风险"
            elif project_end_date:
                try:
                    end_date = datetime.strptime(project_end_date, "%Y-%m-%d").date()
                    if end_date < datetime.now().date():
                        risk_level = "高风险"
                    elif end_date < (datetime.now().date() + timedelta(days=3)):
                        risk_level = "中风险"
                except ValueError:
                    # 日期格式错误，保持默认低风险
                    pass
            
            item = {
                "project_id": row[0],
                "project_name": row[1],
                "leader": row[2],
                "project_start_date": safe_str(row[3]),
                "project_end_date": safe_str(row[4]),
                "overall_progress": safe_float(row[5]),
                "project_status": row[6],
                "updated_at": safe_str(row[7]),
                
                # 任务信息
                "task_id": row[8],
                "task_name": row[9],
                "task_assignee": row[10],
                "task_status": row[11],
                "task_progress": safe_float(row[12]),
                "budget_cost": safe_float(row[13]),
                "actual_cost": safe_float(row[14]),
                
                # 风险分析
                "risk_level": risk_level,
                "warning_info": None,
                "weekly_reports_count": 0
            }
            items.append(item)
        
        # 获取总记录数
        count_query = """
        SELECT COUNT(*) FROM projects p
        WHERE p.is_deleted = FALSE
        """
        count_result = db.execute(text(count_query))
        total = count_result.fetchone()[0]
        
        return SuccessResponse(
            data={
                "items": items,
                "total": total,
                "page": page,
                "limit": limit
            },
            message="获取项目跟踪列表成功"
        )
        
    except Exception as e:
        return SuccessResponse(
            data=None,
            message=f"获取项目跟踪列表失败: {str(e)}"
        )

@router.get("/project-tracking/{project_id}")
async def get_project_tracking_detail(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    获取项目跟踪详情 - 基于原始表数据
    """
    try:
        # 获取项目基本信息
        project_query = """
        SELECT * FROM projects
        WHERE id = :project_id AND is_deleted = FALSE
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
        WHERE project_id = :project_id AND is_deleted = FALSE
        ORDER BY create_time DESC
        """
        
        tasks_result = db.execute(text(tasks_query), {"project_id": str(project_id)})
        tasks = tasks_result.fetchall()
        
        # 获取成本分析
        cost_query = """
        SELECT 
            SUM(budget_cost) as total_budget,
            SUM(actual_cost) as total_actual,
            SUM(budget_cost - actual_cost) as budget_variance,
            CASE 
                WHEN SUM(budget_cost) > 0 THEN 
                    ROUND((SUM(actual_cost) / SUM(budget_cost) - 1) * 100, 2)
                ELSE 0 
            END as cost_variance_percent
        FROM project_tasks
        WHERE project_id = :project_id AND is_deleted = FALSE
        """
        
        cost_result = db.execute(text(cost_query), {"project_id": str(project_id)})
        cost_data = cost_result.fetchone()
        
        # 获取进度统计
        progress_query = """
        SELECT 
            COUNT(*) as total_tasks,
            COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_tasks,
            COUNT(CASE WHEN status = '进行中' THEN 1 END) as in_progress_tasks,
            COUNT(CASE WHEN status = '未开始' THEN 1 END) as pending_tasks,
            ROUND(AVG(progress), 2) as avg_progress
        FROM project_tasks
        WHERE project_id = :project_id AND is_deleted = FALSE
        """
        
        progress_result = db.execute(text(progress_query), {"project_id": str(project_id)})
        progress_data = progress_result.fetchone()
        
        # 构建响应数据
        project_data = {
            "project_id": project[0],
            "name": project[1],
            "description": safe_str(project[2]),
            "leader": project[3],
            "start_date": safe_str(project[4]),
            "end_date": safe_str(project[5]),
            "progress": safe_float(project[6]),
            "status": project[7],
            "budget": safe_float(project[8]),
            "cost": safe_float(project[9]),
            "create_time": safe_str(project[10]),
            "update_time": safe_str(project[11])
        }
        
        task_list = []
        for task in tasks:
            task_list.append({
                "task_id": task[0],
                "task_name": task[1],
                "assignee": task[2],
                "start_date": safe_str(task[3]),
                "end_date": safe_str(task[4]),
                "progress": safe_float(task[5]),
                "status": task[6],
                "create_time": safe_str(task[7]),
                "update_time": safe_str(task[8])
            })
        
        cost_analysis = {
            "total_budget": safe_float(cost_data[0]) if cost_data else 0,
            "total_actual": safe_float(cost_data[1]) if cost_data else 0,
            "budget_variance": safe_float(cost_data[2]) if cost_data else 0,
            "cost_variance_percent": safe_float(cost_data[3]) if cost_data else 0
        }
        
        progress_stats = {
            "total_tasks": progress_data[0] if progress_data else 0,
            "completed_tasks": progress_data[1] if progress_data else 0,
            "in_progress_tasks": progress_data[2] if progress_data else 0,
            "pending_tasks": progress_data[3] if progress_data else 0,
            "avg_progress": safe_float(progress_data[4]) if progress_data else 0
        }
        
        return {
            "code": 200,
            "message": "获取项目跟踪详情成功",
            "data": {
                "project": project_data,
                "tasks": task_list,
                "cost_analysis": cost_analysis,
                "progress_stats": progress_stats
            }
        }
        
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取项目跟踪详情失败: {str(e)}",
            "data": None
        }

@router.get("/project-tracking/{project_id}/gantt")
async def get_project_gantt_data(
    project_id: str,
    db: Session = Depends(get_db)
):
    """
    获取项目甘特图数据
    """
    try:
        # 获取项目基本信息
        project_query = """
        SELECT 
            id, name, leader, start_date, end_date, progress, status
        FROM projects
        WHERE id = :project_id AND is_deleted = FALSE
        """
        
        project_result = db.execute(text(project_query), {"project_id": project_id})
        project = project_result.fetchone()
        
        if not project:
            return {
                "code": 404,
                "message": "项目不存在",
                "data": None
            }
        
        # 获取项目的任务（简化版）
        tasks_query = """
        SELECT 
            task_id,
            task_name,
            assignee,
            status,
            progress,
            budget_cost,
            actual_cost,
            create_time,
            update_time,
            leaf_node
        FROM project_tasks
        WHERE project_id = :project_id 
        AND is_deleted = FALSE
        ORDER BY task_id
        LIMIT 50
        """
        
        tasks_result = db.execute(text(tasks_query), {"project_id": str(project_id)})
        tasks = tasks_result.fetchall()
        
        # 构建响应数据
        task_list = []
        for task in tasks:
            task_id = task[0]
            task_name = task[1]
            assignee = task[2] or '未指定'
            current_status = task[3] or '未开始'
            progress = float(task[4]) if task[4] else 0
            budget_cost = float(task[5]) if task[5] else 0
            actual_cost = float(task[6]) if task[6] else 0
            create_time = task[7]
            update_time = task[8]
            leaf_node = task[9] if len(task) > 9 else None
            
            # 根据状态确定显示状态
            display_status = current_status
            if current_status and '完成' in current_status:
                display_status = '已完成'
            elif current_status and '进行' in current_status:
                display_status = '进行中'
            elif current_status and '未开始' in current_status:
                display_status = '未开始'
            else:
                display_status = '未开始'
            
            # 计算风险等级（基于预算和实际成本）
            risk_level = '低风险'
            if actual_cost > budget_cost * 1.2:
                risk_level = '高风险'
            elif actual_cost > budget_cost * 1.1:
                risk_level = '中风险'
            
            task_list.append({
                "task_id": task_id,
                "task_name": task_name,
                "assignee": assignee,
                "status": display_status,
                "progress": progress,
                "budget_cost": budget_cost,
                "actual_cost": actual_cost,
                "risk_level": risk_level,
                "create_time": create_time,
                "update_time": update_time,
                "leaf_node": leaf_node
            })
        
        # 项目基本信息
        project_data = {
            "project_id": project[0],
            "project_name": project[1],
            "leader": project[2],
            "start_date": project[3],
            "end_date": project[4],
            "progress": float(project[5]) if project[5] else 0,
            "status": project[6]
        }
        
        # 日报统计（简化）
        reports_stats = {
            "weekly": 0,
            "total": 0
        }
        
        return {
            "code": 200,
            "message": "获取项目甘特图数据成功",
            "data": {
                "project": project_data,
                "tasks": task_list,
                "reports_count": reports_stats
            }
        }

    except Exception as e:
        # 记录详细错误信息
        import traceback
        error_detail = traceback.format_exc()
        print(f"甘特图API错误详情: {error_detail}")
        
        return {
            "code": 500,
            "message": f"获取项目甘特图数据失败: {str(e)}",
            "data": None
        }