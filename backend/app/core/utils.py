from datetime import datetime
from typing import Optional
from app.models.project import Project
from app.models.project_task import ProjectTask
from sqlalchemy.orm import Session


def calculate_project_status(project: Project, actual_end_date: Optional[datetime.date] = None, db: Optional[Session] = None) -> str:
    """
    计算项目状态
    
    Args:
        project: 项目对象
        actual_end_date: 项目实际结束日期（可选，如果不提供，会从数据库查询）
        db: 数据库会话（可选，当需要查询实际结束日期时需要）
    
    Returns:
        项目状态字符串
    """
    current_date = datetime.now().date()
    
    # 固定状态直接返回
    if project.status in ["规划中", "已暂停", "已取消"]:
        return project.status
    
    # 如果没有提供实际结束日期，从数据库查询
    if actual_end_date is None and db:
        first_task = db.query(ProjectTask.actual_end_date).filter(
            ProjectTask.project_id == str(project.id),
            ProjectTask.is_deleted == False
        ).order_by(ProjectTask.task_id).first()
        actual_end_date = first_task[0] if first_task else None
    
    m = project.end_date
    n = actual_end_date
    k = current_date
    
    if n is None:
        if m and m >= k:
            return "进行中"
        elif m and m < k:
            return "已延期"
        else:
            return "进行中"
    else:
        if m and m > n:
            return "提前完成"
        elif m and m == n:
            return "已完成"
        elif m and m < n:
            return "延期完成"
        else:
            return "已完成"


def get_project_actual_end_date(project_id: int, db: Session) -> Optional[datetime.date]:
    """
    获取项目的实际结束日期（从第一个任务的实际结束日期获取）
    
    Args:
        project_id: 项目ID
        db: 数据库会话
    
    Returns:
        项目实际结束日期，如果没有则返回None
    """
    first_task = db.query(ProjectTask.actual_end_date).filter(
        ProjectTask.project_id == str(project_id),
        ProjectTask.is_deleted == False
    ).order_by(ProjectTask.task_id).first()
    
    return first_task[0] if first_task else None