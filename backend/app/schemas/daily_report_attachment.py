"""
日报附件数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DailyReportAttachmentBase(BaseModel):
    """附件基础模型"""
    report_id: int = Field(..., description="日报ID")
    file_name: str = Field(..., description="文件名")
    file_data: str = Field(..., description="文件数据")
    file_size: int = Field(..., description="文件大小（字节）")
    file_type: Optional[str] = Field(None, description="文件类型")
    uploader_id: Optional[str] = Field(None, description="上传者ID")
    uploader_name: Optional[str] = Field(None, description="上传者姓名")
    uploaded_at: Optional[datetime] = Field(None, description="上传时间")

class DailyReportAttachment(DailyReportAttachmentBase):
    """附件响应模型"""
    id: int = Field(..., description="附件ID")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    is_deleted: bool = Field(False, description="是否删除")
    
    class Config:
        from_attributes = True

class DailyReportAttachmentCreate(DailyReportAttachmentBase):
    """创建附件模型"""
    pass

class DailyReportAttachmentUpdate(BaseModel):
    """更新附件模型"""
    file_name: Optional[str] = None
    file_type: Optional[str] = None
