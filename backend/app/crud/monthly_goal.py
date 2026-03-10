from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Tuple
from datetime import date, datetime
from decimal import Decimal
from app.models.monthly_goal import MonthlyGoal, WeeklyGoal, DailyReportGoal
from app.schemas.monthly_goal import MonthlyGoalCreate, MonthlyGoalUpdate, MonthlyGoalProgressUpdate


# ==================== 月度目标 CRUD ====================

def get_monthly_goal(db: Session, goal_id: int) -> Optional[MonthlyGoal]:
    """获取月度目标详情"""
    return db.query(MonthlyGoal).filter(
        MonthlyGoal.id == goal_id,
        MonthlyGoal.is_deleted == False
    ).first()


def get_monthly_goal_with_weekly_goals(db: Session, goal_id: int) -> Optional[MonthlyGoal]:
    """获取月度目标详情（包含周目标）"""
    return db.query(MonthlyGoal).filter(
        MonthlyGoal.id == goal_id,
        MonthlyGoal.is_deleted == False
    ).first()


def get_monthly_goals(
    db: Session,
    user_id: str,
    month: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
) -> Tuple[List[MonthlyGoal], int]:
    """获取月度目标列表"""
    query = db.query(MonthlyGoal).filter(
        MonthlyGoal.user_id == user_id,
        MonthlyGoal.is_deleted == False
    )
    
    if month:
        query = query.filter(MonthlyGoal.month == month)
    if status:
        query = query.filter(MonthlyGoal.status == status)
    
    total = query.count()
    goals = query.order_by(MonthlyGoal.month.desc()).offset(skip).limit(limit).all()
    
    # 计算每个目标的周目标数量
    for goal in goals:
        goal.weekly_goal_count = db.query(WeeklyGoal).filter(
            WeeklyGoal.goal_id == goal.id,
            WeeklyGoal.is_deleted == False
        ).count()
    
    return goals, total


def get_monthly_goal_by_user_and_month(
    db: Session,
    user_id: str,
    month: str
) -> Optional[MonthlyGoal]:
    """根据用户和月份获取月度目标"""
    return db.query(MonthlyGoal).filter(
        MonthlyGoal.user_id == user_id,
        MonthlyGoal.month == month,
        MonthlyGoal.is_deleted == False
    ).first()


def create_monthly_goal(db: Session, goal: MonthlyGoalCreate, user_id: str, user_name: str) -> MonthlyGoal:
    """创建月度目标"""
    # 检查是否已存在该用户该月份的目标
    existing = get_monthly_goal_by_user_and_month(db, user_id, goal.month)
    if existing:
        raise ValueError(f"用户 {user_name} 在 {goal.month} 月份的目标已存在")
    
    db_goal = MonthlyGoal(
        user_id=user_id,
        user_name=user_name,
        month=goal.month,
        title=goal.title,
        content=goal.description,
        status=goal.status or "draft",
        progress_rate=goal.progress_rate or Decimal("0")
    )
    
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


def update_monthly_goal(
    db: Session,
    goal_id: int,
    goal_data: MonthlyGoalUpdate
) -> Optional[MonthlyGoal]:
    """更新月度目标"""
    db_goal = get_monthly_goal(db, goal_id)
    if not db_goal:
        return None
    
    update_data = goal_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_goal, field, value)
    
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


def publish_monthly_goal(db: Session, goal_id: int) -> Optional[MonthlyGoal]:
    """发布月度目标"""
    db_goal = get_monthly_goal(db, goal_id)
    if not db_goal:
        return None
    
    db_goal.status = "published"
    
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


def update_monthly_goal_progress(
    db: Session,
    goal_id: int,
    progress_data: MonthlyGoalProgressUpdate
) -> Optional[MonthlyGoal]:
    """更新月度目标进度"""
    db_goal = get_monthly_goal(db, goal_id)
    if not db_goal:
        return None
    
    db_goal.progress_rate = progress_data.progress_rate
    
    # 如果进度达到100%，自动更新状态为completed
    if progress_data.progress_rate >= 100:
        db_goal.status = "completed"
    
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


def delete_monthly_goal(db: Session, goal_id: int) -> bool:
    """删除月度目标（软删除）"""
    db_goal = get_monthly_goal(db, goal_id)
    if not db_goal:
        return False
    
    db_goal.is_deleted = True
    db.commit()
    return True


