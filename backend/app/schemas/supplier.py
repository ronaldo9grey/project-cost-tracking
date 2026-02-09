from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class SupplierBase(BaseModel):
    supplier_name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    status: Optional[int] = 1
    remarks: Optional[str] = None


class SupplierCreate(SupplierBase):
    supplier_name: str


class SupplierUpdate(SupplierBase):
    pass


class SupplierResponse(SupplierBase):
    id: int
    supplier_id: int
    name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SupplierEvaluationBase(BaseModel):
    delivery_punctuality_score: Optional[int] = None
    quality_consistency_score: Optional[int] = None
    service_response_score: Optional[int] = None
    cooperation_score: Optional[int] = None
    evaluation_date: Optional[date] = None
    evaluator: Optional[str] = None
    remarks: Optional[str] = None


class SupplierEvaluationCreate(SupplierEvaluationBase):
    delivery_punctuality_score: int
    quality_consistency_score: int
    service_response_score: int
    cooperation_score: int


class SupplierEvaluationUpdate(BaseModel):
    delivery_punctuality_score: Optional[int] = None
    quality_consistency_score: Optional[int] = None
    service_response_score: Optional[int] = None
    cooperation_score: Optional[int] = None
    evaluation_date: Optional[date] = None
    evaluator: Optional[str] = None
    remarks: Optional[str] = None


class SupplierEvaluationResponse(SupplierEvaluationBase):
    id: int
    evaluation_id: int
    supplier_id: int
    overall_score: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SupplierRankingBase(BaseModel):
    total_score: Optional[float] = None
    suggested_level: Optional[str] = None
    ranking_date: Optional[date] = None
    remarks: Optional[str] = None


class SupplierRankingCreate(SupplierRankingBase):
    supplier_id: int
    supplier_name: str
    total_score: float


class SupplierRankingUpdate(BaseModel):
    total_score: Optional[float] = None
    suggested_level: Optional[str] = None
    ranking_date: Optional[date] = None
    remarks: Optional[str] = None


class SupplierRankingResponse(SupplierRankingBase):
    id: int
    ranking_id: int
    supplier_id: int
    supplier_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SupplierAIAnalysisBase(BaseModel):
    analysis_date: Optional[date] = None
    analysis_result: Optional[str] = None
    status: Optional[int] = 1
    remarks: Optional[str] = None


class SupplierAIAnalysisCreate(SupplierAIAnalysisBase):
    supplier_id: int


class SupplierAIAnalysisResponse(SupplierAIAnalysisBase):
    id: int
    analysis_id: int
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None
    generated_at: Optional[datetime] = None
    generated_by: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
