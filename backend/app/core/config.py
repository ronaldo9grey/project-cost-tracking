from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # 应用基本配置
    APP_NAME: str = "项目管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置 - 从环境变量读取，不提供默认值以确保安全
    DATABASE_URL: str
    
    # 数据库连接池配置
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    # JWT配置 - 从环境变量读取，不提供默认值以确保安全
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 延长到24小时
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 1000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"


settings = Settings()