def calculate_monthly_goal_progress(db: Session, goal_id: int) -> Decimal:
    """计算月度目标进度（基于周目标进度的平均值）"""
    weekly_goals = db.query(WeeklyGoal).filter(
        WeeklyGoal.goal_id == goal_id,
        WeeklyGoal.is_deleted == False
    ).all()
    
    if not weekly_goals:
        return Decimal("0")
    
    total_progress = sum([wg.progress_rate for wg in weekly_goals])
    average_progress = total_progress / len(weekly_goals)
    
    return Decimal(str(average_progress))


# ==================== 周目标 CRUD ====================

def get_weekly_goal(db: Session, weekly_goal_id: int) -> Optional[WeeklyGoal]:
    """获取周目标详情"""
    return db.query(WeeklyGoal).filter(
        WeeklyGoal.id == weekly_goal_id,
        WeeklyGoal.is_deleted == False
    ).first()


def get_weekly_goals_by_monthly_goal(
    db: Session,
    goal_id: int
) -> List[WeeklyGoal]:
    """获取某月度目标的所有周目标"""
    return db.query(WeeklyGoal).filter(
        WeeklyGoal.goal_id == goal_id,
        WeeklyGoal.is_deleted == False
    ).order_by(WeeklyGoal.week_number).all()


def get_weekly_goals_by_user_and_month(
    db: Session,
    user_id: str,
    month: str
) -> List[WeeklyGoal]:
    """获取某用户某月份的所有周目标"""
    return db.query(WeeklyGoal).join(MonthlyGoal).filter(
        MonthlyGoal.user_id == user_id,
        MonthlyGoal.month == month,
        MonthlyGoal.is_deleted == False,
        WeeklyGoal.is_deleted == False
    ).order_by(WeeklyGoal.week_number).all()


def get_current_week_goal(
    db: Session,
    user_id: str,
    current_date: Optional[date] = None
) -> Optional[dict]:
    """获取当前周目标（用于日报填报）
    
    根据当前日期判断属于哪个月份的第几周，返回对应的周目标
    """
    if current_date is None:
        current_date = date.today()
    
    # 格式化当前月份
    current_month = current_date.strftime("%Y-%m")
    
    # 查找当前月份的已发布月度目标
    monthly_goal = db.query(MonthlyGoal).filter(
        MonthlyGoal.user_id == user_id,
        MonthlyGoal.month == current_month,
        MonthlyGoal.status == "published",
        MonthlyGoal.is_deleted == False
    ).first()
    
    if not monthly_goal:
        return None
    
    # 计算当前日期是该月的第几周
    week_number = get_week_number_in_month(current_date)
    
    # 查找对应的周目标
    weekly_goal = db.query(WeeklyGoal).filter(
        WeeklyGoal.goal_id == monthly_goal.id,
        WeeklyGoal.week_number == week_number,
        WeeklyGoal.is_deleted == False
    ).first()
    
    if weekly_goal:
        return {
            "weekly_goal": weekly_goal,
            "month": monthly_goal.month,
            "month_title": monthly_goal.title,
            "week_number": week_number
        }
    
    return None


def get_week_number_in_month(date_obj: date) -> int:
    """计算日期是该月的第几周"""
    # 获取该月第一天是星期几 (0=Monday, 6=Sunday)
    first_day_weekday = date_obj.replace(day=1).weekday()
    # 计算该日期是该月的第几周
    week_number = (date_obj.day + first_day_weekday - 1) // 7 + 1
    return min(week_number, 5)  # 最多5周


def create_weekly_goal(
    db: Session,
    goal_id: int,
    weekly_goal_data: dict
) -> WeeklyGoal:
    """创建周目标"""
    # 检查月度目标是否存在
    monthly_goal = get_monthly_goal(db, goal_id)
    if not monthly_goal:
        raise ValueError("月度目标不存在")
    
    # 检查该周次是否已存在
    existing = db.query(WeeklyGoal).filter(
        WeeklyGoal.goal_id == goal_id,
        WeeklyGoal.week_number == weekly_goal_data.get("week_number"),
        WeeklyGoal.is_deleted == False
    ).first()
    
    if existing:
        raise ValueError(f"第 {weekly_goal_data.get('week_number')} 周目标已存在")
    
    db_weekly_goal = WeeklyGoal(
        goal_id=goal_id,
        week_number=weekly_goal_data.get("week_number"),
        title=weekly_goal_data.get("title"),
        content=weekly_goal_data.get("content") or weekly_goal_data.get("description"),
        progress_rate=weekly_goal_data.get("progress_rate", Decimal("0")),
        status=weekly_goal_data.get("status", "pending"),
        start_date=weekly_goal_data.get("start_date"),
        end_date=weekly_goal_data.get("end_date")
    )
    
    db.add(db_weekly_goal)
    db.commit()
    db.refresh(db_weekly_goal)
    
    # 更新月度目标进度
    update_monthly_progress_from_weekly(db, goal_id)
    
    return db_weekly_goal


