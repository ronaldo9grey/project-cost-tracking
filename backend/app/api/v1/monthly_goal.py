from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from decimal import Decimal

from app.core.dependencies import get_db
from app.api.v1.auth import get_current_user
from app.models.resource import Personnel
from app.models.monthly_goal import MonthlyGoal, WeeklyGoal, DailyReportGoal
from app.crud.monthly_goal import (
    get_monthly_goal,
    get_monthly_goal_with_weekly_goals,
    get_monthly_goals,
    create_monthly_goal,
    update_monthly_goal,
    publish_monthly_goal,
    update_monthly_goal_progress,
    delete_monthly_goal,
    get_weekly_goal,
    get_weekly_goals_by_monthly_goal,
    get_weekly_goals_by_user_and_month,
    get_current_week_goal,
    create_weekly_goal,
    update_weekly_goal,
    update_weekly_goal_progress,
    delete_weekly_goal,
    get_daily_report_goal,
    get_daily_report_goals_by_report,
    create_daily_report_goal,
    update_daily_report_goal,
    delete_daily_report_goal,
    generate_goals_from_tasks
)
from app.schemas.monthly_goal import (
    MonthlyGoalCreate,
    MonthlyGoalUpdate,
    MonthlyGoalResponse,
    MonthlyGoalListResponse,
    MonthlyGoalDetailResponse,
    MonthlyGoalProgressUpdate,
    WeeklyGoalCreate,
    WeeklyGoalUpdate,
    WeeklyGoalResponse,
    WeeklyGoalListResponse,
    WeeklyGoalProgressUpdate,
    WeeklyGoalWithMonthlyInfoResponse,
    CurrentWeekGoalResponse,
    DailyReportGoalCreate,
    DailyReportGoalUpdate,
    DailyReportGoalResponse,
    DailyReportGoalListResponse,
    DailyReportGoalWithDetailsResponse
)

router = APIRouter()


# ==================== 月度目标 API ====================

@router.get("/monthly-goals", response_model=MonthlyGoalListResponse, summary="获取当前用户的月度目标列表")
def read_monthly_goals(
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user),
    month: Optional[str] = Query(None, description="月份筛选 (格式: 2026-02)"),
    status: Optional[str] = Query(None, description="状态筛选", enum=["draft", "published", "completed"]),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    """获取当前用户的月度目标列表"""
    skip = (page - 1) * size
    goals, total = get_monthly_goals(
        db,
        user_id=current_user.employee_id,
        month=month,
        status=status,
        skip=skip,
        limit=size
    )
    
    total_pages = (total + size - 1) // size if total > 0 else 0
    
    return {
        "items": goals,
        "total": total,
        "page": page,
        "size": size,
        "total_pages": total_pages
    }


