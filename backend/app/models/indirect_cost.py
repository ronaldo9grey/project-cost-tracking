from sqlalchemy import Column, Integer, String, Float, Date, Text, Numeric, Boolean
from app.core.database import Base

class IndirectCost(Base):
    __tablename__ = "indirect_costs"
    
    cost_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(50), nullable=False)
    cost_type = Column(String(200), nullable=False)
    amount = Column(Numeric(15, 2), default=0)
    description = Column(Text, nullable=True)
    cost_type_flag = Column(String(50), default="预算")
    remark = Column(Text, nullable=True)
    create_time = Column(Date, nullable=True)
    update_time = Column(Date, nullable=True)
    is_deleted = Column(Boolean, default=False)
    total_price = Column(Numeric(18, 2), default=0.00)
    indirect_type_id = Column(Integer, nullable=True)