def update_weekly_goal(
    db: Session,
    weekly_goal_id: int,
    weekly_goal_data: dict
) -> Optional[WeeklyGoal]:
    """更新周目标"""
    db_weekly_goal = get_weekly_goal(db, weekly_goal_id)
    if not db_weekly_goal:
        return None
    
    update_data = {k: v for k, v in weekly_goal_data.items() if v is not None}
    for field, value in update_data.items():
        setattr(db_weekly_goal, field, value)
    
    db.add(db_weekly_goal)
    db.commit()
    db.refresh(db_weekly_goal)
    
    # 更新月度目标进度
    update_monthly_progress_from_weekly(db, db_weekly_goal.goal_id)
    
    return db_weekly_goal


def update_weekly_goal_progress(
    db: Session,
    weekly_goal_id: int,
    progress_rate: Decimal
) -> Optional[WeeklyGoal]:
    """更新周目标进度"""
    db_weekly_goal = get_weekly_goal(db, weekly_goal_id)
    if not db_weekly_goal:
        return None
    
    db_weekly_goal.progress_rate = progress_rate
    
    # 如果进度达到100%，自动更新状态为completed
    if progress_rate >= 100:
        db_weekly_goal.status = "completed"
    elif progress_rate > 0:
        db_weekly_goal.status = "in_progress"
    
    db.add(db_weekly_goal)
    db.commit()
    db.refresh(db_weekly_goal)
    
    # 更新月度目标进度
    update_monthly_progress_from_weekly(db, db_weekly_goal.goal_id)
    
    return db_weekly_goal


def delete_weekly_goal(db: Session, weekly_goal_id: int) -> bool:
    """删除周目标（软删除）"""
    db_weekly_goal = get_weekly_goal(db, weekly_goal_id)
    if not db_weekly_goal:
        return False
    
    goal_id = db_weekly_goal.goal_id
    
    db_weekly_goal.is_deleted = True
    db.commit()
    
    # 更新月度目标进度
    update_monthly_progress_from_weekly(db, goal_id)
    
    return True


def update_monthly_progress_from_weekly(db: Session, goal_id: int):
    """根据周目标进度更新月度目标进度"""
    new_progress = calculate_monthly_goal_progress(db, goal_id)
    
    monthly_goal = get_monthly_goal(db, goal_id)
    if monthly_goal:
        monthly_goal.progress_rate = new_progress
        db.add(monthly_goal)
        db.commit()


# ==================== 日报目标关联 CRUD ====================

def get_daily_report_goal(db: Session, id: int) -> Optional[DailyReportGoal]:
    """获取日报目标关联详情"""
    return db.query(DailyReportGoal).filter(
        DailyReportGoal.id == id,
        DailyReportGoal.is_deleted == False
    ).first()


def get_daily_report_goals_by_report(
    db: Session,
    daily_report_id: int
) -> List[DailyReportGoal]:
    """获取某日报的所有目标关联"""
    return db.query(DailyReportGoal).filter(
        DailyReportGoal.daily_report_id == daily_report_id,
        DailyReportGoal.is_deleted == False
    ).all()


def get_daily_report_goals_by_weekly_goal(
    db: Session,
    weekly_goal_id: int
) -> List[DailyReportGoal]:
    """获取某周目标的所有日报关联"""
    return db.query(DailyReportGoal).filter(
        DailyReportGoal.weekly_goal_id == weekly_goal_id,
        DailyReportGoal.is_deleted == False
    ).all()


def create_daily_report_goal(
    db: Session,
    daily_report_id: int,
    goal_data: dict
) -> DailyReportGoal:
    """创建日报目标关联"""
    db_goal_link = DailyReportGoal(
        daily_report_id=daily_report_id,
        weekly_goal_id=goal_data.get("weekly_goal_id"),
        project_id=goal_data.get("project_id"),
        project_name=goal_data.get("project_name"),
        task_node_id=goal_data.get("task_node_id"),
        task_node_name=goal_data.get("task_node_name"),
        notes=goal_data.get("notes"),
        completion_rate=goal_data.get("completion_rate", Decimal("0"))
    )
    
    db.add(db_goal_link)
    db.commit()
    db.refresh(db_goal_link)
    
    # 更新周目标进度
    update_weekly_progress_from_daily_reports(db, goal_data.get("weekly_goal_id"))
    
    return db_goal_link


