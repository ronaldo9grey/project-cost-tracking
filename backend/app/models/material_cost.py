from sqlalchemy import Column, Integer, String, Float, Date, Text, Numeric, Boolean
from app.core.database import Base

class MaterialCost(Base):
    __tablename__ = "material_costs"
    
    cost_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(50), nullable=False)
    material_id = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    specification = Column(String(200), nullable=True)
    unit = Column(String(50), nullable=True)
    quantity = Column(Numeric(15, 2), default=0)
    unit_price = Column(Numeric(15, 2), default=0)
    total_price = Column(Numeric(18, 2), default=0.00)
    cost_type = Column(String(50), default="预算")
    remark = Column(Text, nullable=True)
    create_time = Column(Date, nullable=True)
    update_time = Column(Date, nullable=True)
    is_deleted = Column(Boolean, default=False)