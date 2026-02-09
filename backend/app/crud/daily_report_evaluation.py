from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from app.models.daily_report import DailyReport, DailyReportEvaluation
from app.models.daily_report import DailyWorkItem
from app.models.resource import Personnel


def get_subordinate_reports(
    db: Session,
    supervisor_id: str,
    employee_name: Optional[str] = None,
    department: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    获取管辖员工的日报列表
    """
    # 首先获取当前用户管辖的员工列表
    from app.models.resource import EmployeeGroupRelation
    
    # 获取当前用户作为上级的所有分组
    supervised_groups = db.query(EmployeeGroupRelation).filter(
        EmployeeGroupRelation.employee_id == supervisor_id,
        EmployeeGroupRelation.relation_type == 'supervisor'
    ).all()
    
    if not supervised_groups:
        # 如果用户没有管辖任何分组，返回空列表
        return []
    
    group_names = [group.group_name for group in supervised_groups]
    
    # 构建查询：找到在这些分组中的所有成员
    subordinate_employee_ids = db.query(EmployeeGroupRelation.employee_id).filter(
        EmployeeGroupRelation.group_name.in_(group_names),
        EmployeeGroupRelation.relation_type == 'member',
        EmployeeGroupRelation.employee_id != 'GROUP_EMPTY'  # 排除空分组标记
    ).distinct().all()
    
    subordinate_ids = [row[0] for row in subordinate_employee_ids]
    
    if not subordinate_ids:
        # 如果没有下级员工，返回空列表
        return []
    
    # 构建基础查询，限制在管辖员工范围内
    query = db.query(DailyReport).join(
        Personnel, 
        DailyReport.employee_id == Personnel.employee_id
    ).filter(
        DailyReport.employee_id.in_(subordinate_ids)  # 只查询管辖员工
    )
    
    # 应用筛选条件
    if employee_name:
        query = query.filter(DailyReport.employee_name.ilike(f"%{employee_name}%"))
    
    if department:
        query = query.filter(Personnel.department.ilike(f"%{department}%"))
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(DailyReport.report_date >= start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(DailyReport.report_date <= end_date_obj)
        except ValueError:
            pass
    
    # 添加状态筛选，支持多种状态
    if status:
        query = query.filter(DailyReport.status == status)
    else:
        # 默认显示已提交和已评价的日报
        query = query.filter(DailyReport.status.in_(['已提交', '已评价']))
    
    # 按日期倒序排列
    query = query.order_by(DailyReport.report_date.desc())
    
    # 执行查询
    reports = query.all()
    
    # 处理每个日报，添加评价和工作项目信息
    result = []
    for report in reports:
        # 重新获取personnel信息以确保有数据
        personnel_info = db.query(Personnel).filter(
            Personnel.employee_id == report.employee_id
        ).first()
        
        # 获取评价信息
        evaluation = db.query(DailyReportEvaluation).filter(
            DailyReportEvaluation.report_id == report.id
        ).first()
        
        # 获取工作项目信息
        work_items = db.query(DailyWorkItem).filter(
            DailyWorkItem.report_id == report.id
        ).all()
        
        # 构建响应数据
        report_data = {
            "id": report.id,
            "report_date": report.report_date.strftime("%Y-%m-%d"),
            "employee_id": report.employee_id,
            "employee_name": report.employee_name,
            "department": personnel_info.department if personnel_info else "",
            "position": personnel_info.position if personnel_info else "",
            "work_target": report.work_target or "",  # 添加工作目标字段
            "self_evaluation": report.self_evaluation or "",  # 添加自我评价字段
            "tomorrow_plan": report.tomorrow_plan or "",
            "planned_hours": float(report.planned_hours or 0),
            "status": report.status,  # 添加状态字段
            "work_items": [
                {
                    "work_content": item.work_content,
                    "start_time": item.start_time.strftime("%H:%M") if item.start_time else "",
                    "end_time": item.end_time.strftime("%H:%M") if item.end_time else "",
                    "result": item.result or "",
                    "evaluation": item.evaluation or ""
                }
                for item in work_items
            ],
            "evaluation": {
                "supervisor_score": evaluation.supervisor_score,
                "supervisor_comment": evaluation.supervisor_comment or "",
                "supervisor_id": evaluation.supervisor_id,
                "supervisor_name": evaluation.supervisor_name,
                "evaluated_at": evaluation.evaluated_at.strftime("%Y-%m-%d %H:%M:%S")
            } if evaluation else None
        }
        
        result.append(report_data)
    
    return result


def get_evaluation_stats(
    db: Session,
    supervisor_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    获取评价统计数据
    """
    # 首先获取管辖员工列表
    from app.models.resource import EmployeeGroupRelation
    
    # 获取当前用户作为上级的所有分组
    supervised_groups = db.query(EmployeeGroupRelation).filter(
        EmployeeGroupRelation.employee_id == supervisor_id,
        EmployeeGroupRelation.relation_type == 'supervisor'
    ).all()
    
    subordinate_ids = []
    if supervised_groups:
        group_names = [group.group_name for group in supervised_groups]
        subordinate_employee_ids = db.query(EmployeeGroupRelation.employee_id).filter(
            EmployeeGroupRelation.group_name.in_(group_names),
            EmployeeGroupRelation.relation_type == 'member',
            EmployeeGroupRelation.employee_id != 'GROUP_EMPTY'
        ).distinct().all()
        subordinate_ids = [row[0] for row in subordinate_employee_ids]
    
    if not subordinate_ids:
        return {
            "pending_count": 0,
            "evaluated_count": 0,
            "total_count": 0
        }
    
    # 获取基础查询，限制在管辖员工范围内
    query = db.query(DailyReport).filter(
        DailyReport.employee_id.in_(subordinate_ids)  # 只统计管辖员工
    )
    
    # 统计已提交和已评价的日报（与列表保持一致）
    query = query.filter(DailyReport.status.in_(['已提交', '已评价']))
    
    # 应用日期筛选
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(DailyReport.report_date >= start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(DailyReport.report_date <= end_date_obj)
        except ValueError:
            pass
    
    # 获取日报总数
    total_reports = query.count()
    
    # 获取已评价的日报数量（同样应用筛选条件）
    evaluated_query = db.query(func.count(DailyReportEvaluation.id)).join(
        DailyReport,
        DailyReportEvaluation.report_id == DailyReport.id
    ).filter(
        DailyReport.employee_id.in_(subordinate_ids),  # 只统计管辖员工的评价
        DailyReport.status.in_(['已提交', '已评价'])  # 统计已提交和已评价的日报
    )
    
    # 应用日期筛选到已评价统计
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            evaluated_query = evaluated_query.filter(DailyReport.report_date >= start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            evaluated_query = evaluated_query.filter(DailyReport.report_date <= end_date_obj)
        except ValueError:
            pass
    
    evaluated_reports = evaluated_query.scalar() or 0
    pending_reports = total_reports - evaluated_reports
    
    # 计算评价进度
    progress = round((evaluated_reports / total_reports * 100), 2) if total_reports > 0 else 0
    
    return {
        "pending_count": pending_reports,
        "evaluated_count": evaluated_reports,
        "total_count": total_reports,
        "progress": progress
    }


def create_evaluation(
    db: Session,
    report_id: int,
    supervisor_id: str,
    supervisor_name: str,
    score: str,
    comment: str
) -> Dict[str, Any]:
    """
    创建评价记录，并更新日报状态为已评价
    """
    # 检查是否已经存在评价
    existing_evaluation = db.query(DailyReportEvaluation).filter(
        DailyReportEvaluation.report_id == report_id,
        DailyReportEvaluation.supervisor_id == supervisor_id
    ).first()
    
    if existing_evaluation:
        raise ValueError("该用户已对此日报进行过评价")
    
    # 创建评价记录
    evaluation = DailyReportEvaluation(
        report_id=report_id,
        supervisor_score=score,
        supervisor_comment=comment,
        supervisor_id=supervisor_id,
        supervisor_name=supervisor_name,
        evaluated_at=datetime.now()
    )
    
    db.add(evaluation)
    
    # 同时更新日报状态为已评价
    daily_report = db.query(DailyReport).filter(DailyReport.id == report_id).first()
    if daily_report:
        daily_report.status = "已评价"
    
    db.commit()
    db.refresh(evaluation)
    
    return {
        "id": evaluation.id,
        "report_id": evaluation.report_id,
        "supervisor_score": evaluation.supervisor_score,
        "supervisor_comment": evaluation.supervisor_comment or "",
        "supervisor_id": evaluation.supervisor_id,
        "supervisor_name": evaluation.supervisor_name,
        "evaluated_at": evaluation.evaluated_at.strftime("%Y-%m-%d %H:%M:%S")
    }


def get_report_with_evaluation(
    db: Session,
    report_id: int
) -> Optional[Dict[str, Any]]:
    """
    获取日报详情（包含评价）
    """
    report = db.query(DailyReport).filter(DailyReport.id == report_id).first()
    if not report:
        return None
    
    # 获取评价信息
    evaluation = db.query(DailyReportEvaluation).filter(
        DailyReportEvaluation.report_id == report_id
    ).first()
    
    # 获取工作项目信息
    work_items = db.query(DailyWorkItem).filter(
        DailyWorkItem.report_id == report_id
    ).all()
    
    # 获取personnel信息
    personnel_info = db.query(Personnel).filter(
        Personnel.employee_id == report.employee_id
    ).first()
    
    # 构建响应数据
    report_data = {
        "id": report.id,
        "report_date": report.report_date.strftime("%Y-%m-%d"),
        "employee_id": report.employee_id,
        "employee_name": report.employee_name,
        "department": personnel_info.department if personnel_info else "",
        "position": personnel_info.position if personnel_info else "",
        "work_target": report.work_target or "",
        "key_work_tracking": report.key_work_tracking or "",
        "tomorrow_plan": report.tomorrow_plan or "",
        "planned_hours": float(report.planned_hours or 0),
        "status": report.status,  # 添加状态字段
        "work_items": [
            {
                "work_content": item.work_content,
                "start_time": item.start_time.strftime("%H:%M") if item.start_time else "",
                "end_time": item.end_time.strftime("%H:%M") if item.end_time else "",
                "result": item.result or "",
                "evaluation": item.evaluation or ""
            }
            for item in work_items
        ],
        "evaluation": {
            "supervisor_score": evaluation.supervisor_score,
            "supervisor_comment": evaluation.supervisor_comment or "",
            "supervisor_id": evaluation.supervisor_id,
            "supervisor_name": evaluation.supervisor_name,
            "evaluated_at": evaluation.evaluated_at.strftime("%Y-%m-%d %H:%M:%S")
        } if evaluation else None
    }
    
    return report_data


def get_evaluation_history(
    db: Session,
    supervisor_id: str,
    employee_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    limit: int = 10
) -> Dict[str, Any]:
    """
    获取评价历史
    """
    # 构建基础查询
    query = db.query(DailyReportEvaluation).join(
        DailyReport,
        DailyReportEvaluation.report_id == DailyReport.id
    )
    
    # 应用筛选条件
    if employee_id:
        query = query.filter(DailyReport.employee_id == employee_id)
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(DailyReport.report_date >= start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(DailyReport.report_date <= end_date_obj)
        except ValueError:
            pass
    
    # 获取总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * limit
    evaluations = query.offset(offset).limit(limit).all()
    
    # 构建响应数据
    items = []
    for evaluation in evaluations:
        # 获取日报信息
        report = db.query(DailyReport).filter(DailyReport.id == evaluation.report_id).first()
        
        item = {
            "supervisor_score": evaluation.supervisor_score,
            "supervisor_comment": evaluation.supervisor_comment or "",
            "supervisor_id": evaluation.supervisor_id,
            "supervisor_name": evaluation.supervisor_name,
            "evaluated_at": evaluation.evaluated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "report_date": report.report_date.strftime("%Y-%m-%d") if report else "",
            "employee_name": report.employee_name if report else "",
            "employee_id": report.employee_id if report else ""
        }
        items.append(item)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit
    }


def update_evaluation(
    db: Session,
    evaluation_id: int,
    score: Optional[int] = None,
    comment: Optional[str] = None
) -> Dict[str, Any]:
    """
    更新评价记录
    """
    evaluation = db.query(DailyReportEvaluation).filter(
        DailyReportEvaluation.id == evaluation_id
    ).first()
    
    if not evaluation:
        raise ValueError("评价记录不存在")
    
    # 更新字段
    if score is not None:
        evaluation.supervisor_score = score
    
    if comment is not None:
        evaluation.supervisor_comment = comment
    
    db.commit()
    db.refresh(evaluation)
    
    return {
        "id": evaluation.id,
        "report_id": evaluation.report_id,
        "supervisor_score": evaluation.supervisor_score,
        "supervisor_comment": evaluation.supervisor_comment or "",
        "supervisor_id": evaluation.supervisor_id,
        "supervisor_name": evaluation.supervisor_name,
        "evaluated_at": evaluation.evaluated_at.strftime("%Y-%m-%d %H:%M:%S")
    }


def delete_evaluation(db: Session, evaluation_id: int):
    """
    删除评价记录
    """
    evaluation = db.query(DailyReportEvaluation).filter(
        DailyReportEvaluation.id == evaluation_id
    ).first()
    
    if not evaluation:
        raise ValueError("评价记录不存在")
    
    db.delete(evaluation)
    db.commit()