def update_daily_report_goal(
    db: Session,
    id: int,
    goal_data: dict
) -> Optional[DailyReportGoal]:
    """更新日报目标关联"""
    db_goal_link = get_daily_report_goal(db, id)
    if not db_goal_link:
        return None
    
    old_weekly_goal_id = db_goal_link.weekly_goal_id
    
    update_data = {k: v for k, v in goal_data.items() if v is not None}
    for field, value in update_data.items():
        setattr(db_goal_link, field, value)
    
    db.add(db_goal_link)
    db.commit()
    db.refresh(db_goal_link)
    
    # 更新相关周目标进度
    if old_weekly_goal_id:
        update_weekly_progress_from_daily_reports(db, old_weekly_goal_id)
    if db_goal_link.weekly_goal_id and db_goal_link.weekly_goal_id != old_weekly_goal_id:
        update_weekly_progress_from_daily_reports(db, db_goal_link.weekly_goal_id)
    
    return db_goal_link


def delete_daily_report_goal(db: Session, id: int) -> bool:
    """删除日报目标关联（软删除）"""
    db_goal_link = get_daily_report_goal(db, id)
    if not db_goal_link:
        return False
    
    weekly_goal_id = db_goal_link.weekly_goal_id
    
    db_goal_link.is_deleted = True
    db.commit()
    
    # 更新周目标进度
    if weekly_goal_id:
        update_weekly_progress_from_daily_reports(db, weekly_goal_id)
    
    return True


def update_weekly_progress_from_daily_reports(db: Session, weekly_goal_id: int):
    """根据日报关联更新周目标进度"""
    daily_goals = db.query(DailyReportGoal).filter(
        DailyReportGoal.weekly_goal_id == weekly_goal_id,
        DailyReportGoal.is_deleted == False
    ).all()
    
    if not daily_goals:
        # 如果没有日报关联，重置进度为0
        update_weekly_goal_progress(db, weekly_goal_id, Decimal("0"))
        return
    
    # 计算平均完成度
    total_completion = sum([dg.completion_rate for dg in daily_goals])
    average_completion = total_completion / len(daily_goals)
    
    # 更新周目标进度
    weekly_goal = get_weekly_goal(db, weekly_goal_id)
    if weekly_goal:
        weekly_goal.progress_rate = average_completion
        
        # 更新状态
        if average_completion >= 100:
            weekly_goal.status = "completed"
        elif average_completion > 0:
            weekly_goal.status = "in_progress"
        else:
            weekly_goal.status = "pending"
        
        db.add(weekly_goal)
        db.commit()
        
        # 更新月度目标进度
        update_monthly_progress_from_weekly(db, weekly_goal.goal_id)


# ==================== 从项目任务自动生成目标 ====================

