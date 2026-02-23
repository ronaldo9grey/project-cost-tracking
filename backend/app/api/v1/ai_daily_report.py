"""
AI日报助手API
提供日报生成、摘要、评价建议等AI功能
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.core.dependencies import get_db
from app.core.exceptions import BadRequestException
from app.services.ai_daily_report import ai_assistant
from app.models.daily_report import DailyReport
from app.models.resource import Personnel
from app.api.v1.auth import get_current_user
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/ai-daily", tags=["AI日报助手"])


class GenerateReportRequest(BaseModel):
    """生成日报请求"""
    projects: List[str]
    tasks: List[dict]
    notes: Optional[str] = None


class SummarizeRequest(BaseModel):
    """摘要请求"""
    report_content: str


class EvaluationRequest(BaseModel):
    """评价建议请求"""
    report_content: str
    user_role: str
    department: str


class TrendAnalysisRequest(BaseModel):
    """趋势分析请求"""
    days: int = 7


@router.post("/generate")
def generate_daily_report(
    request: GenerateReportRequest,
    current_user: Personnel = Depends(get_current_user)
):
    """
    AI生成日报
    
    根据提供的工作事项，AI自动生成一份专业日报
    """
    result = ai_assistant.generate_daily_report(
        user_name=current_user.name,
        projects=request.projects,
        tasks=request.tasks,
        notes=request.notes
    )
    
    if not result["success"]:
        raise BadRequestException(message=f"生成失败：{result.get('error', '未知错误')}")
    
    return SuccessResponse(
        data=result,
        message="日报生成成功"
    )


@router.post("/summarize")
def summarize_report(
    request: SummarizeRequest
):
    """
    日报摘要
    
    分析日报内容，提取关键信息和摘要
    """
    result = ai_assistant.summarize_daily_report(request.report_content)
    
    if not result["success"]:
        raise BadRequestException(message=f"摘要失败：{result.get('error', '未知错误')}")
    
    return SuccessResponse(
        data=result,
        message="摘要生成成功"
    )


@router.post("/evaluation-suggestions")
def get_evaluation_suggestions(
    request: EvaluationRequest
):
    """
    评价建议
    
    根据日报内容，为管理者提供评价建议
    """
    result = ai_assistant.generate_evaluation_suggestions(
        report_content=request.report_content,
        user_role=request.user_role,
        department=request.department
    )
    
    if not result["success"]:
        raise BadRequestException(message=f"生成失败：{result.get('error', '未知错误')}")
    
    return SuccessResponse(
        data=result,
        message="评价建议生成成功"
    )


@router.post("/workload-trend")
def analyze_workload_trend(
    request: TrendAnalysisRequest,
    current_user: Personnel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    工作量趋势分析
    
    分析用户近期日报数据，识别工作量趋势和模式
    """
    # 获取用户的近期日报
    end_date = datetime.now()
    start_date = end_date - timedelta(days=request.days)
    
    reports = db.query(DailyReport).filter(
        DailyReport.personnel_id == current_user.id,
        DailyReport.report_date >= start_date,
        DailyReport.report_date <= end_date,
        DailyReport.is_deleted == False
    ).order_by(DailyReport.report_date.desc()).all()
    
    result = ai_assistant.analyze_workload_trend(reports, request.days)
    
    if not result["success"]:
        raise BadRequestException(message=f"分析失败：{result.get('error', '未知错误')}")
    
    return SuccessResponse(
        data=result,
        message="工作量趋势分析完成"
    )


@router.post("/quick-generate")
def quick_generate_report(
    current_user: Personnel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    快速生成日报
    
    根据用户今天的任务记录，快速生成日报草稿
    """
    # 获取用户今天的日报数据（如果有）
    today = datetime.now().date()
    today_report = db.query(DailyReport).filter(
        DailyReport.personnel_id == current_user.id,
        DailyReport.report_date == today,
        DailyReport.is_deleted == False
    ).first()
    
    if today_report:
        # 已有日报，生成摘要
        result = ai_assistant.summarize_daily_report(
            f"{today_report.work_goals}\n{today_report.key_progress}\n{today_report.main_work_items}"
        )
        return SuccessResponse(
            data={
                "type": "summary",
                "report_id": today_report.id,
                "result": result
            },
            message="今日日报摘要生成成功"
        )
    else:
        # 没有日报，根据角色生成模板
        tasks = [
            {"name": "处理日常工作任务", "status": "进行中", "progress": 50},
            {"name": "参与项目会议", "status": "已完成", "progress": 100},
            {"name": "编写项目文档", "status": "进行中", "progress": 30}
        ]
        
        result = ai_assistant.generate_daily_report(
            user_name=current_user.name,
            projects=["项目A", "项目B"],
            tasks=tasks,
            notes=f"职位：{current_user.position}，部门：{current_user.department}"
        )
        
        return SuccessResponse(
            data={
                "type": "generated",
                "result": result
            },
            message="日报草稿生成成功，请根据实际情况修改"
        )
