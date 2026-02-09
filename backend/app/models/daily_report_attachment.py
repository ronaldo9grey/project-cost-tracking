"""
日报附件数据模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DailyReportAttachment(Base):
    """日报附件模型"""
    __tablename__ = "daily_report_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, nullable=False, comment="日报ID")
    file_name = Column(Text, nullable=False, comment="文件名")
    file_data = Column(Text, nullable=False, comment="文件数据")
    file_size = Column(Integer, nullable=False, comment="文件大小（字节）")
    file_type = Column(String(100), comment="文件类型")
    uploader_id = Column(String(50), comment="上传者ID")
    uploader_name = Column(String(100), comment="上传者姓名")
    uploaded_at = Column(DateTime, comment="上传时间")
    create_time = Column(DateTime, comment="创建时间")
    update_time = Column(DateTime, comment="更新时间")
    is_deleted = Column(Boolean, default=False, comment="是否删除")
