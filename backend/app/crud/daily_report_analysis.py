"""
日报数据分析相关的CRUD操作
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from sqlalchemy.sql import func as sql_func
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.daily_report import DailyReport, DailyWorkItem, DailyReportEvaluation


def get_overview_stats(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    获取分析概览统计数据
    
    Args:
        db: 数据库会话
        start_date: 开始日期
        end_date: 结束日期
        project_id: 项目ID筛选
    
    Returns:
        概览统计数据
    """
    # 基础查询条件
    query_conditions = [
        DailyReport.status == '已提交',
        DailyReport.is_deleted == False,
        DailyWorkItem.is_deleted == False,
        DailyWorkItem.report_id == DailyReport.id
    ]
    
    # 添加日期范围筛选
    if start_date and end_date:
        query_conditions.extend([
            DailyReport.report_date >= start_date,
            DailyReport.report_date <= end_date
        ])
    
    # 添加项目筛选
    if project_id:
        query_conditions.append(DailyWorkItem.project_id == project_id)
    
    # 获取总工时投入
    total_hours_query = db.query(func.sum(DailyWorkItem.hours_spent)).filter(
        *query_conditions
    )
    total_hours = total_hours_query.scalar() or 0
    
    # 获取活跃项目数
    active_projects_query = db.query(func.count(func.distinct(DailyWorkItem.project_id))).filter(
        *query_conditions
    )
    active_projects = active_projects_query.scalar() or 0
    
    # 获取已完成任务数
    completed_tasks_query = db.query(func.count(DailyWorkItem.id)).filter(
        *query_conditions,
        DailyWorkItem.progress_status == '已完成'
    )
    completed_tasks = completed_tasks_query.scalar() or 0
    
    # 获取总任务数
    total_tasks_query = db.query(func.count(DailyWorkItem.id)).filter(*query_conditions)
    total_tasks = total_tasks_query.scalar() or 0
    
    # 计算平均效率
    if total_tasks > 0:
        avg_efficiency = (completed_tasks / total_tasks) * 100
    else:
        avg_efficiency = 0
    
    # 计算变化趋势（简单示例，实际可能需要与历史数据对比）
    hours_change = "+12.3%"
    project_change = "+1"
    task_change = "+23"
    efficiency_trend = 3.2
    
    return {
        "total_hours": float(total_hours),
        "hours_change": hours_change,
        "active_projects": int(active_projects),
        "project_change": project_change,
        "completed_tasks": int(completed_tasks),
        "task_change": task_change,
        "efficiency_rate": round(avg_efficiency, 1),
        "efficiency_trend": efficiency_trend
    }


