from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"
    
    supplier_id = Column(Integer, primary_key=True, index=True)
    supplier_name = Column(String(200), nullable=False, index=True)
    contact_person = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(100), nullable=True)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(50), nullable=True)
    updated_by = Column(String(50), nullable=True)
    remarks = Column(Text, nullable=True)


class SupplierEvaluation(Base):
    __tablename__ = "supplier_evaluations"
    
    evaluation_id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=False, index=True)
    delivery_punctuality_score = Column(Integer, nullable=True)
    delivery_punctuality_evidence = Column(Text, nullable=True)
    quality_consistency_score = Column(Integer, nullable=True)
    quality_consistency_evidence = Column(Text, nullable=True)
    service_response_score = Column(Integer, nullable=True)
    service_response_evidence = Column(Text, nullable=True)
    cooperation_score = Column(Integer, nullable=True)
    cooperation_evidence = Column(Text, nullable=True)
    overall_score = Column(Numeric(3, 1), nullable=True)
    evaluation_date = Column(Date, nullable=True)
    evaluator = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    remarks = Column(Text, nullable=True)


class SupplierRanking(Base):
    __tablename__ = "supplier_rankings"
    
    ranking_id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=False, index=True)
    supplier_name = Column(String(200), nullable=True)
    total_score = Column(Numeric(5, 2), nullable=True)
    suggested_level = Column(String(200), nullable=True)
    ranking_date = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(50), nullable=True)
    remarks = Column(Text, nullable=True)


class SupplierAIAnalysis(Base):
    __tablename__ = "supplier_ai_analysis"
    
    analysis_id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.supplier_id"), nullable=True, index=True)
    analysis_date = Column(Date, nullable=True)
    analysis_result = Column(Text, nullable=True)
    generated_at = Column(DateTime, nullable=True)
    generated_by = Column(String(50), default='AI系统')
    status = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    remarks = Column(Text, nullable=True)
