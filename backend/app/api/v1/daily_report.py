from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import os
import urllib.parse
from app.core.dependencies import get_db
from app.api.v1.auth import get_current_user
from app.models.daily_report import DailyReport
from app.models.daily_report_attachment import DailyReportAttachment
from app.models.resource import Personnel
from app.schemas.daily_report_attachment import DailyReportAttachment as DailyReportAttachmentSchema
from app.crud.daily_report import (
    get_daily_reports,
    get_daily_report,
    create_daily_report,
    create_daily_report_with_items,
    update_daily_report,
    submit_daily_report,
    evaluate_daily_report,
    delete_daily_report,
    get_my_tasks,
    get_daily_work_logs,
    create_daily_work_log,
    get_pending_reports,
    create_goal_linked_daily_report,
    update_weekly_goal_progress_from_report
)
from app.crud.daily_report_attachment import (
    get_attachments_by_report_id,
    get_attachment_by_id,
    create_attachment,
    delete_attachment
)
from app.schemas.daily_report import (
    DailyReportCreate,
    DailyReportUpdate,
    DailyReportResponse,
    DailyReportListResponse,
    DailyReportListResponseOptimized,
    DailyReportEvaluate,
    DailyReportWithItemsCreate,
    DailyWorkItemResponse,
    DailyWorkLogCreate,
    DailyWorkLogResponse,
    MyTaskResponse,
    GoalLinkedDailyReportCreate,
    CurrentWeekGoalResponse
)

router = APIRouter()


@router.get("/my-tasks", response_model=List[MyTaskResponse], summary="获取我的任务")
def read_my_tasks(
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user),
    status: Optional[str] = Query(None, description="任务状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索")
):
    tasks = get_my_tasks(
        db,
        employee_id=current_user.employee_id,  # 使用employee_id查询assignee_id字段
        status=status,
        keyword=keyword
    )
    return tasks


