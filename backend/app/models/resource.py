from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)


class Personnel(Base):
    __tablename__ = "personnel"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), index=True, nullable=False, unique=True)
    name = Column(String(100), index=True, nullable=False)
    department = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    created_by_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    password = Column(String(255), nullable=False, default="123456")
    role_id = Column(Integer, nullable=True)
    
    @property
    def username(self):
        return self.employee_id


class PersonnelRate(Base):
    __tablename__ = "personnel_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, nullable=False)
    rate_type = Column(String(20), nullable=False)
    rate = Column(Float, nullable=False, default=0.0)
    effective_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)


class Material(Base):
    __tablename__ = "materials"
    
    material_id = Column(String(50), primary_key=True, index=True)
    material_name = Column(String(200), nullable=False, index=True)
    specification = Column(String(200), nullable=True)
    unit = Column(String(50), nullable=True)
    stock_quantity = Column(Float, default=0.0)
    unit_price = Column(Float, default=0.0)
    supplier = Column(String(200), nullable=True)
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)


class Equipment(Base):
    __tablename__ = "equipment"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    model = Column(String(50), nullable=True)
    serial_number = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default="available")
    purchase_date = Column(Date, nullable=True)
    purchase_price = Column(Float, nullable=True)
    location = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)


class IndirectCostType(Base):
    __tablename__ = "indirect_cost_types"
    
    id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)


class OutsourcingServiceType(Base):
    __tablename__ = "outsourcing_service_types"
    
    id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)


class EmployeeGroupRelation(Base):
    __tablename__ = "employee_group_relations"
    
    id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String(100), nullable=False, index=True)
    group_description = Column(Text, nullable=True)
    relation_type = Column(String(20), nullable=False)  # 'member' or 'supervisor'
    employee_id = Column(String(50), nullable=True, index=True)
    employee_name = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    supervisor_position = Column(String(100), nullable=True)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(50), nullable=True)
    remarks = Column(Text, nullable=True)
