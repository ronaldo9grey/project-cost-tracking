from sqlalchemy import Column, Integer, String, Float, Date, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class DailyReport(Base):
    __tablename__ = "daily_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(Date, nullable=False, index=True)
    employee_id = Column(String(50), nullable=False, index=True)
    employee_name = Column(String(100), nullable=False)
    
    # 基本信息字段（汇总信息）
    tomorrow_plan = Column(Text, nullable=True)
    work_target = Column(Text, nullable=True)  # 工作目标字段
    key_work_tracking = Column(Text, nullable=True)  # 近期重点工作跟踪推进情况字段
    self_evaluation = Column(String(10), nullable=True)  # 自我评价
    planned_hours = Column(Float, default=0)
    attachments_id = Column(Integer, nullable=True)  # 附件ID
    
    # 状态字段
    status = Column(String(20), default="待提交")
    submitted_at = Column(DateTime, nullable=True)
    
    # 时间戳
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # 关系：与工作事项表和评价表的关系
    work_items = relationship("DailyWorkItem", back_populates="daily_report", cascade="all, delete-orphan")
    evaluations = relationship("DailyReportEvaluation", back_populates="daily_report", cascade="all, delete-orphan")


class DailyReportEvaluation(Base):
    __tablename__ = "daily_report_evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("daily_reports.id"), nullable=False, index=True)
    
    # 评价信息
    supervisor_score = Column(Integer, default=0)
    supervisor_comment = Column(Text, nullable=True)
    supervisor_id = Column(String(50), nullable=True)
    supervisor_name = Column(String(100), nullable=True)
    evaluated_at = Column(DateTime, server_default=func.now())
    
    # 时间戳
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # 关系：反向关系指向DailyReport
    daily_report = relationship("DailyReport", back_populates="evaluations")


class DailyWorkItem(Base):
    __tablename__ = "daily_work_items"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("daily_reports.id"), nullable=False, index=True)
    
    # 项目任务信息
    project_id = Column(String(50), nullable=True)
    project_name = Column(String(200), nullable=True)
    task_id = Column(String(50), nullable=True)
    task_name = Column(String(200), nullable=True)
    
    # 工作内容
    work_content = Column(Text, nullable=False)
    
    # 时间和进度
    start_time = Column(String(8), nullable=True)  # 存储格式: "08:15"
    end_time = Column(String(8), nullable=True)    # 存储格式: "18:00"
    hours_spent = Column(Float, default=0)
    progress_status = Column(String(20), default="正常")
    progress_percentage = Column(Float, default=0)
    delay_hours = Column(Float, default=0)
    improvement_result = Column(Text, nullable=True)
    key_work_tracking = Column(Text, nullable=True)  # 重点工作跟踪
    
    # 结果和评价
    result = Column(Text, nullable=True)
    measures = Column(Text, nullable=True)
    evaluation = Column(String(1), nullable=True)
    
    # 时间戳
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    # 关系：反向关系指向DailyReport
    daily_report = relationship("DailyReport", back_populates="work_items")


class DailyWorkLog(Base):
    __tablename__ = "daily_work_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, nullable=True)
    project_id = Column(String(50), nullable=False, index=True)
    project_name = Column(String(200), nullable=False)
    task_id = Column(String(50), nullable=True, index=True)
    task_name = Column(String(200), nullable=True)
    employee_id = Column(String(50), nullable=False, index=True)
    employee_name = Column(String(100), nullable=False)
    work_date = Column(Date, nullable=False, index=True)
    work_content = Column(Text, nullable=True)
    hours = Column(Float, default=0, nullable=False)
    status = Column(String(20), default="待审核")
    
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