@router.get("/my-reports", response_model=DailyReportListResponseOptimized, summary="获取我的日报列表")
def read_my_reports(
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user),
    report_date: Optional[date] = Query(None, description="指定日期"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    status: Optional[str] = Query(None, description="状态筛选", enum=["待提交", "已提交", "已评价"]),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    skip = (page - 1) * size
    reports, total = get_daily_reports(
        db,
        employee_id=current_user.employee_id,
        report_date=report_date,
        start_date=start_date,
        end_date=end_date,
        status=status,
        skip=skip,
        limit=size
    )
    
    # 计算实际工时并简化响应数据
    from sqlalchemy import func
    from app.models.daily_report import DailyWorkItem
    
    converted_reports = []
    for report in reports:
        actual_hours = db.query(func.sum(DailyWorkItem.hours_spent)).filter(
            DailyWorkItem.report_id == report.id,
            DailyWorkItem.is_deleted == False
        ).scalar() or 0.0
        
        # 简化的响应数据（移除不需要的字段）
        report_dict = {
            "id": report.id,
            "report_date": report.report_date,
            "employee_id": report.employee_id,
            "employee_name": report.employee_name,
            "tomorrow_plan": report.tomorrow_plan or "",
            "work_target": report.work_target or "",  # 添加工作目标字段
            "planned_hours": float(report.planned_hours) if report.planned_hours else 0.0,
            "actual_hours": float(actual_hours),
            "status": report.status,
            "submitted_at": report.submitted_at,
            "create_time": report.create_time,
            "update_time": report.update_time,
            "report_mode": report.report_mode or "free"  # 添加日报模式字段
        }
        
        converted_reports.append(report_dict)
    
    total_pages = (total + size - 1) // size if total > 0 else 0
    return {
        "items": converted_reports,
        "total": total,
        "page": page,
        "size": size,
        "total_pages": total_pages
    }


@router.get("/my-reports/{report_id}", summary="获取日报详情")
def read_daily_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    # 先用数据库对象进行权限检查
    db_report = get_daily_report(db, report_id, as_dict=False)
    if not db_report:
        raise HTTPException(status_code=404, detail="日报未找到")
    
    if db_report.employee_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权查看此日报")
    
    # 再获取字典版本返回给前端
    report = get_daily_report(db, report_id, as_dict=True)
    
    return report


@router.post("/my-reports", response_model=DailyReportResponse, summary="创建/更新日报")
def create_or_update_daily_report(
    report_data: DailyReportCreate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    report_data.employee_id = current_user.employee_id
    report_data.employee_name = current_user.name
    
    return create_daily_report(db, report_data)


@router.post("/my-reports/with-items", response_model=DailyReportResponse, summary="创建包含工作事项的日报")
def create_daily_report_with_items_handler(
    report_with_items: DailyReportWithItemsCreate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    # 更新员工信息
    report_with_items.report.employee_id = current_user.employee_id
    report_with_items.report.employee_name = current_user.name
    
    # 创建或更新日报
    db_report = create_daily_report_with_items(db, report_with_items)
    
    # 转换为响应模型格式以确保时间字段正确序列化
    report_dict = {
        "id": db_report.id,
        "report_date": db_report.report_date,
        "employee_id": db_report.employee_id,
        "employee_name": db_report.employee_name,
        "tomorrow_plan": db_report.tomorrow_plan,
        "work_target": db_report.work_target or "",
        "key_work_tracking": db_report.key_work_tracking or "",
        "planned_hours": float(db_report.planned_hours) if db_report.planned_hours else 0.0,
        "status": db_report.status,
        "submitted_at": db_report.submitted_at,
        "create_time": db_report.create_time,
        "update_time": db_report.update_time,
        "work_items": []
    }
    
    # 转换工作事项
    if hasattr(db_report, 'work_items') and db_report.work_items:
        work_items = []
        for item in db_report.work_items:
            work_item = {
                "id": item.id,
                "report_id": item.report_id,
                "work_content": item.work_content or "",
                "project_id": item.project_id or "",
                "project_name": item.project_name or "",
                "task_id": item.task_id or "",
                "task_name": item.task_name or "",
                "key_work_tracking": item.key_work_tracking or "",
                "start_time": item.start_time.strftime('%H:%M') if hasattr(item.start_time, 'strftime') else str(item.start_time or ""),
                "end_time": item.end_time.strftime('%H:%M') if hasattr(item.end_time, 'strftime') else str(item.end_time or ""),
                "hours_spent": float(item.hours_spent) if item.hours_spent else 0.0,
                "result": item.result or "",
                "measures": item.measures or "",
                "evaluation": item.evaluation or "",
                "progress_status": item.progress_status or "正常",
                "progress_percentage": float(item.progress_percentage) if item.progress_percentage else 0.0,
                "delay_hours": float(item.delay_hours) if item.delay_hours else 0.0,
                "improvement_result": item.improvement_result or ""
            }
            work_items.append(work_item)
        
        report_dict["work_items"] = work_items
    
    return report_dict


@router.put("/my-reports/{report_id}", response_model=DailyReportResponse, summary="更新日报")
def update_daily_report_handler(
    report_id: int,
    report_data: DailyReportUpdate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    db_report = get_daily_report(db, report_id)
    if not db_report:
        raise HTTPException(status_code=404, detail="日报未找到")
    
    if db_report.employee_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权修改此日报")
    
    if db_report.status == "已评价":
        raise HTTPException(status_code=400, detail="已评价的日报无法修改")
    
    # 更新日报后，重新获取数据并序列化响应
    updated_report = update_daily_report(db, report_id, report_data)
    if not updated_report:
        raise HTTPException(status_code=404, detail="更新失败")
    
    # 手动构建响应格式，确保时间字段正确序列化
    report_dict = {
        "id": updated_report.id,
        "report_date": updated_report.report_date.isoformat() if hasattr(updated_report.report_date, 'isoformat') else str(updated_report.report_date),
        "employee_id": updated_report.employee_id,
        "employee_name": updated_report.employee_name,
        "tomorrow_plan": updated_report.tomorrow_plan or "",
        "work_target": updated_report.work_target or "",
        "key_work_tracking": updated_report.key_work_tracking or "",
        "planned_hours": float(updated_report.planned_hours) if updated_report.planned_hours else 0.0,
        "status": updated_report.status,
        "submitted_at": updated_report.submitted_at.isoformat() if updated_report.submitted_at and hasattr(updated_report.submitted_at, 'isoformat') else str(updated_report.submitted_at) if updated_report.submitted_at else None,
        "create_time": updated_report.create_time.isoformat() if hasattr(updated_report.create_time, 'isoformat') else str(updated_report.create_time),
        "update_time": updated_report.update_time.isoformat() if hasattr(updated_report.update_time, 'isoformat') else str(updated_report.update_time),
        "work_items": []
    }
    
    # 转换工作事项，使用DailyWorkItemResponse类来处理时间字段
    if hasattr(updated_report, 'work_items') and updated_report.work_items:
        work_items = []
        for item in updated_report.work_items:
            # 使用DailyWorkItemResponse来处理时间字段序列化
            work_item = DailyWorkItemResponse(
                id=item.id,
                report_id=item.report_id,
                work_content=item.work_content,
                project_id=item.project_id,
                project_name=item.project_name,
                task_id=item.task_id,
                task_name=item.task_name,
                start_time=item.start_time.strftime('%H:%M') if hasattr(item.start_time, 'strftime') else str(item.start_time) if item.start_time else None,
                end_time=item.end_time.strftime('%H:%M') if hasattr(item.end_time, 'strftime') else str(item.end_time) if item.end_time else None,
                hours_spent=item.hours_spent,
                progress_status=item.progress_status,
                progress_percentage=item.progress_percentage,
                delay_hours=item.delay_hours,
                improvement_result=item.improvement_result,
                result=item.result,
                measures=item.measures,
                evaluation=item.evaluation
            )
            work_items.append(work_item)
        
        report_dict["work_items"] = work_items
    
    return report_dict


@router.post("/my-reports/{report_id}/submit", response_model=DailyReportResponse, summary="提交日报")
def submit_daily_report_handler(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    db_report = get_daily_report(db, report_id)
    if not db_report:
        raise HTTPException(status_code=404, detail="日报未找到")
    
    if db_report.employee_id != current_user.employee_id:
         raise HTTPException(status_code=403, detail="无权提交此日报")
    
    if db_report.status == "已评价":
        raise HTTPException(status_code=400, detail="已评价的日报无法重复提交")
    
    return submit_daily_report(db, report_id)


@router.delete("/my-reports/{report_id}", status_code=204, summary="删除日报")
def delete_daily_report_handler(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    db_report = get_daily_report(db, report_id)
    if not db_report:
        raise HTTPException(status_code=404, detail="日报未找到")
    
    if db_report.employee_id != current_user.employee_id:
         raise HTTPException(status_code=403, detail="无权删除此日报")
    
    if not delete_daily_report(db, report_id):
        raise HTTPException(status_code=404, detail="日报未找到")
    
    return None


@router.get("/my-work-logs", response_model=List[DailyWorkLogResponse], summary="获取我的工作日志")
def read_my_work_logs(
    work_date: date = Query(..., description="工作日期"),
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    return get_daily_work_logs(db, str(current_user.id), work_date)


@router.post("/my-work-logs", response_model=DailyWorkLogResponse, summary="创建工作日志")
def create_work_log_handler(
    log: DailyWorkLogCreate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    log.employee_id = str(current_user.id)
    person = db.query(Personnel).filter(Personnel.id == current_user.id).first()
    employee_name = person.name if person else current_user.username
    return create_daily_work_log(db, log, employee_name)


@router.get("/pending-reports", response_model=DailyReportListResponse, summary="获取待审核的日报列表（领导用）")
def read_pending_reports(
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    skip = (page - 1) * size
    reports, total = get_pending_reports(
        db,
        supervisor_id=str(current_user.id),
        skip=skip,
        limit=size
    )
    total_pages = (total + size - 1) // size if total > 0 else 0
    return {
        "items": reports,
        "total": total,
        "page": page,
        "size": size,
        "total_pages": total_pages
    }


@router.post("/pending-reports/{report_id}/evaluate", response_model=DailyReportResponse, summary="审核评价日报（领导用）")
def evaluate_daily_report_handler(
    report_id: int,
    evaluation: DailyReportEvaluate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    db_report = get_daily_report(db, report_id)
    if not db_report:
        raise HTTPException(status_code=404, detail="日报未找到")
    
    if db_report.status != "待评价":
        raise HTTPException(status_code=400, detail="该日报不在待评价状态")
    
    person = db.query(Personnel).filter(Personnel.id == current_user.id).first()
    supervisor_name = person.name if person else current_user.username
    
    return evaluate_daily_report(
        db,
        report_id,
        str(current_user.id),
        supervisor_name,
        evaluation.supervisor_score,
        evaluation.supervisor_comment
    )


# ===== 主管信息相关路由 =====

@router.get("/supervisor-info/{employee_id}", summary="获取主管信息")
def get_supervisor_info(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """获取主管信息"""
    # 查找主管信息
    supervisor = db.query(Personnel).filter(
        Personnel.employee_id == employee_id,
        Personnel.is_deleted == False
    ).first()
    
    if not supervisor:
        raise HTTPException(status_code=404, detail="主管信息不存在")
    
    return {
        "supervisor_id": supervisor.employee_id,
        "supervisor_name": supervisor.name,
        "department": getattr(supervisor, 'department', ''),
        "position": getattr(supervisor, 'position', '')
    }

# ===== 附件管理相关路由 =====

@router.get("/attachments/{report_id}", response_model=List[DailyReportAttachmentSchema], summary="获取日报附件列表")
def get_daily_report_attachments(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """获取日报附件列表"""
    # 验证日报是否存在
    db_report = get_daily_report(db, report_id)
    if not db_report:
        raise HTTPException(status_code=404, detail="日报不存在")
    
    # 获取附件列表
    attachments = get_attachments_by_report_id(db, report_id)
    return attachments

@router.get("/attachment/{attachment_id}", response_model=DailyReportAttachmentSchema, summary="获取单个附件详情")
def get_daily_report_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """获取单个附件详情"""
    # 获取附件
    attachment = get_attachment_by_id(db, attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="附件不存在")
    
    return attachment

@router.post("/attachments/{report_id}", response_model=DailyReportAttachmentSchema, summary="上传附件")
def upload_daily_report_attachment(
    report_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """上传附件"""
    # 验证日报是否存在
    db_report = get_daily_report(db, report_id)
    if not db_report:
        raise HTTPException(status_code=404, detail="日报不存在")
    
    # 验证文件类型和大小
    is_valid, error_message = validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # 保存文件
    saved_filename = save_uploaded_file(file)
    file_path = os.path.join(UPLOAD_DIR, saved_filename)
    
    # 获取文件大小
    file.file.seek(0)
    file_size = len(file.file.read())
    file.file.seek(0)
    
    # 创建附件记录
    from app.models.daily_report_attachment import DailyReportAttachment
    from datetime import datetime
    
    attachment_model = DailyReportAttachment(
        report_id=report_id,
        file_name=file.filename,
        file_data=file_path,
        file_size=file_size,
        file_type=file.content_type,
        uploader_id=current_user.employee_id,
        uploader_name=current_user.name,
        uploaded_at=datetime.now()
    )
    
    # 保存到数据库
    result = create_attachment(db, attachment_model)
    return result

@router.delete("/attachments/{attachment_id}", summary="删除附件")
def delete_daily_report_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """删除附件"""
    # 查找附件
    attachment = get_attachment_by_id(db, attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="附件不存在")
    
    # 软删除
    if delete_attachment(db, attachment_id):
        return {"message": "附件删除成功"}
    else:
        raise HTTPException(status_code=404, detail="附件不存在")

@router.get("/attachments/{attachment_id}/download", summary="下载附件")
def download_daily_report_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """下载附件"""
    attachment = get_attachment_by_id(db, attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="附件不存在")
    
    if not os.path.exists(attachment.file_data):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 返回文件流
    from fastapi.responses import StreamingResponse
    
    def file_generator():
        with open(attachment.file_data, "rb") as f:
            while chunk := f.read(8192):
                yield chunk
    
    return StreamingResponse(
        file_generator(),
        media_type=attachment.file_type,
        headers={
            "Content-Disposition": f"attachment; filename*=utf-8''{urllib.parse.quote(attachment.file_name)}",
            "Content-Length": str(attachment.file_size)
        }
    )

@router.get("/attachments/{attachment_id}/preview", summary="预览附件")
def preview_daily_report_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """预览附件"""
    import base64
    
    attachment = get_attachment_by_id(db, attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="附件不存在")
    
    if not os.path.exists(attachment.file_data):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 支持预览的文件类型
    previewable_types = {
        'image/jpeg', 'image/png', 'image/gif', 'image/webp',
        'application/pdf', 'text/plain'
    }
    
    if attachment.file_type not in previewable_types:
        return {"message": "该文件类型不支持预览"}
    
    # 对于图片文件，返回base64编码
    if attachment.file_type.startswith('image/'):
        with open(attachment.file_data, "rb") as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
            return f"data:{attachment.file_type};base64,{image_data}"
    
    # 对于PDF和文本文件，返回文件内容
    elif attachment.file_type == 'application/pdf':
        with open(attachment.file_data, "rb") as f:
            pdf_data = base64.b64encode(f.read()).decode('utf-8')
            return f"data:application/pdf;base64,{pdf_data}"
    
    elif attachment.file_type == 'text/plain':
        with open(attachment.file_data, "r", encoding='utf-8') as f:
            text_content = f.read()
            return f"data:text/plain;charset=utf-8,{base64.b64encode(text_content.encode('utf-8')).decode('utf-8')}"
    
    return {"message": "不支持预览该文件类型"}


# 文件处理辅助函数

import shutil
import uuid
from typing import Set

# 文件存储配置
UPLOAD_DIR = "uploads/daily_reports"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 支持的文件类型
SUPPORTED_FILE_TYPES: Set[str] = {
    'image/jpeg', 'image/png', 'image/gif', 'image/webp',
    'application/pdf', 'application/msword', 
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain', 'text/csv',
    'application/sql', 'text/sql', 'application/x-sql',
    'application/json', 'text/json',
    'application/xml', 'text/xml',
    'application/zip', 'application/x-rar-compressed',
    'video/mp4', 'video/avi', 'video/mov',
    'audio/mp3', 'audio/wav'
}

# 支持的文件扩展名
SUPPORTED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.webp',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.txt', '.csv', '.sql', '.json', '.xml',
    '.zip', '.rar', '.mp4', '.avi', '.mov',
    '.mp3', '.wav'
}

# 最大文件大小 (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

def validate_file(file: UploadFile) -> tuple[bool, str]:
    """验证上传文件，返回 (是否通过, 错误信息)"""
    try:
        # 检查文件名
        if not file.filename or len(file.filename.strip()) == 0:
            return False, "文件名不能为空"
        
        # 获取文件扩展名
        import os
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        # 检查文件大小 (通过position)
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置位置
        
        if file_size > MAX_FILE_SIZE:
            return False, f"文件过大: {file_size / (1024*1024):.2f}MB。最大支持: {MAX_FILE_SIZE / (1024*1024):.0f}MB"
        
        if file_size == 0:
            return False, "文件为空，请选择有效的文件"
        
        # 检查文件类型和扩展名
        content_type_ok = file.content_type in SUPPORTED_FILE_TYPES
        extension_ok = file_extension in SUPPORTED_EXTENSIONS
        
        if not (content_type_ok or extension_ok):
            return False, f"不支持的文件类型: {file.content_type} ({file_extension})。支持的类型包括: 图片(.jpg/.png等)、PDF、Office文档、文本文件(.txt/.csv/.sql)、压缩文件、音视频文件"
        
        # 如果是未知类型但扩展名正确，也允许上传
        if not content_type_ok and extension_ok:
            print(f"警告: 未知content_type '{file.content_type}'，但扩展名 '{file_extension}' 支持")
        
        return True, "验证通过"
    except Exception as e:
        return False, f"文件验证失败: {str(e)}"

def save_uploaded_file(file: UploadFile) -> str:
    """保存上传的文件"""
    # 生成唯一文件名
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return unique_filename


# ==================== 简版日报（关联目标模式）API ====================

@router.get("/current-week-goal", response_model=CurrentWeekGoalResponse, summary="获取本周目标（用于简版日报预填）")
def read_current_week_goal_for_report(
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user),
    current_date: Optional[date] = Query(None, description="指定日期，默认为今天")
):
    """
    获取当前周目标，用于简版日报自动填充
    
    - 根据当前日期自动判断属于第几周
    - 返回周目标详情及关联的月度目标信息
    """
    from app.crud.monthly_goal import get_current_week_goal
    from app.models.monthly_goal import MonthlyGoal, WeeklyGoal
    
    result = get_current_week_goal(db, current_user.employee_id, current_date)
    
    if not result or not result.get("weekly_goal"):
        raise HTTPException(status_code=404, detail="未找到本周目标，请先设置月度目标")
    
    weekly_goal = result["weekly_goal"]
    monthly_goal = db.query(MonthlyGoal).filter(MonthlyGoal.id == weekly_goal.goal_id).first()

    return CurrentWeekGoalResponse(
        weekly_goal_id=weekly_goal.id,
        weekly_goal_title=weekly_goal.title,
        weekly_goal_content=weekly_goal.content,
        monthly_goal_id=monthly_goal.id if monthly_goal else 0,
        month=result.get("month", ""),
        month_title=result.get("month_title", ""),
        week_number=result.get("week_number", 0),
        start_date=weekly_goal.start_date,
        end_date=weekly_goal.end_date
    )


@router.post("/with-goal", response_model=DailyReportResponse, summary="创建简版日报（关联目标模式）")
def create_goal_linked_report(
    report_data: GoalLinkedDailyReportCreate,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """
    创建简版日报（关联目标模式）
    
    与自由填报的区别：
    - 自动关联月度/周目标
    - 工作目标自动填充为周目标标题
    - 适合目标明确的日常工作填报
    """
    from app.models.monthly_goal import WeeklyGoal
    
    # 验证周目标是否存在
    weekly_goal = db.query(WeeklyGoal).filter(WeeklyGoal.id == report_data.linked_weekly_goal_id).first()
    if not weekly_goal:
        raise HTTPException(status_code=404, detail="关联的周目标不存在")
    
    # 验证权限
    from app.models.monthly_goal import MonthlyGoal
    monthly_goal = db.query(MonthlyGoal).filter(MonthlyGoal.id == report_data.linked_monthly_goal_id).first()
    if not monthly_goal or monthly_goal.user_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权使用此目标")
    
    # 检查当天是否已有日报
    existing_report = db.query(DailyReport).filter(
        DailyReport.employee_id == current_user.employee_id,
        DailyReport.report_date == report_data.report_date,
        DailyReport.is_deleted == False
    ).first()
    
    if existing_report:
        raise HTTPException(status_code=400, detail="当天已存在日报，无法重复创建")
    
    # 创建简版日报
    db_report = create_goal_linked_daily_report(
        db=db,
        report_data=report_data,
        employee_id=current_user.employee_id,
        employee_name=current_user.name,
        weekly_goal_title=weekly_goal.title
    )
    
    # 转换为响应格式
    report_dict = {
        "id": db_report.id,
        "report_date": db_report.report_date,
        "employee_id": db_report.employee_id,
        "employee_name": db_report.employee_name,
        "work_target": db_report.work_target or "",
        "key_work_tracking": db_report.key_work_tracking or "",
        "tomorrow_plan": db_report.tomorrow_plan or "",
        "planned_hours": float(db_report.planned_hours) if db_report.planned_hours else 0.0,
        "status": db_report.status,
        "submitted_at": db_report.submitted_at,
        "create_time": db_report.create_time,
        "update_time": db_report.update_time,
        "report_mode": db_report.report_mode,
        "linked_monthly_goal_id": db_report.linked_monthly_goal_id,
        "linked_weekly_goal_id": db_report.linked_weekly_goal_id,
        "work_items": []
    }
    
    # 转换工作事项
    if db_report.work_items:
        for item in db_report.work_items:
            # 处理时间字段 - 兼容字符串和datetime.time对象
            start_time_str = item.start_time
            end_time_str = item.end_time
            
            # 如果是time对象，转换为字符串
            if hasattr(start_time_str, 'strftime'):
                start_time_str = start_time_str.strftime('%H:%M')
            if hasattr(end_time_str, 'strftime'):
                end_time_str = end_time_str.strftime('%H:%M')
            
            work_item = {
                "id": item.id,
                "report_id": item.report_id,
                "work_content": item.work_content or "",
                "project_id": item.project_id or "",
                "project_name": item.project_name or "",
                "task_id": item.task_id or "",
                "task_name": item.task_name or "",
                "start_time": start_time_str or "",
                "end_time": end_time_str or "",
                "hours_spent": float(item.hours_spent) if item.hours_spent else 0.0,
                "progress_status": item.progress_status or "正常",
                "progress_percentage": float(item.progress_percentage) if item.progress_percentage else 0.0,
                "delay_hours": float(item.delay_hours) if item.delay_hours else 0.0,
                "improvement_result": item.improvement_result or "",
                "result": item.result or "",
                "measures": item.measures or "",
                "evaluation": item.evaluation or ""
            }
            report_dict["work_items"].append(work_item)
    
    return report_dict


@router.post("/{report_id}/update-goal-progress", summary="手动触发更新周目标进度")
def trigger_update_goal_progress(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: Personnel = Depends(get_current_user)
):
    """
    手动触发根据日报更新周目标进度
    
    通常在提交日报后自动调用，此接口用于手动刷新
    """
    db_report = get_daily_report(db, report_id)
    if not db_report:
        raise HTTPException(status_code=404, detail="日报未找到")
    
    if db_report.employee_id != current_user.employee_id:
        raise HTTPException(status_code=403, detail="无权操作此日报")
    
    success = update_weekly_goal_progress_from_report(db, report_id)
    
    if success:
        return {"message": "周目标进度已更新"}
    else:
        return {"message": "无需更新（未关联目标或无工作事项）"}
