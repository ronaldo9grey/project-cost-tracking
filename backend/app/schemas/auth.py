from pydantic import BaseModel, Field
from typing import Optional


# 令牌模型
class Token(BaseModel):
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(..., description="令牌类型")


# 令牌数据模型
class TokenData(BaseModel):
    username: Optional[str] = Field(None, description="用户名")


# 用户登录模型
class UserLogin(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")


# 修改密码模型
class ChangePassword(BaseModel):
    old_password: str = Field(..., min_length=6, max_length=100, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")
    confirm_password: str = Field(..., min_length=6, max_length=100, description="确认新密码")
