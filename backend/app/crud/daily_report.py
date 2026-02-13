from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Tuple, Dict, Any
from datetime import date, datetime
from app.models.daily_report import DailyReport, DailyWorkItem, DailyWorkLog
from app.models.project import Project
from app.models.project_task import ProjectTask
from app.schemas.daily_report import DailyReportCreate, DailyReportUpdate, DailyWorkLogCreate, DailyReportResponse, DailyReportListResponse, DailyReportEvaluate, DailyReportWithItemsCreate


def get_daily_reports(
    db: Session,
    employee_id: Optional[str] = None,
    report_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
) -> Tuple[List[DailyReport], int]:
    query = db.query(DailyReport).filter(DailyReport.is_deleted == False)
    
    if employee_id:
        query = query.filter(DailyReport.employee_id == employee_id)
    if report_date:
        query = query.filter(DailyReport.report_date == report_date)
    if start_date:
        query = query.filter(DailyReport.report_date >= start_date)
    if end_date:
        query = query.filter(DailyReport.report_date <= end_date)
    if status:
        query = query.filter(DailyReport.status == status)
    
    total = query.count()
    reports = query.order_by(DailyReport.report_date.desc(), DailyReport.create_time.desc()).offset(skip).limit(limit).all()
    
    return reports, total


def get_daily_report(db: Session, report_id: int, as_dict: bool = False) -> Optional[DailyReport]:
    db_report = db.query(DailyReport).filter(
        DailyReport.id == report_id,
        DailyReport.is_deleted == False
    ).first()
    
    if not db_report or not as_dict:
        return db_report
    
    # 转换为字典格式并处理时间字段序列化
    work_items = []
    for item in db_report.work_items:
        work_item = {
            "id": item.id,
            "report_id": item.report_id,
            "work_content": item.work_content,
            "start_time": item.start_time.strftime('%H:%M') if hasattr(item.start_time, 'strftime') else str(item.start_time) if item.start_time else "",
            "end_time": item.end_time.strftime('%H:%M') if hasattr(item.end_time, 'strftime') else str(item.end_time) if item.end_time else "",
            "result": item.result or "",
            "measures": item.measures or "",
            "evaluation": item.evaluation or "",
            "project_id": item.project_id or "",
            "project_name": item.project_name or "",
            "task_id": item.task_id or "",
            "task_name": item.task_name or "",
            "key_work_tracking": item.key_work_tracking or "",
            "hours_spent": float(item.hours_spent) if item.hours_spent else 0.0,
            "progress_status": item.progress_status or "正常",
            "progress_percentage": float(item.progress_percentage) if item.progress_percentage else 0.0,
            "delay_hours": float(item.delay_hours) if item.delay_hours else 0.0,
            "improvement_result": item.improvement_result or ""
        }
        work_items.append(work_item)
    
    # 构建响应字典
    report_dict = {
        "id": db_report.id,
        "employee_id": db_report.employee_id,
        "employee_name": db_report.employee_name,
        "report_date": db_report.report_date.strftime("%Y-%m-%d"),
        "work_target": db_report.work_target or "",
        "key_work_tracking": db_report.key_work_tracking or "",
        "tomorrow_plan": db_report.tomorrow_plan or "",
        "planned_hours": float(db_report.planned_hours) if db_report.planned_hours else 0.0,
        "self_evaluation": db_report.self_evaluation or "",
        "status": db_report.status,
        "submitted_at": db_report.submitted_at.strftime("%Y-%m-%d %H:%M:%S") if db_report.submitted_at else None,
        "create_time": db_report.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        "update_time": db_report.update_time.strftime("%Y-%m-%d %H:%M:%S"),
        "work_items": work_items,
        # 从 evaluations 关系中获取评价信息，而不是直接访问不存在字段
        "supervisor_score": db_report.evaluations[0].supervisor_score if db_report.evaluations else 0,
        "supervisor_comment": db_report.evaluations[0].supervisor_comment if db_report.evaluations else "",
        "supervisor_id": db_report.evaluations[0].supervisor_id if db_report.evaluations else "",
        "supervisor_name": db_report.evaluations[0].supervisor_name if db_report.evaluations else "",
        "evaluated_at": db_report.evaluations[0].evaluated_at.strftime("%Y-%m-%d %H:%M:%S") if db_report.evaluations and db_report.evaluations[0].evaluated_at else None
    }
    
    return report_dict


def get_daily_report_by_employee_and_date(
    db: Session,
    employee_id: str,
    report_date: date
) -> Optional[DailyReport]:
    return db.query(DailyReport).filter(
        DailyReport.employee_id == employee_id,
        DailyReport.report_date == report_date,
        DailyReport.is_deleted == False
    ).first()


