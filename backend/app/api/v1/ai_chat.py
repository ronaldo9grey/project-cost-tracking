from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import json
from datetime import datetime
from decimal import Decimal
import requests

from app.core.dependencies import get_db
from app.models.project import Project
from app.models.project_task import ProjectTask
from app.models.material_cost import MaterialCost
from app.models.labor_cost import LaborCost
from app.models.outsourcing_cost import OutsourcingCost
from app.models.indirect_cost import IndirectCost
from app.models.supplier import SupplierEvaluation

router = APIRouter()

DEEPSEEK_API_KEY = "sk-8d9cab2969fa432da8a919e6fdf6fe63"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def format_datetime(dt):
    if not dt:
        return ""
    if isinstance(dt, str):
        return dt[:19] if 'T' in dt else dt
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def _json_serial(obj):
    from datetime import datetime, date
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def format_currency(amount):
    if amount is None:
        return 0
    return round(float(amount), 2)

@router.get("/project/{projectId}/full-data")
def get_project_full_data(projectId: int, db: Session = Depends(get_db)):
    """获取项目完整数据"""
    try:
        project = db.query(Project).filter(Project.id == projectId).first()
        if not project:
            return {"code": 404, "data": None, "message": "项目不存在"}
        
        # 修复数据库类型不匹配问题：将整数转换为字符串
        project_id_str = str(projectId)
        
        tasks = db.query(ProjectTask).filter(
            ProjectTask.project_id == project_id_str,
            ProjectTask.status != 'deleted'
        ).all()
        
        material_costs = db.query(MaterialCost).filter(
            MaterialCost.project_id == project_id_str
        ).all()
        
        labor_costs = db.query(LaborCost).filter(
            LaborCost.project_id == project_id_str
        ).all()
        
        outsourcing_costs = db.query(OutsourcingCost).filter(
            OutsourcingCost.project_id == project_id_str
        ).all()
        
        indirect_costs = db.query(IndirectCost).filter(
            IndirectCost.project_id == project_id_str
        ).all()
        
        task_data = []
        for task in tasks:
            task_data.append({
                "id": task.task_id,
                "name": task.task_name,
                "description": getattr(task, 'description', ''),
                "start_date": format_datetime(task.start_date),
                "end_date": format_datetime(task.end_date),
                "actual_end_date": format_datetime(task.actual_end_date) if task.actual_end_date else None,
                "status": task.status,
                "progress": task.progress,
                "assigned_to": task.assignee
            })
        
        material_data = []
        for cost in material_costs:
            material_data.append({
                "id": cost.cost_id,
                "name": cost.name,
                "specification": cost.specification,
                "unit": cost.unit,
                "unit_price": format_currency(cost.unit_price),
                "quantity": format_currency(cost.quantity),
                "total_price": format_currency(cost.total_price),
                "cost_type": cost.cost_type,
                "remark": cost.remark,
                "create_time": format_datetime(cost.create_time)
            })
        
        labor_data = []
        for cost in labor_costs:
            labor_data.append({
                "id": cost.cost_id,
                "employee_id": cost.employee_id,
                "year_month": cost.year_month,
                "budget_hours": format_currency(cost.budget_hours),
                "actual_hours": format_currency(cost.actual_hours),
                "hourly_rate": format_currency(cost.hourly_rate),
                "budget_cost": format_currency(cost.budget_cost),
                "actual_cost": format_currency(cost.actual_cost),
                "remark": cost.remark,
                "task_id": cost.task_id
            })
        
        outsourcing_data = []
        for cost in outsourcing_costs:
            outsourcing_data.append({
                "id": cost.cost_id,
                "service_type": cost.service_type,
                "description": cost.description,
                "quantity": format_currency(cost.quantity),
                "unit_price": format_currency(cost.unit_price),
                "total_price": format_currency(cost.total_price),
                "cost_type": cost.cost_type,
                "remark": cost.remark,
                "service_type_id": cost.service_type_id
            })
        
        indirect_data = []
        for cost in indirect_costs:
            indirect_data.append({
                "id": cost.cost_id,
                "cost_type": cost.cost_type,
                "amount": format_currency(cost.amount),
                "description": cost.description,
                "cost_type_flag": cost.cost_type_flag,
                "remark": cost.remark,
                "create_time": format_datetime(cost.create_time)
            })
        
        project_data = {
            "id": project.id,
            "name": project.name,
            "describe": project.describe,
            "start_date": format_datetime(project.start_date),
            "end_date": format_datetime(project['计划结束日期']) if isinstance(project, dict) else format_datetime(getattr(project, '计划结束日期', None)),
            "actual_end_date": format_datetime(project['实际结束日期']) if isinstance(project, dict) and project.get('实际结束日期') else None,
            "budget_total_cost": format_currency(project.budget_total_cost),
            "actual_total_cost": format_currency(project.actual_total_cost),
            "contract_amount": format_currency(project.contract_amount),
            "status": project.status,
            "progress": project.progress,
            "leader": project.leader,
            "created_at": format_datetime(project.created_at),
            "updated_at": format_datetime(project.updated_at)
        }
        
        result = {
            "project": project_data,
            "tasks": task_data,
            "material_costs": material_data,
            "labor_costs": labor_data,
            "outsourcing_costs": outsourcing_data,
            "indirect_costs": indirect_data
        }
        
        return {
            "code": 200,
            "data": result,
            "message": "获取成功"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"code": 500, "data": None, "message": f"获取数据失败: {str(e)}"}

@router.post("/chat")
def chat_with_ai(request: dict):
    """AI智能对话"""
    try:
        project_context = request.get('project_context', {})
        user_question = request.get('user_question', '')
        
        project_context_json = json.dumps(project_context, default=_json_serial, ensure_ascii=False)
        
        prompt = f"""
你是一位资深业务数据分析师，擅长从多维度数据中提取业务洞察和趋势规律。请直接基于提供的数据进行深度分析，输出具体的分析结论和业务洞察。

## 项目上下文信息：
{project_context_json}

## 用户问题：
{user_question}

## 回答要求：
1. 基于提供的项目上下文信息回答问题
2. 宏观视角，关注整体业务表现
3. 业务导向，连接数据与业务价值
4. 回答应当专业、准确、有条理
5. 如果信息不足，请明确指出并提供基于已有信息的建议
6. 前瞻性，预测未来趋势
7. 语言风格应当友好、自然，适合聊天交流
8. 使用中文回答

请直接回答用户问题，不需要使用"尊敬的用户"等开场白。
"""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位资深业务数据分析师，擅长从项目数据中发现问题并提供可行的改进建议。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=120)
        
        if response.status_code != 200:
            return {"message": f"AI服务暂时不可用，请稍后再试。"}
        
        result = response.json()
        ai_content = result['choices'][0]['message']['content']
        
        return ai_content
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"message": f"分析过程中出现错误: {str(e)}"}