async def generate_goals_from_tasks(
    db: Session,
    user_id: str,
    user_name: str,
    year: int
) -> dict:
    """
    根据用户负责的项目任务自动生成月度目标和周目标（支持AI生成）
    """
    from app.models.project_task import ProjectTask
    from app.models.project import Project
    from app.services.ai_goal_generator import generate_goals_with_ai, generate_goals_fallback
    import calendar
    import asyncio
    
    result = {
        "year": year,
        "user_id": user_id,
        "user_name": user_name,
        "generated_months": [],
        "total_tasks": 0,
        "errors": []
    }
    
    # 1. 获取该用户负责的所有未删除任务
    tasks = db.query(ProjectTask).filter(
        ProjectTask.assignee_id == user_id,
        ProjectTask.is_deleted == False
    ).all()
    
    if not tasks:
        result["errors"].append("未找到该用户负责的项目任务")
        return result
    
    result["total_tasks"] = len(tasks)
    
    # 打印任务信息用于调试
    print(f"Found {len(tasks)} tasks for user {user_name} ({user_id})")
    for t in tasks:
        print(f"  Task: {t.task_name}, start_date: {t.start_date}, project_id: {t.project_id}")
    
    # 2. 按月份分组任务 - 严格按指定年份过滤
    tasks_by_month = {}
    for task in tasks:
        if task.start_date:
            task_month = task.start_date.strftime("%Y-%m")
            task_year = task.start_date.year
            # 严格按指定年份过滤
            if task_year == year:
                if task_month not in tasks_by_month:
                    tasks_by_month[task_month] = []
                tasks_by_month[task_month].append(task)
    
    print(f"Tasks grouped by month for year {year}: {list(tasks_by_month.keys())}")
    
    # 3. 为每个月生成月度目标和周目标
    for month_str, month_tasks in tasks_by_month.items():
        try:
            year_val, month_val = map(int, month_str.split("-"))
            
            # 检查是否已存在该月目标
            existing_goal = get_monthly_goal_by_user_and_month(db, user_id, month_str)
            if existing_goal:
                result["generated_months"].append({
                    "month": month_str,
                    "status": "skipped",
                    "reason": "该月目标已存在"
                })
                continue
            
            # 收集项目信息
            project_ids = set()
            for task in month_tasks:
                if task.project_id:
                    project_ids.add(task.project_id)
            
            projects = []
            for pid in project_ids:
                if pid.isdigit():
                    project = db.query(Project).filter(
                        Project.id == int(pid),
                        Project.is_deleted == False
                    ).first()
                    if project:
                        projects.append({
                            "name": project.name,
                            "leader": project.leader
                        })
            
            # 构建任务信息
            tasks_info = []
            for task in month_tasks:
                project_name = ""
                if task.project_id and task.project_id.isdigit():
                    proj = db.query(Project).filter(Project.id == int(task.project_id)).first()
                    if proj:
                        project_name = proj.name
                
                tasks_info.append({
                    "task_name": task.task_name,
                    "project_name": project_name,
                    "start_date": task.start_date.strftime("%Y-%m-%d") if task.start_date else "",
                    "end_date": task.end_date.strftime("%Y-%m-%d") if task.end_date else ""
                })
            
            # 计算四周时间范围
            _, days_in_month = calendar.monthrange(year_val, month_val)
            week_ranges = []
            for week_num in range(1, 5):
                week_start_day = (week_num - 1) * 7 + 1
                week_end_day = min(week_num * 7, days_in_month)
                week_start = date(year_val, month_val, week_start_day)
                week_end = date(year_val, month_val, week_end_day)
                week_ranges.append({
                    "start_date": week_start.strftime("%Y-%m-%d"),
                    "end_date": week_end.strftime("%Y-%m-%d")
                })
            
            # 调用AI生成目标
            ai_result = None
            ai_error = None
            try:
                print(f"开始AI生成目标: user={user_name}, month={month_str}, projects={len(projects)}, tasks={len(tasks_info)}")
                ai_result = await asyncio.wait_for(
                    generate_goals_with_ai(
                        user_name=user_name,
                        month=month_str,
                        projects=projects,
                        tasks=tasks_info,
                        week_ranges=week_ranges
                    ),
                    timeout=30.0
                )
                print(f"AI生成成功: {ai_result is not None}")
            except Exception as e:
                ai_error = str(e)
                print(f"AI生成失败，使用备用方案: {e}")
            
            # 如果AI生成失败，使用备用方案
            if not ai_result:
                project_names = [p["name"] for p in projects]
                task_names = [t["task_name"] for t in tasks_info]
                ai_result = generate_goals_fallback(month_str, project_names, task_names)
            
            # 创建月度目标
            monthly_goal = create_monthly_goal(
                db,
                goal=MonthlyGoalCreate(
                    month=month_str,
                    title=ai_result["monthly_goal"]["title"],
                    description=ai_result["monthly_goal"]["description"],
                    status="draft",
                    progress_rate=Decimal("0")
                ),
                user_id=user_id,
                user_name=user_name
            )
            
            # 创建周目标
            created_weeks = []
            for week_goal in ai_result["weekly_goals"]:
                week_num = week_goal["week_number"]
                week_range = week_ranges[week_num - 1]
                
                try:
                    weekly_goal = create_weekly_goal(
                        db,
                        goal_id=monthly_goal.id,
                        weekly_goal_data={
                            "week_number": week_num,
                            "title": week_goal["title"],
                            "content": week_goal["description"],
                            "start_date": week_range["start_date"],
                            "end_date": week_range["end_date"]
                        }
                    )
                    created_weeks.append({
                        "week_number": week_num,
                        "title": week_goal["title"]
                    })
                except ValueError:
                    pass
            
            result["generated_months"].append({
                "month": month_str,
                "status": "created",
                "monthly_goal_id": monthly_goal.id,
                "title": ai_result["monthly_goal"]["title"],
                "task_count": len(month_tasks),
                "weekly_goals": created_weeks,
                "ai_generated": ai_result is not None and ai_error is None,
                "ai_error": ai_error
            })
            
        except Exception as e:
            result["generated_months"].append({
                "month": month_str,
                "status": "error",
                "error": str(e)
            })
            result["errors"].append(f"生成 {month_str} 目标失败: {str(e)}")
    
    return result
