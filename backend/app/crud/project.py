"""
项目相关的CRUD操作
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Dict, Any, Optional
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


def get_project_list(
    db: Session,
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    获取项目列表
    
    Args:
        db: 数据库会话
        page: 页码
        size: 每页数量
        search: 搜索关键词
        status: 项目状态筛选
    
    Returns:
        项目列表数据
    """
    # 构建基础查询
    query = db.query(Project).filter(Project.is_deleted == False)
    
    # 添加搜索条件
    if search:
        search_condition = or_(
            Project.name.contains(search),
            Project.leader.contains(search),
            Project.contract_no.contains(search)
        )
        query = query.filter(search_condition)
    
    # 添加状态筛选
    if status:
        query = query.filter(Project.status == status)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    projects = query.order_by(desc(Project.created_at)).offset(
        (page - 1) * size
    ).limit(size).all()
    
    # 格式化返回数据
    project_list = []
    for project in projects:
        project_list.append({
            "project_id": str(project.id),  # 使用ID作为project_id
            "project_name": project.name,
            "leader": project.leader,
            "status": project.status,
            "progress": project.progress or 0,
            "start_date": project.start_date.isoformat() if project.start_date else None,
            "end_date": project.end_date.isoformat() if project.end_date else None,
            "contract_no": project.contract_no,
            "contract_amount": float(project.contract_amount) if project.contract_amount else 0,
            "created_at": project.created_at.isoformat() if project.created_at else None
        })
    
    return {
        "items": project_list,
        "total": total,
        "page": page,
        "size": size
    }


def get_all_projects(db: Session) -> List[Dict[str, Any]]:
    """
    获取所有项目（用于下拉选择器）
    
    Args:
        db: 数据库会话
    
    Returns:
        项目列表
    """
    query = db.query(Project).filter(Project.is_deleted == False)
    
    projects = query.order_by(Project.name).all()
    
    project_list = []
    for project in projects:
        project_list.append({
            "project_id": str(project.id),  # 使用ID作为project_id，匹配日报中的project_id字段
            "project_name": project.name,
            "leader": project.leader,
            "status": project.status
        })
    
    return project_list


def create_project(db: Session, project_data: ProjectCreate) -> Project:
    """创建项目"""
    # 创建新项目的逻辑
    pass


def update_project(db: Session, project_id: int, project_data: ProjectUpdate) -> Project:
    """更新项目"""
    # 更新项目的逻辑
    pass


def delete_project(db: Session, project_id: int) -> bool:
    """删除项目"""
    # 删除项目的逻辑
    pass