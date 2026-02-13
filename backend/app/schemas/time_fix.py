"""
时间格式修复模块
"""
from typing import Any, Dict, List
from datetime import time

def convert_time_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """转换时间字段格式"""
    if not data:
        return data
    
    result = data.copy()
    
    # 处理可能存在的时间字段
    time_fields = ['start_time', 'end_time']
    
    for field in time_fields:
        if field in result and result[field] is not None:
            value = result[field]
            
            # 处理datetime.time对象
            if isinstance(value, time):
                result[field] = value.strftime('%H:%M')
            # 处理字符串或其他类型
            elif isinstance(value, str):
                result[field] = value
            else:
                result[field] = str(value)
    
    return result

def convert_work_items(work_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """转换工作事项列表中的时间字段"""
    if not work_items:
        return work_items
    
    return [convert_time_fields(item) for item in work_items]

def convert_daily_report_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """转换日报响应数据"""
    if not response_data:
        return response_data
    
    result = response_data.copy()
    
    # 如果有items，转换每个item
    if 'items' in result and result['items']:
        result['items'] = [convert_item(item) for item in result['items']]
    
    return result

def convert_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """转换单个日报项目"""
    if not item:
        return item
    
    result = item.copy()
    
    # 转换主表的时间字段（如果有的话）
    result = convert_time_fields(result)
    
    # 转换工作事项
    if 'work_items' in result and result['work_items']:
        result['work_items'] = convert_work_items(result['work_items'])
    
    return result