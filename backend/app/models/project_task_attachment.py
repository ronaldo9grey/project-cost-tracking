from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class ProjectTaskAttachment(Base):
    __tablename__ = "project_task_attachments"
    
    attachment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(String(50), ForeignKey("project_tasks.task_id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_data = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=False)
    uploader_id = Column(String(50))
    uploader_name = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())