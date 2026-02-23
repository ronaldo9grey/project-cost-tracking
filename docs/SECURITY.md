# 安全设置指南

## 🔐 环境变量配置

### 1. 本地开发环境

```bash
# 复制示例配置文件
cp backend/.env.example backend/.env

# 编辑 .env 文件，填入实际配置
vim backend/.env
```

### 2. 生产环境安全要求

#### JWT密钥生成
```bash
# 生成强随机密钥（32字节）
openssl rand -hex 32

# 或使用 Python
python -c "import secrets; print(secrets.token_hex(32))"
```

#### 数据库密码策略
- 最小长度：16位
- 包含：大小写字母 + 数字 + 特殊字符
- 定期更换（建议每90天）

#### 腾讯云 Secrets Manager 配置（推荐）
```python
# 生产环境建议从腾讯云 Secrets Manager 获取敏感配置
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ssm.v20190923 import ssm_client, models

def get_secret(secret_name):
    cred = credential.Credential(
        os.getenv("TENCENT_SECRET_ID"),
        os.getenv("TENCENT_SECRET_KEY")
    )
    client = ssm_client.SsmClient(cred, "ap-guangzhou")
    req = models.GetSecretValueRequest()
    req.SecretName = secret_name
    resp = client.GetSecretValue(req)
    return json.loads(resp.SecretString)
```

## 🛡️ 安全最佳实践

### 1. 敏感信息处理
- ✅ 使用 `.env` 文件存储敏感配置
- ✅ `.env` 已添加到 `.gitignore`，不会提交到Git
- ✅ 生产环境使用腾讯云 Secrets Manager 或环境变量注入
- ❌ 禁止在代码中硬编码密码、密钥
- ❌ 禁止提交 `.env` 文件到Git仓库

### 2. 数据库安全
```python
# 数据库连接池配置（已优化）
engine = create_engine(
    database_url,
    pool_size=10,
    max_overflow=15,
    pool_timeout=20,
    pool_recycle=1800,
    pool_pre_ping=False,
    connect_args={
        "connect_timeout": 5,
        "application_name": "project_tracking_api"
    },
    echo=False
)
```

### 3. API安全
- JWT Token 过期时间：2小时
- 刷新Token过期时间：7天
- 密码加密：bcrypt
- 接口限流：待实现

### 4. 日志安全
- 日志中不记录敏感信息（密码、Token）
- 定期清理日志文件
- 生产环境日志脱敏

## 🔧 安全配置检查清单

- [ ] `.env` 文件已从Git仓库移除
- [ ] `.env` 文件权限设置为 600
- [ ] JWT密钥已更换为强随机字符串
- [ ] 数据库密码符合复杂度要求
- [ ] 生产环境使用HTTPS
- [ ] 数据库连接使用SSL/TLS
- [ ] 定期更换密钥和密码
- [ ] 启用操作日志审计

## 🚨 安全事件响应

### 密钥泄露处理
1. 立即更换泄露的密钥/密码
2. 撤销所有已颁发的Token
3. 检查日志确认泄露范围
4. 通知相关人员

### 数据库访问异常
1. 检查数据库连接日志
2. 审查异常查询语句
3. 限制异常IP访问
4. 加强监控告警

## 📚 相关文档

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [腾讯云 Secrets Manager](https://cloud.tencent.com/document/product/1140)
