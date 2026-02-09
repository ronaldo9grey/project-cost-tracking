"""
项目跟踪相关数据库模型
"""
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Numeric, Text
from sqlalchemy.sql import func
from app.database import Base

class ProjectTracking(Base):
    """项目跟踪主表"""
    __tablename__ = "project_trackings"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(50), nullable=False, index=True)
    project_name = Column(String(200), nullable=False)
    
    # 跟踪状态
    overall_progress = Column(Numeric(5, 2), default=0.00)
    tracking_status = Column(String(20), default='进行中', index=True)
    last_update_time = Column(DateTime, default=func.now())
    
    # 统计信息
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    total_reports = Column(Integer, default=0)
    cde_evaluations = Column(Integer, default=0)
    
    # 风险等级
    risk_level = Column(String(10), default='低', index=True)
    priority_level = Column(String(10), default='中', index=True)
    
    # 时间戳
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, index=True)


class TaskTracking(Base):
    """任务跟踪表"""
    __tablename__ = "task_trackings"
    
    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(Integer, nullable=False, index=True)
    
    # 任务基本信息
    task_id = Column(String(50), nullable=False, index=True)
    task_name = Column(String(200), nullable=False)
    assignee = Column(String(100))
    assignee_id = Column(String(50))
    
    # 计划信息
    planned_start = Column(Date)
    planned_end = Column(Date)
    
    # 实际跟踪信息
    actual_start = Column(Date)
    actual_end = Column(Date)
    current_progress = Column(Numeric(5, 2), default=0.00)
    delay_days = Column(Integer, default=0)
    
    # 关联信息
    related_reports_count = Column(Integer, default=0)
    cde_evaluation_count = Column(Integer, default=0)
    
    # 状态跟踪
    status = Column(String(20), default='未开始', index=True)
    priority_level = Column(String(10), default='中')
    risk_level = Column(String(10), default='低')
    
    # 时间戳
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, index=True)


class TaskReportLink(Base):
    """任务日报关联表"""
    __tablename__ = "task_report_links"
    
    id = Column(Integer, primary_key=True, index=True)
    task_tracking_id = Column(Integer, nullable=False, index=True)
    
    # 关联的日报信息
    report_id = Column(Integer, nullable=False, index=True)
    work_item_id = Column(Integer, nullable=False, index=True)
    
    # 关联详情
    employee_id = Column(String(50), nullable=False, index=True)
    employee_name = Column(String(100), nullable=False)
    report_date = Column(Date, nullable=False, index=True)
    
    # 工作详情
    work_content = Column(Text, nullable=False)
    hours_spent = Column(Numeric(8, 2), default=0.00)
    progress_contribution = Column(Numeric(5, 2), default=0.00)
    
    # 时间戳
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, index=True)


class ProjectReportSummary(Base):
    """项目日报汇总表"""
    __tablename__ = "project_report_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(Integer, nullable=False, index=True)
    
    # 汇总期间
    summary_date = Column(Date, nullable=False, index=True)
    
    # 人员统计
    involved_employees = Column(Integer, default=0)
    total_work_hours = Column(Numeric(10, 2), default=0.00)
    
    # 任务进展
    tasks_progressed = Column(Integer, default=0)
    tasks_completed = Column(Integer, default=0)
    
    # CDE评价统计
    cde_evaluations_count = Column(Integer, default=0)
    cde_evaluations_detail = Column(Text)
    
    # 问题和风险
    issues_raised = Column(Integer, default=0)
    risks_identified = Column(Integer, default=0)
    
    # 汇总内容
    daily_summary = Column(Text)
    next_day_plan = Column(Text)
    
    # 时间戳
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, index=True)


class TrackingNotification(Base):
    """跟踪通知表"""
    __tablename__ = "tracking_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(Integer, nullable=False, index=True)
    
    # 通知类型
    notification_type = Column(String(20), nullable=False, index=True)
    priority_level = Column(String(10), default='中')
    
    # 通知内容
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    related_task_id = Column(String(50))
    related_report_id = Column(Integer)
    
    # 接收人信息
    recipient_id = Column(String(50), nullable=False, index=True)
    recipient_name = Column(String(100), nullable=False)
    recipient_role = Column(String(50))
    
    # 通知状态
    is_read = Column(Boolean, default=False, index=True)
    is_sent = Column(Boolean, default=False, index=True)
    sent_time = Column(DateTime)
    read_time = Column(DateTime)
    
    # 推送方式
    push_methods = Column(String(100))
    
    # 时间戳
    create_time = Column(DateTime, default=func.now())
    update_time = Column(DateTime, default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, index=True)
