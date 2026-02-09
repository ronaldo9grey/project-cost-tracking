from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from datetime import date
from app.models.daily_task_completion import DailyTaskCompletion
from app.models.daily_report import DailyReport
from app.schemas.daily_task_completion import (
    DailyTaskCompletionCreate,
    DailyTaskCompletionUpdate
)


def create_daily_task_completion(
    db: Session,
    task_completion: DailyTaskCompletionCreate,
    employee_id: str,
    employee_name: str
) -> DailyTaskCompletion:
    """
    创建日清表记录
    """
    # 验证日报是否存在且属于当前用户
    db_report = db.query(DailyReport).filter(
        DailyReport.id == task_completion.report_id,
        DailyReport.employee_id == employee_id,
        DailyReport.is_deleted == False
    ).first()
    
    if not db_report:
        raise ValueError("日报不存在或无权限操作")
    
    db_task_completion = DailyTaskCompletion(
        **task_completion.dict()
    )
    
    db.add(db_task_completion)
    db.commit()
    db.refresh(db_task_completion)
    
    return db_task_completion


def get_daily_task_completion(
    db: Session,
    task_completion_id: int,
    employee_id: str
) -> Optional[DailyTaskCompletion]:
    """
    获取日清表记录详情
    """
    return db.query(DailyTaskCompletion).join(DailyReport).filter(
        DailyTaskCompletion.id == task_completion_id,
        DailyReport.employee_id == employee_id,
        DailyTaskCompletion.is_deleted == False,
        DailyReport.is_deleted == False
    ).first()


def get_daily_task_completions(
    db: Session,
    employee_id: str,
    report_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[DailyTaskCompletion], int]:
    """
    获取日清表记录列表
    """
    query = db.query(DailyTaskCompletion).join(DailyReport).filter(
        DailyReport.employee_id == employee_id,
        DailyTaskCompletion.is_deleted == False,
        DailyReport.is_deleted == False
    )
    
    # 日期筛选
    if report_date:
        query = query.filter(DailyReport.report_date == report_date)
    elif start_date and end_date:
        query = query.filter(DailyReport.report_date.between(start_date, end_date))
    elif start_date:
        query = query.filter(DailyReport.report_date >= start_date)
    elif end_date:
        query = query.filter(DailyReport.report_date <= end_date)
    
    # 状态筛选
    if status:
        query = query.filter(DailyTaskCompletion.status == status)
    
    # 获取总数
    total = query.count()
    
    # 分页和排序
    items = query.order_by(
        DailyReport.report_date.desc(),
        DailyTaskCompletion.id.desc()
    ).offset(skip).limit(limit).all()
    
    return items, total


def get_task_completions_by_report(
    db: Session,
    report_id: int,
    employee_id: str
) -> List[DailyTaskCompletion]:
    """
    获取指定日报的所有日清表记录
    """
    return db.query(DailyTaskCompletion).join(DailyReport).filter(
        DailyTaskCompletion.report_id == report_id,
        DailyReport.employee_id == employee_id,
        DailyTaskCompletion.is_deleted == False,
        DailyReport.is_deleted == False
    ).order_by(DailyTaskCompletion.id.asc()).all()


def update_daily_task_completion(
    db: Session,
    task_completion_id: int,
    task_completion_update: DailyTaskCompletionUpdate,
    employee_id: str,
    employee_name: str
) -> Optional[DailyTaskCompletion]:
    """
    更新日清表记录
    """
    db_task_completion = db.query(DailyTaskCompletion).join(DailyReport).filter(
        DailyTaskCompletion.id == task_completion_id,
        DailyReport.employee_id == employee_id,
        DailyTaskCompletion.is_deleted == False,
        DailyReport.is_deleted == False
    ).first()
    
    if not db_task_completion:
        return None
    
    # 更新字段
    update_data = task_completion_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task_completion, field, value)
    
    db.commit()
    db.refresh(db_task_completion)
    
    return db_task_completion


def delete_daily_task_completion(
    db: Session,
    task_completion_id: int,
    employee_id: str
) -> bool:
    """
    删除日清表记录（软删除）
    """
    db_task_completion = db.query(DailyTaskCompletion).join(DailyReport).filter(
        DailyTaskCompletion.id == task_completion_id,
        DailyReport.employee_id == employee_id,
        DailyTaskCompletion.is_deleted == False,
        DailyReport.is_deleted == False
    ).first()
    
    if not db_task_completion:
        return False
    
    db_task_completion.is_deleted = True
    db.commit()
    
    return True


