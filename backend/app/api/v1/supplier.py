from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import date
from app.core.dependencies import get_db
from app.models.supplier import Supplier, SupplierEvaluation, SupplierRanking, SupplierAIAnalysis

router = APIRouter()


def format_date(d):
    """格式化日期"""
    if d is None:
        return None
    if isinstance(d, str):
        return d
    return d.strftime("%Y-%m-%d")


def format_datetime(dt):
    """格式化日期时间"""
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# ==================== 供应商基础管理API ====================

@router.get("/")
def get_suppliers(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[int] = None,
    name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取供应商列表"""
    try:
        query = db.query(Supplier)
        
        if status is not None:
            query = query.filter(Supplier.status == status)
        if name:
            query = query.filter(Supplier.supplier_name.contains(name))
        
        query = query.filter(Supplier.supplier_id.isnot(None))
        
        total = query.count()
        suppliers = query.order_by(Supplier.supplier_id).offset((page - 1) * size).limit(size).all()
        
        return {
            "items": [
                {
                    "id": s.supplier_id,
                    "supplier_id": s.supplier_id,
                    "name": s.supplier_name,
                    "contact_person": s.contact_person,
                    "contact_phone": s.contact_phone,
                    "contact_email": s.contact_email,
                    "status": s.status,
                    "created_at": format_datetime(s.created_at),
                    "updated_at": format_datetime(s.updated_at),
                    "remarks": s.remarks
                }
                for s in suppliers
            ],
            "total": total,
            "page": page,
            "size": size
        }
    except Exception as e:
        return {"items": [], "total": 0, "page": page, "size": size, "error": str(e)}


@router.get("/{supplier_id}")
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """获取单个供应商信息"""
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    
    return {
        "id": supplier.supplier_id,
        "supplier_id": supplier.supplier_id,
        "name": supplier.supplier_name,
        "contact_person": supplier.contact_person,
        "contact_phone": supplier.contact_phone,
        "contact_email": supplier.contact_email,
        "status": supplier.status,
        "created_at": format_datetime(supplier.created_at),
        "updated_at": format_datetime(supplier.updated_at),
        "remarks": supplier.remarks
    }


@router.post("/")
def create_supplier(
    data: dict,
    db: Session = Depends(get_db)
):
    """创建供应商"""
    try:
        supplier = Supplier(
            supplier_name=data.get("supplier_name"),
            contact_person=data.get("contact_person"),
            contact_phone=data.get("contact_phone"),
            contact_email=data.get("contact_email"),
            status=data.get("status", 1),
            remarks=data.get("remarks")
        )
        db.add(supplier)
        db.commit()
        db.refresh(supplier)
        
        return {
            "id": supplier.supplier_id,
            "supplier_id": supplier.supplier_id,
            "name": supplier.supplier_name,
            "message": "供应商创建成功"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.put("/{supplier_id}")
def update_supplier(
    supplier_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """更新供应商"""
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    
    try:
        if "supplier_name" in data:
            supplier.supplier_name = data["supplier_name"]
        if "contact_person" in data:
            supplier.contact_person = data["contact_person"]
        if "contact_phone" in data:
            supplier.contact_phone = data["contact_phone"]
        if "contact_email" in data:
            supplier.contact_email = data["contact_email"]
        if "status" in data:
            supplier.status = data["status"]
        if "remarks" in data:
            supplier.remarks = data["remarks"]
        
        db.commit()
        
        return {"message": "供应商更新成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """删除供应商"""
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    
    evaluation_count = db.query(SupplierEvaluation).filter(
        SupplierEvaluation.supplier_id == supplier_id
    ).count()
    
    if evaluation_count > 0:
        return {"code": 400, "message": f"该供应商存在{evaluation_count}条评价记录，无法删除。如需停用，请联系管理员禁用该供应商。"}
    
    try:
        db.delete(supplier)
        db.commit()
        return {"message": "供应商删除成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


# ==================== 供应商评价API ====================

@router.get("/{supplier_id}/evaluations")
def get_supplier_evaluations(
    supplier_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """获取供应商评价列表"""
    try:
        if supplier_id <= 0:
            return {"items": [], "total": 0}
        
        evaluations = db.query(SupplierEvaluation).filter(
            SupplierEvaluation.supplier_id == supplier_id
        ).order_by(desc(SupplierEvaluation.evaluation_id)).offset(skip).limit(limit).all()
        
        total = db.query(SupplierEvaluation).filter(
            SupplierEvaluation.supplier_id == supplier_id
        ).count()
        
        supplier_map = {s.supplier_id: s.supplier_name for s in db.query(Supplier).all()}
        
        return {
            "items": [
                {
                    "id": e.evaluation_id,
                    "evaluation_id": e.evaluation_id,
                    "supplier_id": e.supplier_id,
                    "supplier_name": supplier_map.get(e.supplier_id, ''),
                    "delivery_punctuality_score": e.delivery_punctuality_score,
                    "delivery_punctuality_evidence": e.delivery_punctuality_evidence or '',
                    "quality_consistency_score": e.quality_consistency_score,
                    "quality_consistency_evidence": e.quality_consistency_evidence or '',
                    "service_response_score": e.service_response_score,
                    "service_response_evidence": e.service_response_evidence or '',
                    "cooperation_score": e.cooperation_score,
                    "cooperation_evidence": e.cooperation_evidence or '',
                    "overall_score": float(e.overall_score) if e.overall_score else None,
                    "evaluation_date": format_date(e.evaluation_date),
                    "evaluator": e.evaluator,
                    "created_at": format_datetime(e.created_at),
                    "remarks": e.remarks
                }
                for e in evaluations
            ],
            "total": total
        }
    except Exception as e:
        return {"items": [], "total": 0, "error": str(e)}


@router.post("/{supplier_id}/evaluations")
def create_supplier_evaluation(
    supplier_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """创建供应商评价"""
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    
    try:
        delivery_score = data.get("delivery_punctuality_score", 0)
        quality_score = data.get("quality_consistency_score", 0)
        service_score = data.get("service_response_score", 0)
        cooperation_score = data.get("cooperation_score", 0)
        
        overall = (delivery_score + quality_score + service_score + cooperation_score) / 4
        
        evaluation = SupplierEvaluation(
            supplier_id=supplier_id,
            delivery_punctuality_score=delivery_score,
            quality_consistency_score=quality_score,
            service_response_score=service_score,
            cooperation_score=cooperation_score,
            overall_score=overall,
            evaluation_date=data.get("evaluation_date"),
            evaluator=data.get("evaluator"),
            remarks=data.get("remarks")
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        return {"message": "评价创建成功", "evaluation_id": evaluation.evaluation_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.put("/evaluations/{evaluation_id}")
def update_supplier_evaluation(
    evaluation_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """更新供应商评价"""
    evaluation = db.query(SupplierEvaluation).filter(
        SupplierEvaluation.evaluation_id == evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="评价记录不存在")
    
    try:
        if "delivery_punctuality_score" in data:
            evaluation.delivery_punctuality_score = data["delivery_punctuality_score"]
        if "quality_consistency_score" in data:
            evaluation.quality_consistency_score = data["quality_consistency_score"]
        if "service_response_score" in data:
            evaluation.service_response_score = data["service_response_score"]
        if "cooperation_score" in data:
            evaluation.cooperation_score = data["cooperation_score"]
        if "evaluation_date" in data:
            evaluation.evaluation_date = data["evaluation_date"]
        if "evaluator" in data:
            evaluation.evaluator = data["evaluator"]
        if "remarks" in data:
            evaluation.remarks = data["remarks"]
        
        if all([evaluation.delivery_punctuality_score, evaluation.quality_consistency_score,
                evaluation.service_response_score, evaluation.cooperation_score]):
            evaluation.overall_score = (
                evaluation.delivery_punctuality_score +
                evaluation.quality_consistency_score +
                evaluation.service_response_score +
                evaluation.cooperation_score
            ) / 4
        
        db.commit()
        
        return {"message": "评价更新成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.delete("/evaluations/{evaluation_id}")
def delete_supplier_evaluation(evaluation_id: int, db: Session = Depends(get_db)):
    """删除供应商评价"""
    evaluation = db.query(SupplierEvaluation).filter(
        SupplierEvaluation.evaluation_id == evaluation_id
    ).first()
    
    if not evaluation:
        raise HTTPException(status_code=404, detail="评价记录不存在")
    
    try:
        db.delete(evaluation)
        db.commit()
        return {"message": "评价删除成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


# ==================== 供应商排名API ====================

@router.get("/performance/ranking")
def get_supplier_ranking(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """获取供应商排名"""
    try:
        rankings = db.query(SupplierRanking).order_by(
            SupplierRanking.total_score.desc()
        ).limit(limit).all()
        
        return [
            {
                "supplier_id": r.supplier_id,
                "supplier_name": r.supplier_name,
                "total_score": float(r.total_score) if r.total_score else 0,
                "suggested_level": r.suggested_level,
                "ranking_date": format_date(r.ranking_date)
            }
            for r in rankings
        ]
    except Exception as e:
        return []


# ==================== 供应商履约分析API ====================

@router.get("/analysis/overview")
def get_supplier_analysis_overview(db: Session = Depends(get_db)):
    """获取供应商履约分析概览"""
    try:
        supplier_count = db.query(Supplier).count()
        
        evaluation_count = db.query(SupplierEvaluation).count()
        
        avg_delivery = db.query(func.avg(SupplierEvaluation.delivery_punctuality_score)).filter(
            SupplierEvaluation.delivery_punctuality_score.isnot(None)
        ).scalar() or 0
        
        avg_quality = db.query(func.avg(SupplierEvaluation.quality_consistency_score)).filter(
            SupplierEvaluation.quality_consistency_score.isnot(None)
        ).scalar() or 0
        
        avg_service = db.query(func.avg(SupplierEvaluation.service_response_score)).filter(
            SupplierEvaluation.service_response_score.isnot(None)
        ).scalar() or 0
        
        avg_cooperation = db.query(func.avg(SupplierEvaluation.cooperation_score)).filter(
            SupplierEvaluation.cooperation_score.isnot(None)
        ).scalar() or 0
        
        avg_overall = db.query(func.avg(SupplierRanking.total_score)).filter(
            SupplierRanking.total_score.isnot(None)
        ).scalar() or 0
        
        ranking_count = db.query(SupplierRanking).count()
        
        return {
            "code": 200,
            "data": {
                "supplier_count": supplier_count,
                "evaluation_count": evaluation_count,
                "ranking_count": ranking_count,
                "average_scores": {
                    "delivery_punctuality": round(float(avg_delivery), 2),
                    "quality_consistency": round(float(avg_quality), 2),
                    "service_response": round(float(avg_service), 2),
                    "cooperation": round(float(avg_cooperation), 2),
                    "overall": round(float(avg_overall), 2)
                }
            },
            "message": "获取分析概览成功"
        }
    except Exception as e:
        return {"code": 500, "data": None, "message": f"获取分析概览失败: {str(e)}"}


@router.get("/analysis/trend")
def get_supplier_analysis_trend(
    period: str = Query("month", description="时间周期: month-按月, quarter-按季度"),
    db: Session = Depends(get_db)
):
    """获取供应商履约趋势分析"""
    try:
        evaluations = db.query(SupplierEvaluation).filter(
            SupplierEvaluation.evaluation_date.isnot(None)
        ).all()
        
        trend_data = {}
        for eval in evaluations:
            if not eval.evaluation_date:
                continue
            
            if period == "month":
                key = f"{eval.evaluation_date.year}-{eval.evaluation_date.month:02d}"
            elif period == "quarter":
                quarter = (eval.evaluation_date.month - 1) // 3 + 1
                key = f"{eval.evaluation_date.year}-Q{quarter}"
            else:
                key = str(eval.evaluation_date.year)
            
            if key not in trend_data:
                trend_data[key] = {
                    "period": key,
                    "delivery_sum": 0,
                    "quality_sum": 0,
                    "service_sum": 0,
                    "cooperation_sum": 0,
                    "overall_sum": 0,
                    "count": 0
                }
            
            trend_data[key]["delivery_sum"] += eval.delivery_punctuality_score or 0
            trend_data[key]["quality_sum"] += eval.quality_consistency_score or 0
            trend_data[key]["service_sum"] += eval.service_response_score or 0
            trend_data[key]["cooperation_sum"] += eval.cooperation_score or 0
            trend_data[key]["overall_sum"] += float(eval.overall_score) or 0
            trend_data[key]["count"] += 1
        
        trends = []
        for key, data in sorted(trend_data.items()):
            count = data["count"]
            if count > 0:
                trends.append({
                    "period": key,
                    "delivery_avg": round(data["delivery_sum"] / count, 2),
                    "quality_avg": round(data["quality_sum"] / count, 2),
                    "service_avg": round(data["service_sum"] / count, 2),
                    "cooperation_avg": round(data["cooperation_sum"] / count, 2),
                    "overall_avg": round(data["overall_sum"] / count, 2)
                })
        
        return {
            "code": 200,
            "data": {
                "period": period,
                "trends": trends
            },
            "message": "获取趋势分析成功"
        }
    except Exception as e:
        return {"code": 500, "data": None, "message": f"获取趋势分析失败: {str(e)}"}


@router.get("/analysis/chart-data")
def get_supplier_analysis_chart_data(db: Session = Depends(get_db)):
    """获取供应商履约图表数据"""
    try:
        suppliers = db.query(Supplier).all()
        
        supplier_data = []
        for supplier in suppliers:
            evaluations = db.query(SupplierEvaluation).filter(
                SupplierEvaluation.supplier_id == supplier.supplier_id
            ).all()
            
            if evaluations:
                avg_delivery = sum(e.delivery_punctuality_score or 0 for e in evaluations) / len(evaluations)
                avg_quality = sum(e.quality_consistency_score or 0 for e in evaluations) / len(evaluations)
                avg_service = sum(e.service_response_score or 0 for e in evaluations) / len(evaluations)
                avg_cooperation = sum(e.cooperation_score or 0 for e in evaluations) / len(evaluations)
                avg_overall = sum(float(e.overall_score or 0) for e in evaluations) / len(evaluations)
                
                supplier_data.append({
                    "id": supplier.supplier_id,
                    "name": supplier.supplier_name,
                    "delivery_avg": round(avg_delivery, 2),
                    "quality_avg": round(avg_quality, 2),
                    "service_avg": round(avg_service, 2),
                    "cooperation_avg": round(avg_cooperation, 2),
                    "overall_avg": round(avg_overall, 2),
                    "record_count": len(evaluations)
                })
        
        ranking_data = sorted(supplier_data, key=lambda x: x["overall_avg"], reverse=True)
        
        pie_data = [
            {"value": round(s["overall_avg"], 2), "name": s["name"][:10]}
            for s in ranking_data[:10]
        ]
        
        bar_categories = [s["name"][:8] for s in ranking_data[:10]]
        bar_delivery = [s["delivery_avg"] for s in ranking_data[:10]]
        bar_quality = [s["quality_avg"] for s in ranking_data[:10]]
        bar_service = [s["service_avg"] for s in ranking_data[:10]]
        bar_cooperation = [s["cooperation_avg"] for s in ranking_data[:10]]
        
        return {
            "code": 200,
            "data": {
                "supplier_details": supplier_data,
                "ranking": ranking_data,
                "pie_chart": pie_data,
                "bar_chart": {
                    "categories": bar_categories,
                    "delivery": bar_delivery,
                    "quality": bar_quality,
                    "service": bar_service,
                    "cooperation": bar_cooperation
                }
            },
            "message": "获取图表数据成功"
        }
    except Exception as e:
        return {"code": 500, "data": None, "message": f"获取图表数据失败: {str(e)}"}


@router.get("/analysis/comparison")
def get_supplier_analysis_comparison(
    supplier_ids: str = Query(..., description="供应商ID列表，用逗号分隔"),
    db: Session = Depends(get_db)
):
    """获取多供应商对比分析"""
    try:
        ids = [int(x.strip()) for x in supplier_ids.split(",")]
        
        comparison_data = []
        for sid in ids:
            supplier = db.query(Supplier).filter(
                Supplier.supplier_id == sid
            ).first()
            
            if not supplier:
                continue
            
            evaluations = db.query(SupplierEvaluation).filter(
                SupplierEvaluation.supplier_id == sid
            ).all()
            
            if evaluations:
                comparison_data.append({
                    "supplier_id": supplier.supplier_id,
                    "supplier_name": supplier.supplier_name,
                    "delivery_avg": round(sum(e.delivery_punctuality_score or 0 for e in evaluations) / len(evaluations), 2),
                    "quality_avg": round(sum(e.quality_consistency_score or 0 for e in evaluations) / len(evaluations), 2),
                    "service_avg": round(sum(e.service_response_score or 0 for e in evaluations) / len(evaluations), 2),
                    "cooperation_avg": round(sum(e.cooperation_score or 0 for e in evaluations) / len(evaluations), 2),
                    "overall_avg": round(sum(float(e.overall_score or 0) for e in evaluations) / len(evaluations), 2),
                    "record_count": len(evaluations)
                })
        
        return {
            "code": 200,
            "data": {
                "suppliers": comparison_data,
                "comparison": {
                    "by_delivery": sorted(comparison_data, key=lambda x: x["delivery_avg"], reverse=True),
                    "by_quality": sorted(comparison_data, key=lambda x: x["quality_avg"], reverse=True),
                    "by_service": sorted(comparison_data, key=lambda x: x["service_avg"], reverse=True),
                    "by_cooperation": sorted(comparison_data, key=lambda x: x["cooperation_avg"], reverse=True),
                    "by_overall": sorted(comparison_data, key=lambda x: x["overall_avg"], reverse=True)
                }
            },
            "message": "获取对比分析成功"
        }
    except Exception as e:
        return {"code": 500, "data": None, "message": f"获取对比分析失败: {str(e)}"}


@router.get("/analysis/ai-result")
def get_latest_ai_analysis(db: Session = Depends(get_db)):
    """获取最新AI分析结果"""
    try:
        ai_analysis = db.query(SupplierAIAnalysis).order_by(
            SupplierAIAnalysis.analysis_id.desc()
        ).first()
        
        if not ai_analysis:
            return {
                "code": 404,
                "data": None,
                "message": "暂无AI分析结果"
            }
        
        result_data = {
            "supplier_id": ai_analysis.supplier_id,
            "supplier_name": "",
            "analysis_date": format_datetime(ai_analysis.created_at),
            "analysis_result": ai_analysis.analysis_result,
            "generated_at": format_datetime(ai_analysis.created_at),
            "generated_by": ai_analysis.generated_by
        }
        print(f"返回AI分析数据: code=200, analysis_result长度={len(ai_analysis.analysis_result)}")
        
        return {
            "code": 200,
            "data": result_data,
            "message": "获取AI分析结果成功"
        }
    except Exception as e:
        return {"code": 500, "data": None, "message": f"获取AI分析结果失败: {str(e)}"}


@router.get("/analysis/ai-result/{supplier_id}")
def get_supplier_ai_analysis(supplier_id: int, db: Session = Depends(get_db)):
    """获取供应商AI分析结果"""
    try:
        if supplier_id <= 0:
            return {
                "code": 404,
                "data": None,
                "message": "供应商不存在"
            }
        
        ai_analysis = db.query(SupplierAIAnalysis).filter(
            SupplierAIAnalysis.supplier_id == supplier_id
        ).order_by(SupplierAIAnalysis.analysis_id.desc()).first()
        
        if not ai_analysis:
            return {
                "code": 404,
                "data": None,
                "message": "暂无AI分析结果"
            }
        
        supplier_name = ""
        supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
        if supplier:
            supplier_name = supplier.supplier_name
        
        return {
            "code": 200,
            "data": {
                "supplier_id": supplier_id,
                "supplier_name": supplier_name,
                "analysis_date": format_date(ai_analysis.analysis_date),
                "analysis_result": ai_analysis.analysis_result,
                "generated_at": format_datetime(ai_analysis.generated_at),
                "generated_by": ai_analysis.generated_by
            },
            "message": "获取AI分析结果成功"
        }
    except Exception as e:
        return {"code": 500, "data": None, "message": f"获取AI分析结果失败: {str(e)}"}


@router.get("/analysis/ranking-detail")
def get_supplier_ranking_detail(db: Session = Depends(get_db)):
    """获取供应商排名详情（含合作建议）- 每个供应商只取最新排名"""
    try:
        rankings = db.query(SupplierRanking).order_by(
            SupplierRanking.ranking_id.desc()
        ).all()
        
        latest_rankings = {}
        for r in rankings:
            if r.supplier_id not in latest_rankings:
                latest_rankings[r.supplier_id] = r
        
        sorted_rankings = sorted(latest_rankings.values(), key=lambda x: (x.total_score or 0), reverse=True)
        
        result = []
        for idx, r in enumerate(sorted_rankings, 1):
            result.append({
                "rank": idx,
                "supplier_id": r.supplier_id,
                "supplier_name": r.supplier_name,
                "total_score": float(r.total_score) if r.total_score else 0,
                "suggested_level": r.suggested_level,
                "ranking_date": format_date(r.ranking_date),
                "created_at": format_datetime(r.created_at),
                "remarks": r.remarks
            })
        
        return {
            "code": 200,
            "data": result,
            "message": "获取排名详情成功"
        }
    except Exception as e:
        return {"code": 500, "data": [], "message": f"获取排名详情失败: {str(e)}"}


@router.post("/analysis/ai-generate")
def generate_ai_analysis(db: Session = Depends(get_db)):
    """触发AI分析生成"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("开始AI分析...")
        suppliers = db.query(Supplier).filter(Supplier.status == 1).all()
        logger.info(f"找到 {len(suppliers)} 个启用的供应商")
        
        if not suppliers:
            return {"code": 400, "data": None, "message": "没有可分析的供应商"}
        
        suppliers_data = []
        for supplier in suppliers:
            latest_eval = db.query(SupplierEvaluation).filter(
                SupplierEvaluation.supplier_id == supplier.supplier_id
            ).order_by(desc(SupplierEvaluation.evaluation_id)).first()
            
            delivery_score = latest_eval.delivery_punctuality_score if latest_eval else 0
            quality_score = latest_eval.quality_consistency_score if latest_eval else 0
            service_score = latest_eval.service_response_score if latest_eval else 0
            cooperation_score = latest_eval.cooperation_score if latest_eval else 0
            
            avg_delivery = delivery_score
            avg_quality = quality_score
            avg_service = service_score
            avg_cooperation = cooperation_score
            
            overall_score = (avg_delivery + avg_quality + avg_service + avg_cooperation) / 4 if (avg_delivery or avg_quality or avg_service or avg_cooperation) else 0
            
            level = "D"
            if overall_score >= 9 and min(avg_delivery, avg_quality, avg_service, avg_cooperation) >= 8.5:
                level = "A"
            elif overall_score >= 8 and min(avg_delivery, avg_quality, avg_service, avg_cooperation) >= 7.5:
                level = "B"
            elif overall_score >= 7 and min(avg_delivery, avg_quality, avg_service, avg_cooperation) >= 6.5:
                level = "C"
            
            evidence = f"最新评价日期: {latest_eval.evaluation_date}" if latest_eval else "暂无评价"
            
            suppliers_data.append({
                "name": supplier.supplier_name,
                "evaluation_data": {
                    "delivery_punctuality_rate": {"score": round(avg_delivery, 1), "evidence": evidence},
                    "service_response_efficiency": {"score": round(avg_service, 1), "evidence": evidence},
                    "quality_consistency": {"score": round(avg_quality, 1), "evidence": evidence},
                    "cooperation_attitude": {"score": round(avg_cooperation, 1), "evidence": evidence}
                }
            })
            logger.info(f"供应商 {supplier.supplier_name}: 交付={avg_delivery:.1f}, 质量={avg_quality:.1f}, 服务={avg_service:.1f}, 合作={avg_cooperation:.1f}")
        
        import requests
        import json
        from datetime import datetime
        
        DEEPSEEK_API_KEY = "sk-8d9cab2969fa432da8a919e6fdf6fe63"
        DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
        
        supplier_ranking_list_json = '''{
            "supplier_ranking_list": [
                {
                    "ranking": 1,
                    "supplier_name": "供应商名称",
                    "comprehensive_score": 9.5,
                    "suggestion_level": "A: 战略合作",
                    "dimension_scores": {
                        "delivery_punctuality_rate": 9,
                        "service_response_efficiency": 8,
                        "quality_consistency": 6,
                        "cooperation_attitude": 5
                    }
                }
            ]
        }'''
        
        prompt = f"""
        你是一个专业的供应商履约分析专家，请基于以下供应商数据进行深度分析：
        ## 供应商履约数据概览：
        {json.dumps(suppliers_data, ensure_ascii=False, indent=2)}

        ## 请从以下维度进行专业分析：
        1. **交付准时率**：评估订单按时完成情况、延迟频率及通知主动性。
        2. **服务响应效率**：评估沟通响应速度、问题解决效率和技术支持能力。
        3. **质量一致性**：评估产品/服务合格率、质量稳定性与标准符合度。
        4. **合作配合度**：评估沟通协作态度、处理异常积极性和价值创造主动性。
        5. **供应商评价等级**：根据综合评分和等级划分，为供应商分配评价等级。综合评分：四个维度得分的算术平均值,每个维度总分10分
            等级划分：A（战略合作）：≥9分，且无维度低于8.5分；B（优先合作）：≥8分，且无维度低于7.5分；
            C（合格待改善）：≥7分，且无维度低于6.5分；D（高风险）：<7分，或任一维度低于6.5分

        # 输出要求
        ## 第一部分：详细分析报告
        请按以下结构生成详细报告：
        1. 对每个维度都要给出具体的评分和分析结论
        2. 识别供应商的优势领域和改进空间
        3. 提供可操作的改进建议和风险预警
        4. 对未来合作策略提出专业建议
        5. 输出结构化、专业的分析报告
        6. 在报告最后，用单独一行「===JSON_DATA===」作为分隔符

        ## 第二部分：结构化JSON数据。在报告结束后，必须输出一个格式完好的JSON对象，包含供应商排名表。
        **JSON结构必须严格遵循：**
        {supplier_ranking_list_json}
        请用专业、结构化的方式呈现分析结果，重点突出供应商履约的关键洞察和actionable建议。
        """
        
        logger.info("调用DeepSeek API...")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个专业的项目管理与成本分析专家，擅长从数据中发现问题并提供可行的改进建议。"},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=300)
        
        logger.info(f"DeepSeek API响应状态: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"DeepSeek API错误: {response.text}")
            return {"code": 500, "data": None, "message": f"AI调用失败: {response.status_code}"}
        
        result = response.json()
        ai_content = result['choices'][0]['message']['content']
        
        if '===JSON_DATA===' in ai_content:
            analysis_part, json_part = ai_content.split('===JSON_DATA===', 1)
            analysis_result = analysis_part.strip()
        else:
            analysis_result = ai_content
        
        logger.info(f"AI分析结果长度: {len(analysis_result)}")
        
        ai_analysis = SupplierAIAnalysis(
            supplier_id=None,
            analysis_date=datetime.now().date(),
            analysis_result=analysis_result,
            generated_at=datetime.now(),
            generated_by='AI系统',
            status=1
        )
        db.add(ai_analysis)
        db.commit()
        db.refresh(ai_analysis)
        
        logger.info(f"AI分析记录已保存: analysis_id={ai_analysis.analysis_id}")
        
        return {
            "code": 200,
            "data": {
                "analysis_id": ai_analysis.analysis_id,
                "analysis_result": analysis_result
            },
            "message": "AI分析生成成功"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"AI分析异常: {str(e)}")
        db.rollback()
        return {"code": 500, "data": None, "message": f"AI分析失败: {str(e)}"}
