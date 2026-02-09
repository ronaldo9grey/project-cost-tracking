#!/usr/bin/env python3
"""
测试数据库URL构建
"""
from urllib.parse import quote

# 构建正确的数据库URL
username = "yjydb"
password = "Jlbk@2025"  # 原始密码
host = "cd-postgres-2p7vnsx4.sql.tencentcdb.com"
port = "25331"
database = "project_cost_tracking"

# 对密码进行URL编码
encoded_password = quote(password, safe='')

# 构建完整的数据库URL
database_url = f"postgresql://{username}:{encoded_password}@{host}:{port}/{database}"

print("=== 正确的数据库URL构建 ===")
print(f"原始密码: {password}")
print(f"编码后密码: {encoded_password}")
print(f"完整URL: {database_url}")

# 保存到.env文件的格式
env_format = f"DATABASE_URL=postgresql://{username}:{encoded_password}@{host}:{port}/{database}"
print(f"\n.env文件格式:")
print(env_format)