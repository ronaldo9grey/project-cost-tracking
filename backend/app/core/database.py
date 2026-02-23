from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from urllib.parse import quote_plus


def encode_database_url(url: str) -> str:
    """对数据库URL中的密码进行编码，处理特殊字符"""
    if '@' in url and '://' in url:
        proto_part = url.split('://')[0]
        rest = url.split('://')[1]
        
        if '@' in rest:
            creds_host_part = rest.rsplit('@', 1)[0]
            host_db_part = rest.rsplit('@', 1)[1]
            
            if ':' in creds_host_part:
                parts = creds_host_part.split(':')
                user = parts[0]
                password = ':'.join(parts[1:])
                encoded_password = quote_plus(password)
                return f"{proto_part}://{user}:{encoded_password}@{host_db_part}"
    return url


# 根据数据库类型创建引擎配置
def create_db_engine():
    # 获取编码后的数据库URL
    database_url = encode_database_url(settings.DATABASE_URL)
    
    # SQLite配置
    if database_url.startswith('sqlite'):
        return create_engine(
            database_url,
            echo=False  # 关闭SQL打印，提高性能
        )
    # PostgreSQL配置
    else:
        return create_engine(
            database_url,
            pool_size=10,               # 减少连接池大小，避免资源竞争
            max_overflow=15,            # 减少最大溢出连接数
            pool_timeout=20,            # 减少超时时间
            pool_recycle=1800,          # 缩短连接回收时间到30分钟
            pool_pre_ping=False,        # 禁用连接预检查，避免并发问题
            pool_use_lifo=False,        # 使用FIFO策略避免连接冲突
            connect_args={
                "connect_timeout": 5,   # 连接超时时间
                "application_name": "project_tracking_api"  # 标识应用
            },
            echo=False                  # 关闭SQL语句打印，提高性能
        )

# 创建数据库引擎
engine = create_db_engine()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()
