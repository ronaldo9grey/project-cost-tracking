from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar('T')


class ResponseBase(BaseModel):
    """基础响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None


class PaginationResponse(BaseModel):
    """分页响应模型"""
    items: Any
    total: int
    page: int
    size: int
    total_pages: int


class SuccessResponse(ResponseBase, Generic[T]):
    """成功响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None


class ErrorResponse(ResponseBase):
    """错误响应模型"""
    code: int = 500
    message: str = "internal server error"
    data: Optional[Any] = None
    
    @classmethod
    def from_exception(cls, exception: Exception, code: int = 500):
        """从异常创建错误响应"""
        return cls(
            code=code,
            message=str(exception),
            data=None
        )