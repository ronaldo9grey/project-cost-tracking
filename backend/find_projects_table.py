#!/usr/bin/env python3
"""
查找项目相关的表
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 数据库连接
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()

try:
    # 获取所有表名
    print("=== 数据库中的所有表 ===")
    result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
    tables = result.fetchall()
    for table in tables:
        table_name = table[0]
        print(f"  {table_name}")
    
    # 查找可能的项目表
    print("\n=== 查找可能的项目表 ===")
    project_like_tables = [t[0] for t in tables if 'project' in t[0].lower()]
    print(f"包含'project'的表: {project_like_tables}")
    
    # 检查每个表的字段
    for table_name in project_like_tables:
        print(f"\n{table_name}表的结构:")
        try:
            result = db.execute(text(f"PRAGMA table_info({table_name})"))
            cols = result.fetchall()
            for col in cols:
                print(f"  {col[1]} ({col[2]})")
        except Exception as e:
            print(f"  无法获取表结构: {e}")

except Exception as e:
    print(f"查询出错: {e}")
finally:
    db.close()