@router.post("/monthly-goals", response_model=MonthlyGoalResponse, summary="创建月度目标")
def create_monthly_goal_endpoint(
    goal_data: MonthlyGoalCreate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """创建月度目标"""
    try:
        goal = create_monthly_goal(
            db,
            goal=goal_data,
            user_id=current_user.employee_id,
            user_name=current_user.name
        )
        return goal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/monthly-goals/{goal_id}", response_model=MonthlyGoalDetailResponse, summary="获取月度目标详情")
def read_monthly_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """获取月度目标详情（包含周目标）"""
    goal = get_monthly_goal_with_weekly_goals(db, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="月度目标未找到")
    
    # 检查权限（只能查看自己的目标）
    if goal.user_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权查看此目标")
    
    # 构建响应
    goal_dict = {
        "id": goal.id,
        "user_id": goal.user_id,
        "user_name": goal.user_name,
        "month": goal.month,
        "title": goal.title,
        "content": goal.content,
        "status": goal.status,
        "progress_rate": goal.progress_rate,
        "created_at": goal.created_at,
        "updated_at": goal.updated_at,
        "is_deleted": goal.is_deleted,
        "weekly_goal_count": len(goal.weekly_goals),
        "weekly_goals": []
    }
    
    # 转换周目标
    for wg in goal.weekly_goals:
        if not wg.is_deleted:
            goal_dict["weekly_goals"].append({
                "id": wg.id,
                "goal_id": wg.goal_id,
                "week_number": wg.week_number,
                "title": wg.title,
                "content": wg.content,
                "progress_rate": wg.progress_rate,
                "status": wg.status,
                "start_date": wg.start_date,
                "end_date": wg.end_date,
                "created_at": wg.created_at,
                "updated_at": wg.updated_at,
                "is_deleted": wg.is_deleted
            })
    
    return goal_dict


@router.put("/monthly-goals/{goal_id}", response_model=MonthlyGoalResponse, summary="更新月度目标")
def update_monthly_goal_endpoint(
    goal_id: int,
    goal_data: MonthlyGoalUpdate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """更新月度目标"""
    goal = get_monthly_goal(db, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="月度目标未找到")
    
    # 检查权限
    if goal.user_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权修改此目标")
    
    updated_goal = update_monthly_goal(db, goal_id, goal_data)
    if not updated_goal:
        raise HTTPException(status_code=400, detail="更新失败")
    
    return updated_goal


@router.delete("/monthly-goals/{goal_id}", summary="删除月度目标")
def delete_monthly_goal_endpoint(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """删除月度目标（软删除）"""
    goal = get_monthly_goal(db, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="月度目标未找到")
    
    # 检查权限
    if goal.user_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权删除此目标")
    
    if delete_monthly_goal(db, goal_id):
        return {"message": "月度目标删除成功"}
    else:
        raise HTTPException(status_code=400, detail="删除失败")


@router.put("/monthly-goals/{goal_id}/publish", response_model=MonthlyGoalResponse, summary="发布月度目标")
def publish_monthly_goal_endpoint(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """发布月度目标"""
    goal = get_monthly_goal(db, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="月度目标未找到")
    
    # 检查权限
    if goal.user_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权发布此目标")
    
    published_goal = publish_monthly_goal(db, goal_id)
    if not published_goal:
        raise HTTPException(status_code=400, detail="发布失败")
    
    return published_goal


@router.put("/monthly-goals/{goal_id}/progress", response_model=MonthlyGoalResponse, summary="更新月度目标进度")
def update_monthly_goal_progress_endpoint(
    goal_id: int,
    progress_data: MonthlyGoalProgressUpdate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """更新月度目标进度"""
    goal = get_monthly_goal(db, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="月度目标未找到")
    
    # 检查权限
    if goal.user_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权修改此目标")
    
    updated_goal = update_monthly_goal_progress(db, goal_id, progress_data)
    if not updated_goal:
        raise HTTPException(status_code=400, detail="更新失败")
    
    return updated_goal


# ==================== 周目标 API ====================

@router.get("/monthly-goals/{goal_id}/weeks", response_model=WeeklyGoalListResponse, summary="获取某月度的所有周目标")
def read_weekly_goals_by_monthly(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """获取某月度的所有周目标"""
    # 检查月度目标是否存在
    goal = get_monthly_goal(db, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="月度目标未找到")
    
    # 检查权限
    if goal.user_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权查看此目标")
    
    weekly_goals = get_weekly_goals_by_monthly_goal(db, goal_id)
    
    return {
        "items": weekly_goals,
        "total": len(weekly_goals)
    }


@router.post("/monthly-goals/{goal_id}/weeks", response_model=WeeklyGoalResponse, summary="创建周目标")
def create_weekly_goal_endpoint(
    goal_id: int,
    weekly_goal_data: WeeklyGoalCreate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """创建周目标"""
    # 检查月度目标是否存在
    goal = get_monthly_goal(db, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="月度目标未找到")
    
    # 检查权限
    if goal.user_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权修改此目标")
    
    try:
        weekly_goal = create_weekly_goal(
            db,
            goal_id=goal_id,
            weekly_goal_data=weekly_goal_data.model_dump()
        )
        return weekly_goal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/weekly-goals/current", response_model=CurrentWeekGoalResponse, summary="获取本周目标（用于日报填报）")
def read_current_week_goal(
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user),
    current_date: Optional[date] = Query(None, description="指定日期，默认为今天")
):
    """获取本周目标（用于日报填报）
    
    根据当前日期自动判断属于第几周，返回对应的周目标
    """
    result = get_current_week_goal(db, current_user.employee_id, current_date)
    
    if not result:
        return {
            "weekly_goal": None,
            "month": None,
            "month_title": None,
            "week_number": None
        }
    
    weekly_goal = result["weekly_goal"]
    return {
        "weekly_goal": {
            "id": weekly_goal.id,
            "goal_id": weekly_goal.goal_id,
            "week_number": weekly_goal.week_number,
            "title": weekly_goal.title,
            "content": weekly_goal.content,
            "progress_rate": weekly_goal.progress_rate,
            "status": weekly_goal.status,
            "start_date": weekly_goal.start_date,
            "end_date": weekly_goal.end_date,
            "created_at": weekly_goal.created_at,
            "updated_at": weekly_goal.updated_at,
            "is_deleted": weekly_goal.is_deleted
        },
        "month": result["month"],
        "month_title": result["month_title"],
        "week_number": result["week_number"]
    }


@router.put("/weekly-goals/{weekly_goal_id}", response_model=WeeklyGoalResponse, summary="更新周目标")
def update_weekly_goal_endpoint(
    weekly_goal_id: int,
    weekly_goal_data: WeeklyGoalUpdate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """更新周目标"""
    weekly_goal = get_weekly_goal(db, weekly_goal_id)
    if not weekly_goal:
        raise HTTPException(status_code=404, detail="周目标未找到")
    
    # 检查权限
    monthly_goal = get_monthly_goal(db, weekly_goal.goal_id)
    if not monthly_goal or monthly_goal.user_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权修改此目标")
    
    updated_weekly_goal = update_weekly_goal(
        db,
        weekly_goal_id=weekly_goal_id,
        weekly_goal_data=weekly_goal_data.model_dump(exclude_unset=True)
    )
    
    if not updated_weekly_goal:
        raise HTTPException(status_code=400, detail="更新失败")
    
    return updated_weekly_goal


@router.delete("/weekly-goals/{weekly_goal_id}", summary="删除周目标")
def delete_weekly_goal_endpoint(
    weekly_goal_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """删除周目标（软删除）"""
    weekly_goal = get_weekly_goal(db, weekly_goal_id)
    if not weekly_goal:
        raise HTTPException(status_code=404, detail="周目标未找到")
    
    # 检查权限
    monthly_goal = get_monthly_goal(db, weekly_goal.goal_id)
    if not monthly_goal or monthly_goal.user_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权删除此目标")
    
    if delete_weekly_goal(db, weekly_goal_id):
        return {"message": "周目标删除成功"}
    else:
        raise HTTPException(status_code=400, detail="删除失败")


@router.put("/weekly-goals/{weekly_goal_id}/progress", response_model=WeeklyGoalResponse, summary="更新周目标进度")
def update_weekly_goal_progress_endpoint(
    weekly_goal_id: int,
    progress_data: WeeklyGoalProgressUpdate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """更新周目标进度"""
    weekly_goal = get_weekly_goal(db, weekly_goal_id)
    if not weekly_goal:
        raise HTTPException(status_code=404, detail="周目标未找到")
    
    # 检查权限
    monthly_goal = get_monthly_goal(db, weekly_goal.goal_id)
    if not monthly_goal or monthly_goal.user_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权修改此目标")
    
    updated_weekly_goal = update_weekly_goal_progress(
        db,
        weekly_goal_id=weekly_goal_id,
        progress_rate=progress_data.progress_rate
    )
    
    if not updated_weekly_goal:
        raise HTTPException(status_code=400, detail="更新失败")
    
    return updated_weekly_goal


# ==================== 日报目标关联 API ====================

@router.get("/daily-reports/{report_id}/goals", response_model=DailyReportGoalListResponse, summary="获取某日报的目标关联")
def read_daily_report_goals(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """获取某日报的所有目标关联"""
    from app.models.daily_report import DailyReport
    
    # 检查日报是否存在
    report = db.query(DailyReport).filter(
        DailyReport.id == report_id,
        DailyReport.is_deleted == False
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="日报未找到")
    
    # 检查权限
    if report.employee_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权查看此日报")
    
    goals = get_daily_report_goals_by_report(db, report_id)
    
    return {
        "items": goals,
        "total": len(goals)
    }


@router.post("/daily-reports/{report_id}/goals", response_model=DailyReportGoalResponse, summary="关联周目标到日报")
def create_daily_report_goal_endpoint(
    report_id: int,
    goal_data: DailyReportGoalCreate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """关联周目标到日报"""
    from app.models.daily_report import DailyReport
    
    # 检查日报是否存在
    report = db.query(DailyReport).filter(
        DailyReport.id == report_id,
        DailyReport.is_deleted == False
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="日报未找到")
    
    # 检查权限
    if report.employee_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权修改此日报")
    
    # 检查周目标是否存在
    weekly_goal = get_weekly_goal(db, goal_data.weekly_goal_id)
    if not weekly_goal:
        raise HTTPException(status_code=404, detail="周目标未找到")
    
    # 检查周目标是否属于当前用户
    monthly_goal = get_monthly_goal(db, weekly_goal.goal_id)
    if not monthly_goal or monthly_goal.user_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权使用此目标")
    
    goal_link = create_daily_report_goal(
        db,
        daily_report_id=report_id,
        goal_data=goal_data.model_dump()
    )
    
    return goal_link


@router.put("/daily-report-goals/{goal_link_id}", response_model=DailyReportGoalResponse, summary="更新目标关联")
def update_daily_report_goal_endpoint(
    goal_link_id: int,
    goal_data: DailyReportGoalUpdate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """更新目标关联"""
    goal_link = get_daily_report_goal(db, goal_link_id)
    if not goal_link:
        raise HTTPException(status_code=404, detail="目标关联未找到")
    
    # 检查权限（通过日报的employee_id）
    from app.models.daily_report import DailyReport
    report = db.query(DailyReport).filter(
        DailyReport.id == goal_link.daily_report_id,
        DailyReport.is_deleted == False
    ).first()
    
    if not report or report.employee_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权修改此目标关联")
    
    updated_goal_link = update_daily_report_goal(
        db,
        id=goal_link_id,
        goal_data=goal_data.model_dump(exclude_unset=True)
    )
    
    if not updated_goal_link:
        raise HTTPException(status_code=400, detail="更新失败")
    
    return updated_goal_link


@router.delete("/daily-report-goals/{goal_link_id}", summary="删除目标关联")
def delete_daily_report_goal_endpoint(
    goal_link_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """删除目标关联（软删除）"""
    goal_link = get_daily_report_goal(db, goal_link_id)
    if not goal_link:
        raise HTTPException(status_code=404, detail="目标关联未找到")
    
    # 检查权限（通过日报的employee_id）
    from app.models.daily_report import DailyReport
    report = db.query(DailyReport).filter(
        DailyReport.id == goal_link.daily_report_id,
        DailyReport.is_deleted == False
    ).first()
    
    if not report or report.employee_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权删除此目标关联")
    
    if delete_daily_report_goal(db, goal_link_id):
        return {"message": "目标关联删除成功"}
    else:
        raise HTTPException(status_code=400, detail="删除失败")


# ==================== 自动生成目标 API ====================

@router.post("/monthly-goals/generate-from-tasks", summary="从项目任务自动生成目标（AI智能生成）")
async def generate_goals_from_tasks_endpoint(
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user),
    year: Optional[int] = Query(None, description="年份，默认为当前年份")
):
    """
    根据当前登录用户负责的项目任务，AI智能生成月度目标和周目标
    
    - 分析用户的项目任务
    - 调用DeepSeek AI基于项目管理方法论生成高质量目标
    - 遵循SMART原则（具体、可衡量、可达成、相关、有时限）
    - 生成成果导向的目标，而非简单罗列任务
    """
    if year is None:
        year = date.today().year
    
    try:
        result = await generate_goals_from_tasks(
            db,
            user_id=current_user.employee_id,
            user_name=current_user.name,
            year=year
        )
        
        return {
            "message": "AI目标生成完成",
            "data": result
        }
    except Exception as e:
        import traceback
        print(f"Error generating goals from tasks: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"生成目标失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成目标失败: {str(e)}")
