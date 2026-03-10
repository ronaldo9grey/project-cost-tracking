from sqlalchemy import Column, Integer, String, Float, Date, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class MonthlyGoal(Base):
    """月度目标表"""
    __tablename__ = "monthly_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)  # 员工ID
    user_name = Column(String(100))  # 员工姓名
    month = Column(String(7), nullable=False, index=True)  # 月份 (格式: 2026-02)
    title = Column(String(500), nullable=False)  # 目标标题
    content = Column(Text)  # 工作内容 (可多行)
    status = Column(String(20), default="draft")  # 状态: draft/published/completed
    progress_rate = Column(Numeric(5, 2), default=0)  # 完成进度 0-100
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # 关系：与周目标表的关系
    weekly_goals = relationship("WeeklyGoal", back_populates="monthly_goal", cascade="all, delete-orphan")
    
    class Config:
        orm_mode = True


class WeeklyGoal(Base):
    """周目标表"""
    __tablename__ = "weekly_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("monthly_goals.id"), nullable=False, index=True)  # 关联的月度目标ID
    week_number = Column(Integer, nullable=False)  # 周次 (1-5)
    title = Column(String(500), nullable=False)  # 周目标标题
    content = Column(Text)  # 工作内容
    progress_rate = Column(Numeric(5, 2), default=0)  # 完成进度 0-100
    status = Column(String(20), default="pending")  # 状态: pending/in_progress/completed
    start_date = Column(Date)  # 周开始日期
    end_date = Column(Date)  # 周结束日期
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # 关系：反向关系指向MonthlyGoal
    monthly_goal = relationship("MonthlyGoal", back_populates="weekly_goals")
    
    # 关系：与日报目标关联表的关系
    daily_report_goals = relationship("DailyReportGoal", back_populates="weekly_goal", cascade="all, delete-orphan")
    
    class Config:
        orm_mode = True


class DailyReportGoal(Base):
    """日报目标关联表"""
    __tablename__ = "daily_report_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    daily_report_id = Column(Integer, ForeignKey("daily_reports.id"), nullable=False, index=True)  # 日报ID
    weekly_goal_id = Column(Integer, ForeignKey("weekly_goals.id"), nullable=False, index=True)  # 周目标ID
    project_id = Column(String(50))  # 项目ID
    project_name = Column(String(200))  # 项目名称
    task_node_id = Column(String(50))  # 任务节点ID
    task_node_name = Column(String(200))  # 任务节点名称
    notes = Column(Text)  # 填报说明
    completion_rate = Column(Numeric(5, 2), default=0)  # 该任务完成度
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # 关系：反向关系指向WeeklyGoal
    weekly_goal = relationship("WeeklyGoal", back_populates="daily_report_goals")
    
    class Config:
        orm_mode = True
