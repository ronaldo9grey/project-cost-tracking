from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ProjectTask(Base):
    __tablename__ = "project_tasks"
    
    task_id = Column(String(50), primary_key=True, index=True)
    project_id = Column(String(50), nullable=False, index=True)
    task_name = Column(String(200), nullable=False)
    parent_task_id = Column(String(50), nullable=True)
    task_level = Column(Integer, default=1)
    assignee = Column(String(100), nullable=True)
    assignee_id = Column(String(300), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    planned_hours = Column(Float, default=0.0)
    actual_hours = Column(Float, default=0.0)
    adjusted_hours = Column(Float, default=0.0)
    budget_cost = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    status = Column(String(50), default="未开始")
    remark = Column(Text, nullable=True)
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, index=True)
    progress = Column(Float, default=0.0)
    actual_end_date = Column(Date, nullable=True, index=True)
    evaluation = Column(Float, nullable=True)
    evaluation_desc = Column(Text, nullable=True)
    progress_rootcause = Column(Text, nullable=True)
    measures_results = Column(Text, nullable=True)
    attachment = Column(Text, nullable=True)
    isNode = Column(Boolean, nullable=True)
    leaf_node = Column(String, nullable=True)
