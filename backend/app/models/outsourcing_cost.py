from sqlalchemy import Column, Integer, String, Float, Date, Text, Numeric, Boolean
from app.core.database import Base

class OutsourcingCost(Base):
    __tablename__ = "outsourcing_costs"
    
    cost_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(50), nullable=False)
    service_type = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Numeric(10, 2), default=1)
    unit_price = Column(Numeric(15, 2), default=0)
    total_price = Column(Numeric(18, 2), default=0.00)
    cost_type = Column(String(50), default="预算")
    remark = Column(Text, nullable=True)
    create_time = Column(Date, nullable=True)
    update_time = Column(Date, nullable=True)
    is_deleted = Column(Boolean, default=False)
    service_type_id = Column(Integer, nullable=True)