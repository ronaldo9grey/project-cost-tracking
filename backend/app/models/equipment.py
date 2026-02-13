from sqlalchemy import Column, Integer, String, Date, Text
from app.core.database import Base

class Equipment(Base):
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    model = Column(String(255), nullable=False)
    specification = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="在用")
    location = Column(String(255), nullable=True)
    purchase_date = Column(Date, nullable=True)
    maintainer_id = Column(Integer, nullable=True)
    maintainer = Column(String(100), nullable=True)
    remark = Column(Text, nullable=True)
    create_time = Column(Date, nullable=True)
    update_time = Column(Date, nullable=True)
    is_deleted = Column(Integer, nullable=False, default=0)