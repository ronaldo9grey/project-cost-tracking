# 🔒 安全修复指南

## 问题描述

发现代码中存在硬编码的敏感信息：
- 数据库密码
- JWT密钥

这些信息已暴露在Git历史中，需要立即修复。

---

## ✅ 修复步骤

### 步骤1: 立即修改数据库密码

1. 登录腾讯云控制台
2. 进入 PostgreSQL 实例管理
3. 找到数据库用户 `yjydb`
4. 修改密码为新的强密码

### 步骤2: 创建本地环境变量文件

在 `backend/` 目录下创建 `.env` 文件：

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，填入实际值：

```env
# 数据库连接（使用新密码）
DATABASE_URL=postgresql://yjydb:你的新密码@cd-postgres-2p7vnsx4.sql.tencentcdb.com:25331/project_cost_tracking

# JWT密钥（生成新的随机密钥）
SECRET_KEY=your-new-random-secret-key
```

生成随机密钥：
```bash
openssl rand -hex 32
```

### 步骤3: 测试应用

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

确保应用能正常启动（如果没有.env文件会报错）。

### 步骤4: 提交修复后的代码

```bash
# 添加修复的文件
git add backend/app/core/config.py
git add backend/.env.example
git add backend/.gitignore

# 提交
git commit -m "security: remove hardcoded credentials from config

- Remove hardcoded DATABASE_URL
- Remove hardcoded SECRET_KEY
- Add .env.example template
- Add .gitignore to exclude .env files

BREAKING CHANGE: Application now requires .env file to run"

# 推送
git push origin main
```

---

## ⚠️ 重要提醒

### 关于Git历史

即使修改了代码，**旧的密码仍然在Git历史中**！

如果你确定这是生产环境密码，建议：

1. **修改数据库密码**（已完成步骤1）
2. **轮换JWT密钥**（所有用户需要重新登录）
3. **考虑清理Git历史**（如果需要彻底删除敏感信息）

清理Git历史（谨慎操作）：
```bash
# 这将重写Git历史，影响所有协作者
git filter-repo --path backend/app/core/config.py --invert-paths
```

或者更简单的方法：
1. 删除GitHub仓库
2. 创建新仓库
3. 推送修复后的代码

---

## 🔐 后续安全建议

1. **启用数据库IP白名单**：只允许应用服务器访问数据库
2. **使用密钥管理服务**：如腾讯云Secrets Manager
3. **定期轮换密钥**：建议每3个月更换一次
4. **启用数据库审计日志**：监控异常访问
5. **代码审查**：确保不再提交敏感信息

---

## 📋 检查清单

- [ ] 数据库密码已修改
- [ ] `.env` 文件已创建并配置
- [ ] 应用能正常启动
- [ ] `.env` 未被提交到Git（检查 `git status`）
- [ ] 修复代码已推送
- [ ] 考虑清理Git历史（可选）

---

## 🆘 遇到问题？

如果应用启动报错：
```
pydantic.error_wrappers.ValidationError: 1 validation error for Settings
DATABASE_URL
  field required (type=value_error.missing)
```

说明 `.env` 文件未正确加载，检查：
1. 文件是否在 `backend/` 目录下
2. 文件是否命名为 `.env`（不是 `env` 或 `.env.txt`）
3. 变量名是否正确

---

**修复完成时间**: 2026-02-23
