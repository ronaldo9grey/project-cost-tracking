from fastapi import HTTPException, status


class CustomException(HTTPException):
    """自定义异常基类"""
    def __init__(self, code: int, message: str):
        super().__init__(status_code=code, detail=message)
        self.code = code
        self.message = message


class NotFoundException(CustomException):
    """资源未找到异常"""
    def __init__(self, message: str = "资源未找到"):
        super().__init__(status.HTTP_404_NOT_FOUND, message)


class BadRequestException(CustomException):
    """请求参数错误异常"""
    def __init__(self, message: str = "请求参数错误"):
        super().__init__(status.HTTP_400_BAD_REQUEST, message)


class UnauthorizedException(CustomException):
    """未授权异常"""
    def __init__(self, message: str = "未授权访问"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message)


class ForbiddenException(CustomException):
    """禁止访问异常"""
    def __init__(self, message: str = "禁止访问"):
        super().__init__(status.HTTP_403_FORBIDDEN, message)


class ServerErrorException(CustomException):
    """服务器内部错误异常"""
    def __init__(self, message: str = "服务器内部错误"):
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, message)