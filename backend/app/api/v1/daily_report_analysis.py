"""
日报数据分析API
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.core.dependencies import get_db
from app.api.v1.auth import get_current_user
from app.models.resource import Personnel
from app.crud.daily_report_analysis import (
    get_overview_stats,
    get_hours_trend,
    get_project_hours_distribution,
    get_employee_hours_ranking,
    get_task_completion_analysis,
    get_evaluation_analysis,
    get_analysis_projects_list
)
from app.crud.project import get_all_projects

router = APIRouter(prefix="/analysis", tags=["daily-report-analysis"])

@router.get("/overview", summary="获取分析概览数据")
def get_analysis_overview(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    project_id: Optional[str] = Query(None, description="项目ID"),
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """
    获取日报数据分析概览统计
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        project_id: 项目ID
    
    Returns:
        分析概览数据
    """
    try:
        # 解析日期参数
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="开始日期格式不正确")
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="结束日期格式不正确")
        
        # 获取概览数据
        overview_data = get_overview_stats(db, start_dt, end_dt, project_id)
        
        return {
            "code": 200,
            "message": "获取概览数据成功",
            "data": overview_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取概览数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取概览数据失败: {str(e)}")

@router.get("/hours-trend", summary="获取工时趋势数据")
def get_hours_trend_data(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    group_by: str = Query("day", description="分组方式: day, week, month"),
    project_id: Optional[str] = Query(None, description="项目ID"),
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """
    获取工时趋势数据
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        group_by: 分组方式 (day, week, month)
        project_id: 项目ID
    
    Returns:
        工时趋势数据
    """
    try:
        # 设置默认日期范围（最近30天）
        if not start_date or not end_date:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=30)
        else:
            # 解析日期参数
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="日期格式不正确")
        
        # 验证group_by参数
        if group_by not in ['day', 'week', 'month']:
            raise HTTPException(status_code=400, detail="分组方式必须是 day, week, 或 month")
        
        # 获取趋势数据
        trend_data = get_hours_trend(db, start_dt, end_dt, group_by, project_id)
        
        return {
            "code": 200,
            "message": "获取工时趋势数据成功",
            "data": trend_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取工时趋势数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取工时趋势数据失败: {str(e)}")

@router.get("/project-distribution", summary="获取项目工时分布")
def get_project_distribution_data(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    limit: int = Query(20, description="返回数量限制"),
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """
    获取项目工时分布数据
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        limit: 返回数量限制
    
    Returns:
        项目工时分布数据
    """
    try:
        # 解析日期参数
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="开始日期格式不正确")
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="结束日期格式不正确")
        
        # 验证limit参数
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="limit必须在1-100之间")
        
        # 获取项目分布数据
        distribution_data = get_project_hours_distribution(db, start_dt, end_dt, limit)
        
        return {
            "code": 200,
            "message": "获取项目分布数据成功",
            "data": distribution_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取项目分布数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取项目分布数据失败: {str(e)}")

@router.get("/employee-ranking", summary="获取人员工时排名")
def get_employee_ranking_data(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    limit: int = Query(20, description="返回数量限制"),
    project_id: Optional[str] = Query(None, description="项目ID"),
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """
    获取人员工时排名数据
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        limit: 返回数量限制
        project_id: 项目ID
    
    Returns:
        人员工时排名数据
    """
    try:
        # 解析日期参数
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="开始日期格式不正确")
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="结束日期格式不正确")
        
        # 验证limit参数
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="limit必须在1-100之间")
        
        # 获取排名数据
        ranking_data = get_employee_hours_ranking(db, start_dt, end_dt, limit, project_id)
        
        return {
            "code": 200,
            "message": "获取人员排名数据成功",
            "data": ranking_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取人员排名数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取人员排名数据失败: {str(e)}")

@router.get("/task-completion", summary="获取任务完成率分析")
def get_task_completion_data(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    project_id: Optional[str] = Query(None, description="项目ID"),
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """
    获取任务完成率分析数据
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        project_id: 项目ID
    
    Returns:
        任务完成率分析数据
    """
    try:
        # 解析日期参数
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="开始日期格式不正确")
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="结束日期格式不正确")
        
        # 获取完成率分析数据
        completion_data = get_task_completion_analysis(db, start_dt, end_dt, project_id)
        
        return {
            "code": 200,
            "message": "获取任务完成率分析数据成功",
            "data": completion_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取任务完成率分析数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务完成率分析数据失败: {str(e)}")

@router.get("/projects", summary="获取项目列表")
def get_project_list(
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """
    获取项目列表，用于筛选器
    
    Returns:
        项目列表数据
    """
    try:
        # 从 projects 表获取项目列表
        projects = get_all_projects(db)
        
        return {
            "code": 200,
            "message": "获取项目列表成功",
            "data": projects
        }
    
    except Exception as e:
        print(f"获取项目列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取项目列表失败: {str(e)}")

@router.get("/evaluation", summary="获取评价分析数据")
def get_evaluation_analysis_data(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    project_id: Optional[str] = Query(None, description="项目ID"),
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """
    获取评价分析数据
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        project_id: 项目ID
    
    Returns:
        评价分析数据
    """
    try:
        # 解析日期参数
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="开始日期格式不正确")
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="结束日期格式不正确")
        
        # 获取评价分析数据
        evaluation_data = get_evaluation_analysis(db, start_dt, end_dt, project_id)
        
        return {
            "code": 200,
            "message": "获取评价分析数据成功",
            "data": evaluation_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取评价分析数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取评价分析数据失败: {str(e)}")

@router.get("/dashboard", summary="获取分析仪表板数据")
def get_analysis_dashboard(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    project_id: Optional[str] = Query(None, description="项目ID"),
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """
    获取分析仪表板所有数据
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        project_id: 项目ID
    
    Returns:
        仪表板所有数据
    """
    try:
        # 解析日期参数
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="开始日期格式不正确")
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(status_code=400, detail="结束日期格式不正确")
        
        # 如果没有指定日期，默认获取最近30天的数据
        if not start_dt and not end_dt:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=30)
        
        # 并发获取所有数据
        overview_data = get_overview_stats(db, start_dt, end_dt, project_id)
        
        # 获取工时趋势数据（最近30天按天分组）
        hours_trend = get_hours_trend(db, start_dt, end_dt, "day", project_id)
        
        # 获取项目分布数据
        project_distribution = get_project_hours_distribution(db, start_dt, end_dt, 20)
        
        # 获取人员排名数据
        employee_ranking = get_employee_hours_ranking(db, start_dt, end_dt, 20, project_id)
        
        # 获取任务完成率分析
        task_completion = get_task_completion_analysis(db, start_dt, end_dt, project_id)
        
        dashboard_data = {
            "overview": overview_data,
            "hours_trend": hours_trend,
            "project_distribution": project_distribution,
            "employee_ranking": employee_ranking,
            "task_completion": task_completion,
            "date_range": {
                "start_date": start_dt.strftime('%Y-%m-%d'),
                "end_date": end_dt.strftime('%Y-%m-%d')
            }
        }
        
        return {
            "code": 200,
            "message": "获取仪表板数据成功",
            "data": dashboard_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取仪表板数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取仪表板数据失败: {str(e)}")