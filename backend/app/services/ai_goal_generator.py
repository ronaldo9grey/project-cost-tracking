"""
AI目标生成服务
基于项目管理和实施方法论生成高质量目标
"""
import json
import httpx
from typing import List, Dict, Optional
from datetime import date
from app.core.config import settings


async def generate_goals_with_ai(
    user_name: str,
    month: str,
    projects: List[Dict],
    tasks: List[Dict],
    week_ranges: List[Dict]
) -> Dict:
    """
    使用AI生成高质量的目标内容
    
    基于SMART原则和项目管理方法论
    """
    
    # 构建项目信息
    projects_info = "\n".join([
        f"- 项目：{p['name']}，负责人：{p.get('leader', '未知')}"
        for p in projects
    ])
    
    # 构建任务信息
    tasks_info = "\n".join([
        f"- {t['task_name']}（所属项目：{t.get('project_name', '未知')}，"
        f"开始：{t.get('start_date', '未知')}，结束：{t.get('end_date', '未知')}）"
        for t in tasks[:10]  # 限制任务数量避免token超限
    ])
    
    # 构建提示词
    prompt = f"""你是一位资深项目管理专家，精通OKR、SMART原则和敏捷开发方法论。

请为以下用户生成本月的工作目标：

## 用户信息
- 姓名：{user_name}
- 目标月份：{month}

## 负责的项目
{projects_info}

## 负责的任务清单
{tasks_info}

## 四周时间范围
"""
    
    for i, wr in enumerate(week_ranges, 1):
        prompt += f"- 第{i}周：{wr['start_date']} 至 {wr['end_date']}\n"
    
    prompt += f"""
## 要求

请生成以下内容（JSON格式）：

1. **月度结果目标**（1个）：基于SMART原则，概括本月要达成的核心成果
   - 必须具体、可衡量、有时限
   - 与项目和任务强相关
   - 体现专业项目管理思维

2. **月度具体内容**：描述实现目标的关键行动、里程碑和交付物

3. **四周目标拆解**（4个周目标）：
   - 每周都要有明确的结果目标
   - 每周目标要支撑月度目标的达成
   - 按时间顺序递进，体现项目推进逻辑
   - 包含具体交付物和验收标准

请按以下JSON格式返回：
{{
    "monthly_goal": {{
        "title": "月度结果目标标题（20字以内）",
        "description": "月度具体内容（100-200字）"
    }},
    "weekly_goals": [
        {{
            "week_number": 1,
            "title": "第1周结果目标（简洁明了）",
            "description": "第1周具体内容"
        }},
        ...
    ]
}}

要求：
- 目标要专业、有高度，体现项目管理思维
- 避免简单罗列任务，要提炼成果导向
- 语言简洁有力，符合职场表达习惯
- 必须是JSON格式，不要其他说明文字
"""

    # 调用DeepSeek API
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "你是一位专业的项目管理顾问，擅长制定OKR目标和项目规划。"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )
            
            if response.status_code != 200:
                print(f"AI API调用失败: {response.status_code} - {response.text}")
                return None
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # 提取JSON内容
            try:
                # 尝试直接解析
                goals_data = json.loads(content)
                return goals_data
            except json.JSONDecodeError:
                # 尝试从markdown代码块中提取
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    goals_data = json.loads(json_match.group(1))
                    return goals_data
                
                # 尝试直接找JSON对象
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    goals_data = json.loads(json_match.group())
                    return goals_data
                
                print(f"无法解析AI返回内容: {content}")
                return None
                
    except Exception as e:
        print(f"AI调用异常: {e}")
        return None


def generate_goals_fallback(
    month: str,
    projects: List[str],
    tasks: List[str]
) -> Dict:
    """
    AI生成失败时的备用方案
    """
    project_names = ", ".join(projects[:3]) if projects else "相关工作"
    task_summary = tasks[0] if tasks else "项目任务"
    
    return {
        "monthly_goal": {
            "title": f"高质量完成{project_names}相关交付",
            "description": f"本月重点推进{project_names}项目，完成{task_summary}等核心任务，确保项目按计划交付，达成预期质量标准。"
        },
        "weekly_goals": [
            {
                "week_number": 1,
                "title": "完成需求分析与方案设计",
                "description": "梳理本周任务需求，制定详细执行方案，完成前期准备工作。"
            },
            {
                "week_number": 2,
                "title": "推进核心任务开发/执行",
                "description": "按照计划推进主要工作任务，完成阶段性产出。"
            },
            {
                "week_number": 3,
                "title": "完成关键交付物",
                "description": "完成核心交付物，进行内部评审和质量检查。"
            },
            {
                "week_number": 4,
                "title": "项目收尾与复盘",
                "description": "完成剩余工作，整理项目文档，进行月度复盘。"
            }
        ]
    }
