"""
AI日报助手模块
提供日报生成、摘要、评价建议等功能
"""

import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from openai import OpenAI

from app.models.daily_report import DailyReport
from app.models.resource import Personnel


class AIDailyReportAssistant:
    """AI日报助手"""
    
    def __init__(self):
        """初始化AI客户端"""
        # 优先使用 DeepSeek API (与其他模块保持一致)
        api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("MOONSHOT_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            # 如果没有配置API key，设置为None，后续功能会 gracefully 降级
            self.client = None
            self.model = None
        else:
            # 使用 DeepSeek API
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1"
            )
            self.model = "deepseek-chat"
    
    def generate_daily_report(
        self,
        user_name: str,
        projects: List[str],
        tasks: List[Dict],
        notes: Optional[str] = None
    ) -> Dict:
        """
        根据工作事项生成日报
        
        Args:
            user_name: 用户姓名
            projects: 参与的项目列表
            tasks: 任务列表 [{"name": "任务名", "status": "状态", "progress": 进度}]
            notes: 额外备注
            
        Returns:
            生成的日报内容
        """
        # 检查AI客户端是否可用
        if not self.client:
            return {
                "success": False,
                "error": "AI功能未配置，请先配置DEEPSEEK_API_KEY环境变量",
                "content": None
            }
        
        # 构建提示词
        prompt = self._build_generate_prompt(user_name, projects, tasks, notes)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的工作日报生成助手。根据提供的工作事项，生成一份专业、简洁、有条理的日报。日报应包含：工作目标、工作进展、具体事项、明日计划。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # 解析生成的内容
            return {
                "success": True,
                "content": content,
                "work_goals": self._extract_section(content, "工作目标"),
                "key_progress": self._extract_section(content, "工作进展"),
                "work_items": self._extract_section(content, "具体事项"),
                "tomorrow_plan": self._extract_section(content, "明日计划")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    def summarize_daily_report(self, report_content: str) -> Dict:
        """
        生成日报摘要
        
        Args:
            report_content: 日报内容
            
        Returns:
            摘要信息
        """
        # 检查AI客户端是否可用
        if not self.client:
            return {
                "success": False,
                "error": "AI功能未配置，请先配置DEEPSEEK_API_KEY环境变量"
            }
        
        prompt = f"""请对以下日报内容进行摘要，提取关键信息：

{report_content}

请以JSON格式返回：
{{
    "summary": "一句话摘要",
    "key_points": ["要点1", "要点2", "要点3"],
    "workload": "工作量评估（低/中/高）",
    "completion_rate": "完成度评估（百分比）",
    "risk_items": ["风险项1", "风险项2"]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个工作日报分析专家。请分析日报内容，提取关键信息并给出专业评估。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # 尝试解析JSON
            import json
            try:
                result = json.loads(content)
                result["success"] = True
                return result
            except:
                return {
                    "success": True,
                    "summary": content[:200],
                    "key_points": [],
                    "workload": "未知",
                    "completion_rate": "未知",
                    "risk_items": []
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_evaluation_suggestions(
        self,
        report_content: str,
        user_role: str,
        department: str
    ) -> Dict:
        """
        生成评价建议
        
        Args:
            report_content: 日报内容
            user_role: 用户角色/职位
            department: 部门
            
        Returns:
            评价建议
        """
        # 检查AI客户端是否可用
        if not self.client:
            return {
                "success": False,
                "error": "AI功能未配置，请先配置DEEPSEEK_API_KEY环境变量"
            }
        
        prompt = f"""请根据以下日报内容，为上级提供评价建议：

员工信息：
- 职位：{user_role}
- 部门：{department}

日报内容：
{report_content}

请提供：
1. 评价等级建议（A/B/C/D）及理由
2. 工作亮点
3. 改进建议
4. 具体评语（可直接使用）
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位资深的团队管理者和绩效评估专家。请根据日报内容，提供专业、客观、有建设性的评价建议。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            return {
                "success": True,
                "suggestions": content,
                "rating": self._extract_rating(content),
                "highlights": self._extract_highlights(content),
                "improvements": self._extract_improvements(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_workload_trend(
        self,
        reports: List[DailyReport],
        days: int = 7
    ) -> Dict:
        """
        分析工作量趋势
        
        Args:
            reports: 日报列表
            days: 分析天数
            
        Returns:
            趋势分析结果
        """
        # 检查AI客户端是否可用
        if not self.client:
            return {
                "success": False,
                "error": "AI功能未配置，请先配置DEEPSEEK_API_KEY环境变量"
            }
        
        if not reports:
            return {
                "success": False,
                "error": "没有足够的日报数据"
            }
        
        # 统计信息
        total_reports = len(reports)
        total_tasks = sum(len(report.work_items) for report in reports)
        avg_tasks_per_day = total_tasks / total_reports if total_reports > 0 else 0
        
        # 构建分析提示
        report_summaries = []
        for report in reports[:days]:
            summary = f"日期：{report.report_date}\n"
            summary += f"工作事项数：{len(report.work_items)}\n"
            summary += f"自我评价：{report.self_evaluation}\n"
            report_summaries.append(summary)
        
        prompt = f"""请分析以下工作日报数据，给出工作量趋势分析：

统计信息：
- 分析天数：{days}天
- 日报总数：{total_reports}
- 总任务数：{total_tasks}
- 日均任务数：{avg_tasks_per_day:.1f}

日报详情：
{chr(10).join(report_summaries)}

请提供：
1. 工作量趋势（上升/下降/平稳）
2. 工作效率评估
3. 可能存在的问题
4. 改进建议
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是数据分析专家。请分析工作日报数据，识别趋势和模式，提供有价值的洞察。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=1500
            )
            
            return {
                "success": True,
                "analysis": response.choices[0].message.content,
                "statistics": {
                    "total_reports": total_reports,
                    "total_tasks": total_tasks,
                    "avg_tasks_per_day": round(avg_tasks_per_day, 2),
                    "analysis_period": days
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_generate_prompt(
        self,
        user_name: str,
        projects: List[str],
        tasks: List[Dict],
        notes: Optional[str]
    ) -> str:
        """构建生成日报的提示词"""
        prompt = f"""请为 {user_name} 生成一份工作日报：

参与项目：
{chr(10).join([f"- {p}" for p in projects])}

今日工作事项：
"""
        for i, task in enumerate(tasks, 1):
            prompt += f"\n{i}. {task['name']}"
            if 'status' in task:
                prompt += f"（状态：{task['status']}）"
            if 'progress' in task:
                prompt += f" - 进度：{task['progress']}%"
            if 'time' in task:
                prompt += f" - 用时：{task['time']}小时"
        
        if notes:
            prompt += f"\n\n备注：\n{notes}"
        
        prompt += """\n\n请生成日报，包含以下部分：
1. 工作目标
2. 关键工作进展
3. 具体工作事项（详细描述）
4. 明日工作计划
5. 自我评价（A/B/C/D）

请用专业、简洁的语言，突出重点。"""
        
        return prompt
    
    def _extract_section(self, content: str, section_name: str) -> str:
        """从内容中提取指定部分"""
        lines = content.split('\n')
        result = []
        in_section = False
        
        for line in lines:
            if section_name in line and ('：' in line or ':' in line):
                in_section = True
                continue
            
            if in_section:
                # 检查是否进入下一部分
                if line.strip() and ('：' in line or ':' in line) and len(line) < 20:
                    break
                result.append(line)
        
        return '\n'.join(result).strip()
    
    def _extract_rating(self, content: str) -> str:
        """提取评价等级"""
        if 'A' in content[:500] and '等级' in content[:500]:
            return 'A'
        elif 'B' in content[:500] and '等级' in content[:500]:
            return 'B'
        elif 'C' in content[:500] and '等级' in content[:500]:
            return 'C'
        elif 'D' in content[:500] and '等级' in content[:500]:
            return 'D'
        return '未知'
    
    def _extract_highlights(self, content: str) -> List[str]:
        """提取亮点"""
        highlights = []
        lines = content.split('\n')
        in_highlight = False
        
        for line in lines:
            if '亮点' in line or '优点' in line:
                in_highlight = True
                continue
            
            if in_highlight:
                if line.strip().startswith('-') or line.strip().startswith('•') or line.strip()[0:2] in ['1.', '2.', '3.', '4.', '5.']:
                    highlights.append(line.strip().lstrip('- •').strip())
                elif line.strip() and '建议' in line:
                    break
        
        return highlights[:5]
    
    def _extract_improvements(self, content: str) -> List[str]:
        """提取改进建议"""
        improvements = []
        lines = content.split('\n')
        in_improvement = False
        
        for line in lines:
            if '改进' in line or '建议' in line:
                in_improvement = True
                continue
            
            if in_improvement:
                if line.strip().startswith('-') or line.strip().startswith('•') or line.strip()[0:2] in ['1.', '2.', '3.', '4.', '5.']:
                    improvements.append(line.strip().lstrip('- •').strip())
                elif line.strip() and len(improvements) >= 3:
                    break
        
        return improvements[:5]


# 全局AI助手实例
ai_assistant = AIDailyReportAssistant()
