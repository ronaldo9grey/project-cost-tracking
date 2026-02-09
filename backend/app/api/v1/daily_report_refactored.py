from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.dependencies import get_db
from app.api.v1.auth import get_current_user
from app.models.resource import Personnel
from app.crud.daily_report_refactored import (
    create_refactored_daily_report,
    update_refactored_daily_report,
    get_refactored_daily_report,
    submit_refactored_daily_report,
    get_refactored_daily_reports,
    add_work_item,
    add_evaluation
)
from app.schemas.daily_work_item import (
    RefactoredDailyReportCreate,
    RefactoredDailyReportUpdate,
    RefactoredDailyReportResponse,
    DailyWorkItemCreate,
    DailyReportEvaluationCreate
)

router = APIRouter()


@router.post("/v2/reports", response_model=RefactoredDailyReportResponse, summary="创建重构版日报")
def create_refactored_report(
    report: RefactoredDailyReportCreate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """
    创建重构版日报，支持工作事项子表和评价子表
    """
    try:
        result = create_refactored_daily_report(
            db, 
            report, 
            str(current_user.id), 
            current_user.name
        )
        
        # 转换为响应格式
        return get_refactored_daily_report(db, result.id, str(current_user.id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建日报失败: {str(e)}")


@router.put("/v2/reports/{report_id}", response_model=RefactoredDailyReportResponse, summary="更新重构版日报")
def update_refactored_report(
    report_id: int,
    report_data: RefactoredDailyReportUpdate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """
    更新重构版日报
    """
    try:
        result = update_refactored_daily_report(
            db, 
            report_id, 
            report_data, 
            str(current_user.id), 
            current_user.name
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="日报未找到或无权限修改")
        
        # 转换为响应格式
        return get_refactored_daily_report(db, report_id, str(current_user.id))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新日报失败: {str(e)}")


@router.get("/v2/reports/{report_id}", response_model=RefactoredDailyReportResponse, summary="获取重构版日报详情")
def get_refactored_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """
    获取重构版日报详情
    """
    result = get_refactored_daily_report(db, report_id, str(current_user.id))
    
    if not result:
        raise HTTPException(status_code=404, detail="日报未找到或无权限查看")
    
    return result


@router.post("/v2/reports/{report_id}/submit", response_model=RefactoredDailyReportResponse, summary="提交重构版日报")
def submit_refactored_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """
    提交重构版日报
    """
    try:
        result = submit_refactored_daily_report(db, report_id, str(current_user.id))
        
        if not result:
            raise HTTPException(status_code=404, detail="日报未找到或无权限操作")
        
        # 转换为响应格式
        return get_refactored_daily_report(db, report_id, str(current_user.id))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交日报失败: {str(e)}")


@router.post("/v2/reports/{report_id}/work-items", summary="添加工作事项")
def create_work_item(
    report_id: int,
    work_item_data: DailyWorkItemCreate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """
    添加工作事项
    """
    try:
        result = add_work_item(db, report_id, work_item_data, str(current_user.id))
        
        if not result:
            raise HTTPException(status_code=404, detail="日报未找到或无权限操作")
        
        return {"message": "工作事项添加成功", "work_item_id": result.id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加工作事项失败: {str(e)}")


@router.post("/v2/reports/{report_id}/evaluations", summary="添加评价")
def create_evaluation(
    report_id: int,
    evaluation_data: DailyReportEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """
    添加评价（领导用）
    """
    try:
        result = add_evaluation(db, report_id, evaluation_data, str(current_user.id))
        
        if not result:
            raise HTTPException(status_code=404, detail="日报未找到或无权限操作")
        
        return {"message": "评价添加成功", "evaluation_id": result.id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加评价失败: {str(e)}")


@router.get("/v2/my-reports", summary="获取重构版日报列表")
def get_refactored_reports(
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user),
    report_date: Optional[date] = Query(None, description="指定日期"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    """
    获取重构版日报列表
    """
    skip = (page - 1) * size
    reports, total = get_refactored_daily_reports(
        db,
        str(current_user.id),
        report_date=report_date,
        start_date=start_date,
        end_date=end_date,
        status=status,
        skip=skip,
        limit=size
    )
    
    total_pages = (total + size - 1) // size if total > 0 else 0
    
    # 转换为响应格式
    items = []
    for report in reports:
        # 计算总工时（从工作事项表中汇总）
        total_hours = 0
        work_items_data = []
        for item in report.work_items:
            if not item.is_deleted:
                total_hours += item.hours_spent or 0
                work_items_data.append({
                    "id": item.id,
                    "report_id": item.report_id,
                    "project_id": item.project_id,
                    "project_name": item.project_name,
                    "task_id": item.task_id,
                    "task_name": item.task_name,
                    "hours_spent": item.hours_spent,
                    "progress_status": item.progress_status,
                    "progress_percentage": item.progress_percentage,
                    "delay_hours": item.delay_hours,
                    "improvement_result": item.improvement_result,
                    "key_work_tracking": item.key_work_tracking,
                    "work_content": item.work_content,
                    "start_time": item.start_time,
                    "end_time": item.end_time,
                    "result": item.result,
                    "measures": item.measures,
                    "evaluation": item.evaluation,
                    "create_time": item.create_time,
                    "update_time": item.update_time,
                    "is_deleted": item.is_deleted
                })
        
        evaluations_data = []
        for eval_item in report.evaluations:
            if not eval_item.is_deleted:
                evaluations_data.append({
                    "id": eval_item.id,
                    "report_id": eval_item.report_id,
                    "supervisor_score": eval_item.supervisor_score,
                    "supervisor_comment": eval_item.supervisor_comment,
                    "supervisor_id": eval_item.supervisor_id,
                    "supervisor_name": eval_item.supervisor_name,
                    "evaluated_at": eval_item.evaluated_at,
                    "create_time": eval_item.create_time,
                    "update_time": eval_item.update_time,
                    "is_deleted": eval_item.is_deleted
                })
        
        items.append({
            "id": report.id,
            "report_date": report.report_date,
            "employee_id": report.employee_id,
            "employee_name": report.employee_name,
            "work_target": report.work_target,
            "key_work_tracking": report.key_work_tracking,
            "tomorrow_plan": report.tomorrow_plan,
            "planned_hours": report.planned_hours,
            "status": report.status,
            "submitted_at": report.submitted_at,
            "self_evaluation": report.self_evaluation,
            "create_time": report.create_time,
            "update_time": report.update_time,
            "work_items": work_items_data,
            "evaluations": evaluations_data
        })
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "total_pages": total_pages
    }