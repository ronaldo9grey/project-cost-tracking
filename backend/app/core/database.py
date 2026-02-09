from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 根据数据库类型创建引擎配置
def create_db_engine():
    # SQLite配置
    if settings.DATABASE_URL.startswith('sqlite'):
        return create_engine(
            settings.DATABASE_URL,
            echo=False  # 关闭SQL打印，提高性能
        )
    # PostgreSQL配置
    else:
        return create_engine(
            settings.DATABASE_URL,
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