def create_daily_report(
    db: Session, 
    report: DailyReportCreate
) -> DailyReport:
    """创建日报记录（只处理主表）"""
    
    # 检查是否已存在该员工当天的日报
    existing = get_daily_report_by_employee_and_date(
        db, report.employee_id, report.report_date
    )
    if existing:
        return update_daily_report(db, existing.id, report)
    
    db_report = DailyReport(
        report_date=report.report_date,
        employee_id=report.employee_id,
        employee_name=report.employee_name,
        work_target=report.work_target,
        key_work_tracking=report.key_work_tracking,
        tomorrow_plan=report.tomorrow_plan,
        planned_hours=report.planned_hours,
        status="待提交"
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def create_daily_report_with_items(
    db: Session, 
    report_with_items: DailyReportWithItemsCreate
) -> DailyReport:
    """创建包含工作事项的完整日报"""
    
    # 检查是否已存在该员工当天的日报
    existing_report = get_daily_report_by_employee_and_date(
        db, report_with_items.report.employee_id, report_with_items.report.report_date
    )
    
    if existing_report:
        # 如果存在，使用现有日报ID
        db_report = existing_report
        
        # 清空现有的工作事项
        db.query(DailyWorkItem).filter(
            DailyWorkItem.report_id == db_report.id
        ).delete()
        db.flush()
    else:
        # 如果不存在，创建新的日报
        db_report = DailyReport(
            report_date=report_with_items.report.report_date,
            employee_id=report_with_items.report.employee_id,
            employee_name=report_with_items.report.employee_name,
            work_target=report_with_items.report.work_target,
            key_work_tracking=report_with_items.report.key_work_tracking,
            tomorrow_plan=report_with_items.report.tomorrow_plan,
            planned_hours=report_with_items.report.planned_hours,
            status="待提交"
        )
        db.add(db_report)
        db.flush()
    
    # 创建工作事项记录
    if report_with_items.work_items:
        for item_data in report_with_items.work_items:
            # 安全处理时间字段
            start_time_str = None
            end_time_str = None
            
            if item_data.start_time:
                start_time_str = str(item_data.start_time)
            
            if item_data.end_time:
                end_time_str = str(item_data.end_time)
            
            # 安全处理数值字段
            hours_spent = float(item_data.hours_spent) if item_data.hours_spent else 0.0
            progress_percentage = float(item_data.progress_percentage) if item_data.progress_percentage else 0.0
            delay_hours = float(item_data.delay_hours) if item_data.delay_hours else 0.0
            
            # 安全处理字符串字段
            work_content = item_data.work_content or ""
            project_id = item_data.project_id or ""
            project_name = item_data.project_name or ""
            task_id = item_data.task_id or ""
            task_name = item_data.task_name or ""
            key_work_tracking = item_data.key_work_tracking or ""
            result = item_data.result or ""
            measures = item_data.measures or ""
            evaluation = item_data.evaluation or ""
            progress_status = item_data.progress_status or "正常"
            improvement_result = item_data.improvement_result or ""
            
            db_work_item = DailyWorkItem(
                report_id=db_report.id,
                work_content=work_content,
                project_id=project_id,
                project_name=project_name,
                task_id=task_id,
                task_name=task_name,
                key_work_tracking=key_work_tracking,
                start_time=start_time_str,
                end_time=end_time_str,
                hours_spent=hours_spent,
                result=result,
                measures=measures,
                evaluation=evaluation,
                progress_status=progress_status,
                progress_percentage=progress_percentage,
                delay_hours=delay_hours,
                improvement_result=improvement_result
            )
            db.add(db_work_item)
    
    db.commit()
    db.refresh(db_report)
    return db_report


def update_daily_report(
    db: Session,
    report_id: int,
    report_data: DailyReportCreate or DailyReportUpdate
) -> Optional[DailyReport]:
    db_report = get_daily_report(db, report_id)
    if not db_report:
        return None
    
    update_data = report_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_report, field, value)
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def submit_daily_report(db: Session, report_id: int) -> Optional[Dict[str, Any]]:
    db_report = get_daily_report(db, report_id)
    if not db_report:
        return None
    
    db_report.status = "已提交"
    db_report.submitted_at = datetime.now()
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    # 重新获取数据并转换为字典格式
    return get_daily_report(db, report_id, as_dict=True)


def evaluate_daily_report(
    db: Session,
    report_id: int,
    supervisor_id: str,
    supervisor_name: str,
    score: int,
    comment: Optional[str] = None
) -> Optional[DailyReport]:
    db_report = get_daily_report(db, report_id)
    if not db_report:
        return None
    
    # 创建或更新评价记录
    from app.models.daily_report import DailyReportEvaluation
    
    # 检查是否已有评价记录
    existing_evaluation = db.query(DailyReportEvaluation).filter(
        DailyReportEvaluation.report_id == report_id
    ).first()
    
    if existing_evaluation:
        # 更新现有评价
        existing_evaluation.supervisor_score = score
        existing_evaluation.supervisor_comment = comment
        existing_evaluation.supervisor_id = supervisor_id
        existing_evaluation.supervisor_name = supervisor_name
        existing_evaluation.evaluated_at = datetime.now()
    else:
        # 创建新评价
        new_evaluation = DailyReportEvaluation(
            report_id=report_id,
            supervisor_score=score,
            supervisor_comment=comment,
            supervisor_id=supervisor_id,
            supervisor_name=supervisor_name,
            evaluated_at=datetime.now()
        )
        db.add(new_evaluation)
    
    # 更新日报状态
    db_report.status = "已评价"
    db.add(db_report)
    
    db.commit()
    db.refresh(db_report)
    return db_report


