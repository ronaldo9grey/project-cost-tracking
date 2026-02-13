from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from app.core.dependencies import get_db
from app.api.v1.auth import get_current_user
from app.models.daily_report import DailyReport, DailyReportEvaluation
from app.models.resource import Personnel
from app.crud.daily_report_evaluation import (
    get_subordinate_reports,
    get_evaluation_stats,
    create_evaluation,
    get_report_with_evaluation,
    get_evaluation_history,
    update_evaluation,
    delete_evaluation
)
from app.schemas.daily_report_evaluation import (
    SubordinateReportResponse,
    EvaluationStatsResponse,
    CreateEvaluationRequest,
    EvaluationResponse,
    EvaluationHistoryResponse
)
from app.schemas.response import SuccessResponse

router = APIRouter()


@router.get("/subordinate-reports", summary="获取管辖员工的日报列表")
async def get_subordinate_reports_api(
    employee_name: Optional[str] = Query(None, description="员工姓名筛选"),
    department: Optional[str] = Query(None, description="部门筛选"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """获取当前用户的管辖员工的日报列表"""
    try:
        # 获取当前用户的管辖员工日报（包括已提交和已评价的）
        reports = get_subordinate_reports(
            db=db,
            supervisor_id=current_user.employee_id,
            employee_name=employee_name,
            department=department,
            start_date=start_date,
            end_date=end_date
        )
        
        return SuccessResponse(
            data=reports, 
            message="获取管辖员工日报成功"
        )
    except Exception as e:
        print(f"获取管辖员工日报失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取管辖员工日报失败: {str(e)}")


@router.get("/stats", summary="获取评价统计数据")
async def get_evaluation_stats_api(
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """获取评价统计数据"""
    try:
        stats = get_evaluation_stats(
            db=db,
            supervisor_id=current_user.employee_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return SuccessResponse(
            data=stats, 
            message="获取评价统计数据成功"
        )
    except Exception as e:
        print(f"获取评价统计数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取评价统计数据失败: {str(e)}")


@router.post("/evaluate", summary="评价日报")
async def evaluate_daily_report_api(
    evaluation_data: CreateEvaluationRequest,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """对日报进行评价"""
    try:
        # 验证评价权限：只能评价下属员工的日报
        if not can_evaluate_report(db, evaluation_data.report_id, current_user.employee_id):
            raise HTTPException(status_code=403, detail="没有权限评价此日报")
        
        # 创建评价记录
        evaluation = create_evaluation(
            db=db,
            report_id=evaluation_data.report_id,
            supervisor_id=current_user.employee_id,
            supervisor_name=current_user.name,
            score=evaluation_data.supervisor_score,
            comment=evaluation_data.supervisor_comment
        )
        
        return SuccessResponse(
            data=evaluation, 
            message="日报评价成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"日报评价失败: {e}")
        raise HTTPException(status_code=500, detail=f"日报评价失败: {str(e)}")


@router.get("/reports/{report_id}", summary="获取日报详情")
async def get_report_detail_api(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """获取日报详情"""
    try:
        # 验证权限：只能查看下属员工的日报
        if not can_evaluate_report(db, report_id, current_user.employee_id):
            raise HTTPException(status_code=403, detail="没有权限查看此日报")
        
        report = get_report_with_evaluation(db, report_id)
        
        return SuccessResponse(
            data=report, 
            message="获取日报详情成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取日报详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取日报详情失败: {str(e)}")


@router.get("/history", summary="获取评价历史")
async def get_evaluation_history_api(
    employee_id: Optional[str] = Query(None, description="员工ID"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """获取评价历史"""
    try:
        history = get_evaluation_history(
            db=db,
            supervisor_id=current_user.employee_id,
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit
        )
        
        return SuccessResponse(
            data=history, 
            message="获取评价历史成功"
        )
    except Exception as e:
        print(f"获取评价历史失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取评价历史失败: {str(e)}")


@router.put("/evaluations/{evaluation_id}", summary="更新评价")
async def update_evaluation_api(
    evaluation_id: int,
    evaluation_data: CreateEvaluationRequest,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """更新评价"""
    try:
        # 验证权限：只能更新自己创建的评价
        evaluation = db.query(DailyReportEvaluation).filter(DailyReportEvaluation.id == evaluation_id).first()
        if not evaluation:
            raise HTTPException(status_code=404, detail="评价记录不存在")
        
        if evaluation.supervisor_id != current_user.employee_id:
            raise HTTPException(status_code=403, detail="没有权限修改此评价")
        
        updated_evaluation = update_evaluation(
            db=db,
            evaluation_id=evaluation_id,
            score=evaluation_data.supervisor_score,
            comment=evaluation_data.supervisor_comment
        )
        
        return SuccessResponse(
            data=updated_evaluation, 
            message="评价更新成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"更新评价失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新评价失败: {str(e)}")


@router.delete("/evaluations/{evaluation_id}", summary="删除评价")
async def delete_evaluation_api(
    evaluation_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """删除评价"""
    try:
        # 验证权限：只能删除自己创建的评价
        evaluation = db.query(DailyReportEvaluation).filter(DailyReportEvaluation.id == evaluation_id).first()
        if not evaluation:
            raise HTTPException(status_code=404, detail="评价记录不存在")
        
        if evaluation.supervisor_id != current_user.employee_id:
            raise HTTPException(status_code=403, detail="没有权限删除此评价")
        
        delete_evaluation(db=db, evaluation_id=evaluation_id)
        
        return SuccessResponse(
            data=None, 
            message="评价删除成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除评价失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除评价失败: {str(e)}")


def can_evaluate_report(db: Session, report_id: int, supervisor_id: str) -> bool:
    """验证是否可以评价某日报"""
    # 获取日报信息
    report = db.query(DailyReport).filter(DailyReport.id == report_id).first()
    if not report:
        return False
    
    # 检查当前用户是否是该员工的上级
    # 这里需要根据employee_group_relations表进行判断
    from app.models.resource import EmployeeGroupRelation
    
    # 查找当前用户作为该员工的上级
    relationship = db.query(EmployeeGroupRelation).filter(
        EmployeeGroupRelation.group_name.in_(
            # 获取当前用户所在分组作为上级的所有分组
            db.query(EmployeeGroupRelation.group_name).filter(
                EmployeeGroupRelation.employee_id == supervisor_id,
                EmployeeGroupRelation.relation_type == 'supervisor'
            )
        ),
        EmployeeGroupRelation.employee_id == report.employee_id,
        EmployeeGroupRelation.relation_type == 'member'
    ).first()
    
    return relationship is not None