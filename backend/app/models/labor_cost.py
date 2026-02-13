from sqlalchemy import Column, Integer, String, Float, Date, Text, Numeric, Boolean
from app.core.database import Base

class LaborCost(Base):
    __tablename__ = "labor_costs"
    
    cost_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(50), nullable=False)
    employee_id = Column(String(50), nullable=False)
    year_month = Column(String(7), nullable=True)
    budget_hours = Column(Numeric(10, 2), default=0)
    actual_hours = Column(Numeric(10, 2), default=0)
    adjusted_hours = Column(Numeric(10, 2), default=0)
    hourly_rate = Column(Numeric(10, 2), default=0)
    budget_cost = Column(Numeric(15, 2), default=0)
    actual_cost = Column(Numeric(15, 2), default=0)
    adjusted_cost = Column(Numeric(15, 2), default=0)
    remark = Column(Text, nullable=True)
    create_time = Column(Date, nullable=True)
    update_time = Column(Date, nullable=True)
    is_deleted = Column(Boolean, default=False)
    task_id = Column(Integer, nullable=True)
    mode = Column(String(1), nullable=True)