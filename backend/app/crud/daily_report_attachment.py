"""
日报附件CRUD操作
"""
from sqlalchemy.orm import Session
from typing import List
from app.models.daily_report_attachment import DailyReportAttachment

def get_attachments_by_report_id(db: Session, report_id: int) -> List[DailyReportAttachment]:
    """根据日报ID获取附件列表"""
    return db.query(DailyReportAttachment).filter(
        DailyReportAttachment.report_id == report_id,
        DailyReportAttachment.is_deleted == False
    ).all()

def get_attachment_by_id(db: Session, attachment_id: int) -> DailyReportAttachment:
    """根据ID获取附件"""
    return db.query(DailyReportAttachment).filter(
        DailyReportAttachment.id == attachment_id,
        DailyReportAttachment.is_deleted == False
    ).first()

def create_attachment(db: Session, attachment: DailyReportAttachment) -> DailyReportAttachment:
    """创建附件"""
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment

def update_attachment(db: Session, attachment_id: int, **kwargs) -> DailyReportAttachment:
    """更新附件"""
    attachment = get_attachment_by_id(db, attachment_id)
    if attachment:
        for key, value in kwargs.items():
            setattr(attachment, key, value)
        db.commit()
        db.refresh(attachment)
    return attachment

def delete_attachment(db: Session, attachment_id: int) -> bool:
    """删除附件（软删除）"""
    attachment = get_attachment_by_id(db, attachment_id)
    if attachment:
        attachment.is_deleted = True
        db.commit()
        return True
    return False