def get_hours_trend(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    group_by: str = "day",  # day, week, month
    project_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    获取工时趋势数据
    
    Args:
        db: 数据库会话
        start_date: 开始日期
        end_date: 结束日期
        group_by: 分组方式 (day, week, month)
        project_id: 项目ID筛选
    
    Returns:
        趋势数据列表
    """
    try:
        # 基础查询条件
        query_conditions = [
            DailyReport.status == '已提交',
            DailyReport.is_deleted == False,
            DailyWorkItem.is_deleted == False,
            DailyWorkItem.report_id == DailyReport.id,
            DailyReport.report_date >= start_date,
            DailyReport.report_date <= end_date
        ]
        
        if project_id:
            query_conditions.append(DailyWorkItem.project_id == project_id)
        
        # 简化查询 - 先获取基础数据
        base_query = db.query(
            DailyReport.report_date,
            func.sum(DailyWorkItem.hours_spent).label('total_hours'),
            func.count(func.distinct(DailyWorkItem.project_id)).label('project_count'),
            func.count(func.distinct(DailyReport.employee_id)).label('employee_count')
        ).filter(*query_conditions).group_by(DailyReport.report_date)
        
        results = base_query.all()
        
        # 格式化返回数据
        trend_data = []
        for result in results:
            date_str = result.report_date.strftime('%Y-%m-%d') if result.report_date else ''
            trend_data.append({
                "date": date_str,
                "total_hours": float(result.total_hours or 0),
                "project_count": int(result.project_count or 0),
                "employee_count": int(result.employee_count or 0)
            })
        
        # 按日期排序
        trend_data.sort(key=lambda x: x['date'])
        
        return trend_data
    
    except Exception as e:
        print(f"工时趋势查询错误: {str(e)}")
        # 返回空数据而不是抛出异常
        return []


def get_project_hours_distribution(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    获取项目工时分布数据
    
    Args:
        db: 数据库会话
        start_date: 开始日期
        end_date: 结束日期
        limit: 返回数量限制
    
    Returns:
        项目工时分布数据
    """
    # 基础查询条件
    query_conditions = [
        DailyReport.status == '已提交',
        DailyReport.is_deleted == False,
        DailyWorkItem.is_deleted == False,
        DailyWorkItem.report_id == DailyReport.id
    ]
    
    if start_date and end_date:
        query_conditions.extend([
            DailyReport.report_date >= start_date,
            DailyReport.report_date <= end_date
        ])
    
    query = db.query(
        DailyWorkItem.project_id,
        DailyWorkItem.project_name,
        func.sum(DailyWorkItem.hours_spent).label('total_hours'),
        func.count(func.distinct(DailyReport.employee_id)).label('employee_count'),
        func.count(DailyWorkItem.id).label('task_count'),
        func.avg(DailyWorkItem.progress_percentage).label('avg_progress')
    ).filter(*query_conditions).group_by(
        DailyWorkItem.project_id,
        DailyWorkItem.project_name
    ).order_by(desc('total_hours')).limit(limit)
    
    results = query.all()
    
    # 计算总工时用于计算百分比
    total_hours = sum([r.total_hours for r in results]) or 1
    
    distribution_data = []
    for result in results:
        percentage = round((result.total_hours / total_hours) * 100, 1)
        avg_hours_per_employee = float(result.total_hours) / max(result.employee_count, 1)
        avg_progress = float(result.avg_progress or 0)
        
        # 计算完成率
        completion_query = db.query(func.count(DailyWorkItem.id)).filter(
            *query_conditions,
            DailyWorkItem.project_id == result.project_id,
            DailyWorkItem.progress_status == '已完成'
        )
        completed_count = completion_query.scalar() or 0
        
        total_count_query = db.query(func.count(DailyWorkItem.id)).filter(
            *query_conditions,
            DailyWorkItem.project_id == result.project_id
        )
        total_count = total_count_query.scalar() or 1
        
        completion_rate = round((completed_count / total_count) * 100, 1)
        
        distribution_data.append({
            "project_id": result.project_id,
            "project_name": result.project_name,
            "total_hours": float(result.total_hours or 0),
            "employee_count": int(result.employee_count or 0),
            "task_count": int(result.task_count or 0),
            "avg_progress": round(avg_progress, 1),
            "avg_hours_per_employee": round(avg_hours_per_employee, 1),
            "completion_rate": completion_rate,
            "percentage": percentage
        })
    
    return distribution_data


def get_employee_hours_ranking(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 20,
    project_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    获取人员工时排名数据
    
    Args:
        db: 数据库会话
        start_date: 开始日期
        end_date: 结束日期
        limit: 返回数量限制
        project_id: 项目ID筛选
    
    Returns:
        人员工时排名数据
    """
    # 基础查询条件
    query_conditions = [
        DailyReport.status == '已提交',
        DailyReport.is_deleted == False,
        DailyWorkItem.is_deleted == False,
        DailyWorkItem.report_id == DailyReport.id
    ]
    
    if start_date and end_date:
        query_conditions.extend([
            DailyReport.report_date >= start_date,
            DailyReport.report_date <= end_date
        ])
    
    if project_id:
        query_conditions.append(DailyWorkItem.project_id == project_id)
    
    query = db.query(
        DailyReport.employee_id,
        DailyReport.employee_name,
        func.sum(DailyWorkItem.hours_spent).label('total_hours'),
        func.count(func.distinct(DailyWorkItem.project_id)).label('projects_count'),
        func.count(DailyWorkItem.id).label('tasks_count'),
        func.avg(DailyWorkItem.progress_percentage).label('avg_progress')
    ).filter(*query_conditions).group_by(
        DailyReport.employee_id,
        DailyReport.employee_name
    ).order_by(desc('total_hours')).limit(limit)
    
    results = query.all()
    
    ranking_data = []
    for i, result in enumerate(results, 1):
        # 计算效率评分（基于平均进度和工时投入）
        efficiency_score = min(5.0, max(1.0, float(result.avg_progress or 0) / 20))
        
        # 确定工作负荷等级
        workload_level = "正常"
        if result.total_hours > 160:  # 超过标准工时
            workload_level = "较重"
        elif result.total_hours < 80:  # 低于标准工时
            workload_level = "较轻"
        
        ranking_data.append({
            "employee_id": result.employee_id,
            "employee_name": result.employee_name,
            "total_hours": float(result.total_hours or 0),
            "projects_count": int(result.projects_count or 0),
            "tasks_count": int(result.tasks_count or 0),
            "avg_progress": round(float(result.avg_progress or 0), 1),
            "efficiency_score": round(efficiency_score, 1),
            "workload_level": workload_level,
            "ranking": i
        })
    
    return ranking_data


def get_task_completion_analysis(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    获取任务完成率分析数据
    
    Args:
        db: 数据库会话
        start_date: 开始日期
        end_date: 结束日期
        project_id: 项目ID筛选
    
    Returns:
        任务完成率分析数据
    """
    # 基础查询条件
    query_conditions = [
        DailyReport.status == '已提交',
        DailyReport.is_deleted == False,
        DailyWorkItem.is_deleted == False,
        DailyWorkItem.report_id == DailyReport.id
    ]
    
    if start_date and end_date:
        query_conditions.extend([
            DailyReport.report_date >= start_date,
            DailyReport.report_date <= end_date
        ])
    
    if project_id:
        query_conditions.append(DailyWorkItem.project_id == project_id)
    
    # 获取状态统计
    status_query = db.query(
        DailyWorkItem.progress_status,
        func.count(DailyWorkItem.id)
    ).filter(*query_conditions).group_by(DailyWorkItem.progress_status)
    
    results = status_query.all()
    
    # 统计各状态的任务数量
    status_counts = {result.progress_status: result.count for result in results}
    
    total_tasks = sum(status_counts.values())
    completed_tasks = status_counts.get('已完成', 0)
    in_progress_tasks = status_counts.get('进行中', 0)
    pending_tasks = status_counts.get('待开始', 0)
    delayed_tasks = status_counts.get('延期', 0)
    
    # 计算完成率
    completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "pending_tasks": pending_tasks,
        "delayed_tasks": delayed_tasks,
        "completion_rate": completion_rate,
        "status_counts": status_counts
    }


def get_evaluation_analysis(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    获取评价数据分析
    
    Args:
        db: 数据库会话
        start_date: 开始日期
        end_date: 结束日期
        project_id: 项目ID筛选
    
    Returns:
        评价分析数据
    """
    # 基础查询条件
    query_conditions = [
        DailyReportEvaluation.is_deleted == False,
        DailyReportEvaluation.report_id == DailyReport.id
    ]
    
    # 添加日期范围筛选
    if start_date and end_date:
        query_conditions.extend([
            DailyReport.report_date >= start_date,
            DailyReport.report_date <= end_date
        ])
    
    # 添加项目筛选
    if project_id:
        query_conditions.append(DailyWorkItem.project_id == project_id)
    
    # 获取评价统计
    evaluation_query = db.query(
        func.avg(DailyReportEvaluation.supervisor_score).label('avg_score'),
        func.count(DailyReportEvaluation.id).label('total_evaluations'),
        func.count(func.distinct(DailyReportEvaluation.supervisor_id)).label('total_supervisors')
    ).filter(*query_conditions)
    
    result = evaluation_query.first()
    avg_score = float(result.avg_score or 0)
    total_evaluations = int(result.total_evaluations or 0)
    total_supervisors = int(result.total_supervisors or 0)
    
    # 获取评分分布
    score_distribution_query = db.query(
        DailyReportEvaluation.supervisor_score,
        func.count(DailyReportEvaluation.id).label('count')
    ).filter(*query_conditions).group_by(DailyReportEvaluation.supervisor_score)
    
    score_results = score_distribution_query.all()
    score_distribution = {}
    for score_result in score_results:
        score = score_result.supervisor_score
        count = score_result.count
        score_distribution[f"score_{score}"] = count
    
    # 获取主管评价排名
    supervisor_ranking_query = db.query(
        DailyReportEvaluation.supervisor_id,
        DailyReportEvaluation.supervisor_name,
        func.avg(DailyReportEvaluation.supervisor_score).label('avg_score'),
        func.count(DailyReportEvaluation.id).label('evaluation_count')
    ).filter(*query_conditions).group_by(
        DailyReportEvaluation.supervisor_id,
        DailyReportEvaluation.supervisor_name
    ).order_by(desc('avg_score')).limit(10)
    
    supervisor_results = supervisor_ranking_query.all()
    supervisor_ranking = []
    for i, supervisor_result in enumerate(supervisor_results, 1):
        supervisor_ranking.append({
            "supervisor_id": supervisor_result.supervisor_id,
            "supervisor_name": supervisor_result.supervisor_name,
            "avg_score": round(float(supervisor_result.avg_score or 0), 1),
            "evaluation_count": int(supervisor_result.evaluation_count or 0),
            "ranking": i
        })
    
    # 获取员工评价排名
    employee_evaluation_query = db.query(
        DailyReport.employee_id,
        DailyReport.employee_name,
        func.avg(DailyReportEvaluation.supervisor_score).label('avg_score'),
        func.count(DailyReportEvaluation.id).label('evaluation_count')
    ).filter(*query_conditions).group_by(
        DailyReport.employee_id,
        DailyReport.employee_name
    ).order_by(desc('avg_score')).limit(10)
    
    employee_results = employee_evaluation_query.all()
    employee_evaluation_ranking = []
    for i, employee_result in enumerate(employee_results, 1):
        employee_evaluation_ranking.append({
            "employee_id": employee_result.employee_id,
            "employee_name": employee_result.employee_name,
            "avg_score": round(float(employee_result.avg_score or 0), 1),
            "evaluation_count": int(employee_result.evaluation_count or 0),
            "ranking": i
        })
    
    # 计算评价质量指标
    high_quality_count = 0
    for score_result in score_results:
        if score_result.supervisor_score >= 4:
            high_quality_count += score_result.count
    
    quality_rate = round((high_quality_count / total_evaluations * 100), 1) if total_evaluations > 0 else 0
    
    return {
        "avg_score": round(avg_score, 1),
        "total_evaluations": total_evaluations,
        "total_supervisors": total_supervisors,
        "score_distribution": score_distribution,
        "supervisor_ranking": supervisor_ranking,
        "employee_evaluation_ranking": employee_evaluation_ranking,
        "quality_rate": quality_rate,
        "high_quality_count": high_quality_count
    }


def get_analysis_projects_list(db: Session) -> List[Dict[str, Any]]:
    """
    获取项目列表，用于分析筛选器
    优先使用 projects 表的数据，如果找不到则使用日报中的项目信息
    
    Args:
        db: 数据库会话
    
    Returns:
        项目列表数据
    """
    # 首先从日报中获取所有项目信息
    daily_projects_query = db.query(
        DailyWorkItem.project_id,
        DailyWorkItem.project_name,
        func.sum(DailyWorkItem.hours_spent).label('total_hours'),
        func.count(func.distinct(DailyWorkItem.report_id)).label('report_count')
    ).join(
        DailyReport, DailyWorkItem.report_id == DailyReport.id
    ).filter(
        DailyReport.status == '已提交',
        DailyReport.is_deleted == False,
        DailyWorkItem.is_deleted == False,
        DailyWorkItem.project_id.isnot(None),
        DailyWorkItem.project_name.isnot(None)
    ).group_by(
        DailyWorkItem.project_id,
        DailyWorkItem.project_name
    ).order_by(desc('total_hours'))
    
    daily_results = daily_projects_query.all()
    
    projects = []
    seen_project_ids = set()  # 用于避免重复
    
    # 处理日报中的项目数据
    for result in daily_results:
        project_id = result.project_id
        if project_id not in seen_project_ids:
            projects.append({
                "project_id": project_id,
                "project_name": result.project_name,
                "total_hours": float(result.total_hours or 0),
                "report_count": int(result.report_count or 0)
            })
            seen_project_ids.add(project_id)
    
    # 如果日报数据为空，尝试从 projects 表获取项目
    if not projects:
        try:
            from app.models.project import Project
            projects_query = db.query(Project).filter(
                Project.is_deleted == False
            ).order_by(Project.name).limit(20)
            
            project_results = projects_query.all()
            for project in project_results:
                projects.append({
                    "project_id": str(project.id),
                    "project_name": project.name,
                    "total_hours": 0,
                    "report_count": 0
                })
        except Exception as e:
            print(f"从 projects 表获取项目失败: {str(e)}")
    
    return projects