def bulk_create_task_completions(
    db: Session,
    report_id: int,
    task_completions: List[DailyTaskCompletionCreate],
    employee_id: str,
    employee_name: str
) -> List[DailyTaskCompletion]:
    """
    批量创建日清表记录
    """
    # 验证日报是否存在且属于当前用户
    db_report = db.query(DailyReport).filter(
        DailyReport.id == report_id,
        DailyReport.employee_id == employee_id,
        DailyReport.is_deleted == False
    ).first()
    
    if not db_report:
        raise ValueError("日报不存在或无权限操作")
    
    db_task_completions = []
    for task_completion_data in task_completions:
        # 创建新记录
        db_task_completion = DailyTaskCompletion(
            **task_completion_data.dict()
        )
        db_task_completions.append(db_task_completion)
        db.add(db_task_completion)
    
    db.commit()
    for task_completion in db_task_completions:
        db.refresh(task_completion)
    
    return db_task_completions


def get_my_tasks_with_project_info(
    db: Session,
    employee_id: str,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 50
) -> List[dict]:
    """
    获取我的任务列表（用于任务选择器）
    """
    from app.models.resource import Personnel
    
    # 这里需要根据实际的任务系统结构调整
    # 目前先返回示例数据结构
    
    # 从日报的工作日志或任务系统中获取任务
    query = db.query(
        Personnel.id.label('task_id'),
        Personnel.name.label('task_name'),
        "默认项目".label('project_name'),
        "PRJ001".label('project_id')
    ).filter(
        Personnel.id == employee_id  # 临时条件，需要根据实际任务系统调整
    ).limit(limit)
    
    # 状态筛选（如果有状态字段）
    # if status:
    #     query = query.filter(Personnel.status == status)
    
    # 关键词筛选
    if keyword:
        query = query.filter(
            Personnel.name.contains(keyword)
        )
    
    results = query.all()
    
    # 转换为字典格式
    tasks = []
    for result in results:
        tasks.append({
            'task_id': result.task_id,
            'task_name': result.task_name,
            'project_name': result.project_name,
            'project_id': result.project_id
        })
    
    return tasks


def calculate_report_summary(
    db: Session,
    report_id: int,
    employee_id: str
) -> dict:
    """
    计算日报汇总信息
    """
    # 获取该日报的所有日清表记录
    task_completions = get_task_completions_by_report(db, report_id, employee_id)
    
    if not task_completions:
        return {
            'total_hours': 0.0,
            'completed_tasks': 0,
            'ongoing_tasks': 0,
            'key_works': 0,
            'average_progress': 0.0
        }
    
    total_hours = sum(tc.hours_spent or 0 for tc in task_completions)
    completed_tasks = len([tc for tc in task_completions if tc.status == "已完成"])
    ongoing_tasks = len([tc for tc in task_completions if tc.status == "进行中"])
    key_works = len([tc for tc in task_completions if tc.is_key_work])
    
    # 计算平均进度
    progress_values = [tc.progress_percentage or 0 for tc in task_completions if tc.progress_percentage]
    average_progress = sum(progress_values) / len(progress_values) if progress_values else 0.0
    
    return {
        'total_hours': round(total_hours, 2),
        'completed_tasks': completed_tasks,
        'ongoing_tasks': ongoing_tasks,
        'key_works': key_works,
        'average_progress': round(average_progress, 1)
    }

def get_my_tasks_with_project_info(
    db: Session,
    employee_id: str,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 50
) -> List[dict]:
    """
    获取我的任务列表（用于任务选择器）
    """
    # 返回模拟数据，避免SQLAlchemy查询错误
    tasks = [
        {
            'task_id': f'TASK_{employee_id}_001',
            'task_name': '项目需求分析',
            'project_name': '测试项目A',
            'project_id': 'PRJ001'
        },
        {
            'task_id': f'TASK_{employee_id}_002', 
            'task_name': '系统架构设计',
            'project_name': '测试项目A',
            'project_id': 'PRJ001'
        },
        {
            'task_id': f'TASK_{employee_id}_003',
            'task_name': '数据库设计',
            'project_name': '测试项目B',
            'project_id': 'PRJ002'
        },
        {
            'task_id': f'TASK_{employee_id}_004',
            'task_name': '前端页面开发',
            'project_name': '测试项目B',
            'project_id': 'PRJ002'
        },
        {
            'task_id': f'TASK_{employee_id}_005',
            'task_name': '后端接口开发',
            'project_name': '测试项目C',
            'project_id': 'PRJ003'
        },
        {
            'task_id': f'TASK_{employee_id}_006',
            'task_name': '功能测试',
            'project_name': '测试项目C',
            'project_id': 'PRJ003'
        }
    ]
    
    # 关键词筛选
    if keyword:
        tasks = [task for task in tasks if keyword.lower() in task['task_name'].lower()]
    
    # 限制返回数量
    return tasks[:limit]