def delete_daily_report(db: Session, report_id: int) -> bool:
    db_report = get_daily_report(db, report_id)
    if not db_report:
        return False
    
    db_report.is_deleted = True
    db.commit()
    return True


def get_my_tasks(
    db: Session,
    employee_id: str,
    status: Optional[str] = None,
    keyword: Optional[str] = None
) -> List[ProjectTask]:
    # 同时支持工号和人员ID两种格式的查询
    query = db.query(ProjectTask).filter(
        ProjectTask.is_deleted == False
    ).filter(
        or_(
            # 按工号匹配
            ProjectTask.assignee_id == employee_id,
            ProjectTask.assignee_id.like(f"{employee_id},%"),
            ProjectTask.assignee_id.like(f"%,{employee_id}"),
            ProjectTask.assignee_id.like(f"%,{employee_id},%"),
            # 按人员ID匹配（转换为字符串）
            ProjectTask.assignee_id == str(employee_id),
            ProjectTask.assignee_id.like(f"{str(employee_id)},%"),
            ProjectTask.assignee_id.like(f"%,{str(employee_id)}"),
            ProjectTask.assignee_id.like(f"%,{str(employee_id)},%")
        )
    )
    
    if status:
        query = query.filter(ProjectTask.status == status)
    
    if keyword:
        query = query.filter(
            or_(
                ProjectTask.task_name.ilike(f"%{keyword}%"),
                ProjectTask.project_id.ilike(f"%{keyword}%")
            )
        )
    
    tasks = query.order_by(ProjectTask.start_date.desc()).all()
    
    # 批量查询项目名称，减少SQL查询次数
    result = []
    project_names = {}
    
    if tasks:
        # 获取所有项目ID
        project_ids = [int(task.project_id) for task in tasks if task.project_id]
        
        # 批量查询项目信息
        projects = db.query(Project).filter(Project.id.in_(project_ids)).all()
        project_names = {str(p.id): p.name for p in projects}
    
    for task in tasks:
        task.project_name = project_names.get(str(task.project_id), "")
        
        # 转换为MyTaskResponse格式
        from app.schemas.daily_report import MyTaskResponse
        task_response = MyTaskResponse(
            task_id=task.task_id,
            task_name=task.task_name,
            project_id=task.project_id,
            project_name=task.project_name,
            assignee=task.assignee,
            assignee_id=task.assignee_id,
            start_date=task.start_date,
            end_date=task.end_date,
            status=task.status,
            progress=float(task.progress) if task.progress else 0.0,
            resource_allocation=getattr(task, 'resource_allocation', None)
        )
        result.append(task_response)
    
    return result


def get_daily_work_logs(
    db: Session,
    employee_id: str,
    work_date: date
) -> List[DailyWorkLog]:
    return db.query(DailyWorkLog).filter(
        DailyWorkLog.employee_id == employee_id,
        DailyWorkLog.work_date == work_date,
        DailyWorkLog.is_deleted == False
    ).all()


def create_daily_work_log(db: Session, log: DailyWorkLogCreate, employee_name: str) -> DailyWorkLog:
    existing = db.query(DailyWorkLog).filter(
        DailyWorkLog.project_id == log.project_id,
        DailyWorkLog.task_id == log.task_id,
        DailyWorkLog.employee_id == log.employee_id,
        DailyWorkLog.work_date == log.work_date,
        DailyWorkLog.is_deleted == False
    ).first()
    
    if existing:
        existing.hours = log.hours
        existing.work_content = log.work_content
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    
    db_log = DailyWorkLog(
        project_id=log.project_id,
        project_name=log.project_name,
        task_id=log.task_id,
        task_name=log.task_name,
        employee_id=log.employee_id,
        employee_name=employee_name,
        work_date=log.work_date,
        work_content=log.work_content,
        hours=log.hours,
        status="待审核"
    )
    
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_pending_reports(
    db: Session,
    supervisor_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
) -> Tuple[List[DailyReport], int]:
    query = db.query(DailyReport).filter(
        DailyReport.is_deleted == False,
        DailyReport.status == "待评价"
    )
    
    if supervisor_id:
        query = query.filter(DailyReport.employee_id != supervisor_id)
    
    total = query.count()
    reports = query.order_by(DailyReport.submitted_at.desc()).offset(skip).limit(limit).all()
    
    return reports, total
