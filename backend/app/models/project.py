from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, Text, cast
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), index=True, nullable=False)
    describe = Column(Text, nullable=True)  # 项目描述字段，对应数据库中的describe列
    leader = Column(String(100), nullable=False)
    leader_id = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, default="进行中", index=True)
    progress = Column(Integer, default=0)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    contract_date = Column(Date, nullable=True)
    contract_no = Column(String(100), nullable=True)
    tax_rate = Column(Float, default=0.13)
    contract_amount = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)
    target_profit = Column(Float, default=0.0)
    actual_profit = Column(Float, default=0.0)
    created_by_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, index=True)
    # 总成本
    budget_total_cost = Column(Float, default=0.0)
    actual_total_cost = Column(Float, default=0.0)
    # 各成本类型的预算和实际值
    material_budget = Column(Float, default=0.0)
    material_actual = Column(Float, default=0.0, name="material_cost")
    outsourcing_budget = Column(Float, default=0.0)
    outsourcing_actual = Column(Float, default=0.0, name="outsourcing_cost")
    indirect_budget = Column(Float, default=0.0)
    indirect_actual = Column(Float, default=0.0, name="indirect_cost")
    labor_budget = Column(Float, default=0.0)
    labor_actual = Column(Float, default=0.0, name="labor_cost")
    
    # 关系
    # 移除了与Task模型的关系定义，因为Task模型中的project_id是String类型，与Project.id（Integer）类型不匹配
    # tasks = relationship("Task", back_populates="project")
    # 移除了与成本模型的关系定义，因为成本模型中的project_id是String类型，与Project.id（Integer）类型不匹配
    # 且没有显式的ForeignKey约束，导致关系无法正常工作


# 注：Task模型已移至project_task.py文件中，使用ProjectTask名称定义
# 为了避免表名冲突，已删除此处的Task模型定义
# 如果需要使用项目任务模型，请从app.models.project_task import ProjectTask


# Subtask模型已废弃，建议使用ProjectTask模型的parent_task_id字段实现父子任务关系
# 为了避免与ProjectTask模型冲突，已注释掉Subtask模型定义
# class Subtask(Base):
#     __tablename__ = "subtasks"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
#     name = Column(String(100), nullable=False)
#     description = Column(Text, nullable=True)
#     status = Column(String(20), nullable=False, default="todo", index=True)  # todo, in_progress, done
#     assigned_to = Column(String(50), nullable=True)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
#     deleted_at = Column(DateTime, nullable=True)
#     is_deleted = Column(Boolean, default=False, index=True)
#     
#     # 关系
#     task = relationship("Task", back_populates="subtasks")



