#!/usr/bin/env python3
"""
清理测试数据脚本
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 数据库配置
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/project_management"

def clear_test_data():
    """清理测试数据"""
    print("=== 清理测试数据 ===")
    
    try:
        # 创建数据库连接
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        from sqlalchemy import text
        
        print("1. 清理日报工作事项表...")
        db.execute(text("DELETE FROM daily_work_items"))
        
        print("2. 清理日报表...")
        db.execute(text("DELETE FROM daily_reports"))
        
        print("3. 清理评价表...")
        db.execute(text("DELETE FROM daily_report_evaluations"))
        
        # 提交事务
        db.commit()
        db.close()
        
        print("✅ 测试数据清理完成")
        
    except Exception as e:
        print(f"❌ 清理数据失败: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()

if __name__ == "__main__":
    clear_test_data()