"""
日报附件管理API
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
import os
import shutil
from datetime import datetime
import uuid
import urllib.parse

from app.database import get_db
from app.models.daily_report import DailyReport
from app.models.daily_report_attachment import DailyReportAttachment
from app.schemas.daily_report_attachment import (
    DailyReportAttachment as DailyReportAttachmentSchema,
    DailyReportAttachmentCreate
)

router = APIRouter(prefix="/attachments", tags=["daily-report-attachments"])

# 文件存储配置
UPLOAD_DIR = "uploads/daily_reports"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 支持的文件类型
SUPPORTED_FILE_TYPES = {
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

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_token
from app.models.resource import Personnel

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户信息"""
    try:
        # 验证token
        payload = verify_token(credentials.credentials)
        employee_id = payload.get("sub")
        
        # 从数据库获取用户信息
        db = next(get_db())
        user = db.query(Personnel).filter(Personnel.employee_id == employee_id).first()
        db.close()
        
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
            
        return {
            "id": user.id,
            "employee_id": user.employee_id,
            "employee_name": user.name
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="认证失败")

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
            return False, f"不支持的文件类型: {file.content_type} ({file_extension})。支持的类型包括: 图片(.jpg/.png等)、PDF、Office文档、文本文件(.txt/.csv/.sql)、压缩文件，音视频文件"
        
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

@router.get("/{report_id}", response_model=List[DailyReportAttachmentSchema])
async def get_attachments(
    report_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取日报附件列表"""
    # 验证日报是否存在
    daily_report = db.query(DailyReport).filter(DailyReport.id == report_id).first()
    if not daily_report:
        raise HTTPException(status_code=404, detail="日报不存在")
    
    # 获取附件列表
    attachments = db.query(DailyReportAttachment).filter(
        DailyReportAttachment.report_id == report_id,
        DailyReportAttachment.is_deleted == False
    ).all()
    
    return attachments

@router.post("/{report_id}", response_model=DailyReportAttachmentSchema)
async def upload_attachment(
    report_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """上传附件"""
    # 验证日报是否存在
    daily_report = db.query(DailyReport).filter(DailyReport.id == report_id).first()
    if not daily_report:
        raise HTTPException(status_code=404, detail="日报不存在")
    
    # 验证文件
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
    attachment = DailyReportAttachment(
        report_id=report_id,
        file_name=file.filename,
        file_data=file_path,
        file_size=file_size,
        file_type=file.content_type,
        uploader_id=current_user["employee_id"],
        uploader_name=current_user["employee_name"],
        uploaded_at=datetime.now()
    )
    
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    
    return attachment

@router.delete("/{attachment_id}")
async def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除附件"""
    # 查找附件
    attachment = db.query(DailyReportAttachment).filter(
        DailyReportAttachment.id == attachment_id,
        DailyReportAttachment.is_deleted == False
    ).first()
    
    if not attachment:
        raise HTTPException(status_code=404, detail="附件不存在")
    
    # 软删除
    attachment.is_deleted = True
    db.commit()
    
    # 可选：物理删除文件
    # if os.path.exists(attachment.file_path):
    #     os.remove(attachment.file_path)
    
    return {"message": "附件删除成功"}

@router.get("/{attachment_id}/download")
async def download_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """下载附件"""
    attachment = db.query(DailyReportAttachment).filter(
        DailyReportAttachment.id == attachment_id,
        DailyReportAttachment.is_deleted == False
    ).first()
    
    if not attachment:
        raise HTTPException(status_code=404, detail="附件不存在")
    
    if not os.path.exists(attachment.file_data):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 返回文件流
    def file_generator():
        with open(attachment.file_data, "rb") as f:
            while chunk := f.read(8192):
                yield chunk
    
    from fastapi.responses import StreamingResponse
    
    return StreamingResponse(
        file_generator(),
        media_type=attachment.file_type,
        headers={
            "Content-Disposition": f"attachment; filename*=utf-8''{urllib.parse.quote(attachment.file_name)}",
            "Content-Length": str(attachment.file_size)
        }
    )

@router.get("/{attachment_id}/preview")
async def preview_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """预览附件"""
    attachment = db.query(DailyReportAttachment).filter(
        DailyReportAttachment.id == attachment_id,
        DailyReportAttachment.is_deleted == False
    ).first()
    
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
