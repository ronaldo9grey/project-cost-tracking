from fastapi import Query, Depends
from typing import Optional
from app.core.config import settings


class PaginationParams:
    """分页参数依赖"""
    def __init__(
        self,
        page: int,
        size: int
    ):
        self.page = page
        self.size = size
        self.skip = (page - 1) * size
        self.limit = size


def get_pagination_params(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="每页大小")
) -> PaginationParams:
    """获取分页参数"""
    return PaginationParams(page=page, size=size)


def get_db():
    """获取数据库会话"""
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()