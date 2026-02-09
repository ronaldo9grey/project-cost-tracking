# 项目成本跟踪系统

## 项目简介

项目成本跟踪系统是一个用于管理和跟踪项目成本的Web应用，支持项目管理、成本分析、资源管理和供应商管理等功能。

## 技术栈

### 后端
- Python 3.13
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT (JSON Web Token) 认证

### 前端
- Vue 3
- TypeScript
- Element Plus
- ECharts
- Axios

## 项目结构

```
web_project/
├── backend/                  # 后端代码
│   ├── app/                 # 应用主目录
│   │   ├── api/             # API路由
│   │   │   ├── endpoints/   # API端点
│   │   │   └── v1/           # API版本1
│   │   ├── core/            # 核心配置
│   │   ├── crud/            # CRUD操作
│   │   ├── models/          # 数据库模型
│   │   └── schemas/         # Pydantic模式
│   ├── .env                 # 环境变量配置
│   ├── requirements.txt      # 依赖列表
│   └── project_cost_tracking.db  # SQLite数据库（开发环境）
├── frontend/                 # 前端代码
│   ├── src/                 # 源代码
│   │   ├── api/             # API请求
│   │   ├── router/           # 路由配置
│   │   ├── views/            # 页面组件
│   │   ├── App.vue          # 根组件
│   │   └── main.ts           # 入口文件
│   ├── index.html           # HTML模板
│   ├── package.json         # 依赖配置
│   └── vite.config.ts       # Vite配置
└── info/                    # 项目信息
    └── tables.sql           # 数据库表结构
```

## 后端配置和运行

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制`.env`文件并修改相应配置：

```bash
cp .env.example .env
```

### 3. 初始化数据库

```bash
# 创建数据库表
python -m app.core.database
```

### 4. 运行后端服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 前端配置和运行

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 运行开发服务器

```bash
npm run dev
```

### 3. 构建生产版本

```bash
npm run build
```

### 4. 预览生产版本

```bash
npm run preview
```

## 主要功能模块

### 1. 项目管理
- 项目创建、编辑、删除
- 项目状态跟踪
- 项目进度管理
- 项目任务管理

### 2. 成本分析
- 项目成本汇总
- 成本趋势分析
- 预算与实际成本对比
- 成本类型分析（材料、人力、外包、间接成本）

### 3. 资源管理
- 人员管理
- 材料管理
- 设备管理
- 成本类型配置

### 4. 供应商管理
- 供应商信息管理
- 供应商绩效分析
- 供应商评估

### 5. 统计报表
- 项目概览统计
- 成本分布统计
- 进度分布统计

## API文档

### 认证
- POST `/api/v1/auth/login` - 用户登录
- POST `/api/v1/auth/refresh` - 刷新令牌
- POST `/api/v1/auth/change-password` - 修改密码

### 项目管理
- GET `/api/v1/projects` - 获取项目列表
- POST `/api/v1/projects` - 创建项目
- GET `/api/v1/projects/{project_id}` - 获取项目详情
- PUT `/api/v1/projects/{project_id}` - 更新项目
- DELETE `/api/v1/projects/{project_id}` - 删除项目

### 成本分析
- GET `/api/v1/cost/statistics` - 获取成本统计
- GET `/api/v1/projects/{project_id}/costs` - 获取项目成本汇总

### 资源管理
- GET `/api/v1/resource/personnel` - 获取人员列表
- GET `/api/v1/resource/materials` - 获取材料列表
- GET `/api/v1/resource/equipment` - 获取设备列表

## 开发和测试

### 后端测试

```bash
# 运行单元测试
python -m pytest
```

### 前端测试

```bash
# 运行单元测试
npm run test:unit

# 运行端到端测试
npm run test:e2e
```

## 部署说明

### 后端部署

1. 使用Gunicorn作为WSGI服务器：

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

2. 使用Nginx作为反向代理：

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 前端部署

1. 构建生产版本：

```bash
npm run build
```

2. 将构建产物部署到Nginx或其他Web服务器：

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        root /path/to/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

## 版本管理

### Git工作流

本项目采用GitFlow分支管理策略：

- **main分支**: 生产环境代码
- **develop分支**: 开发主分支
- **feature/*分支**: 功能开发分支
- **release/*分支**: 发布准备分支
- **hotfix/*分支**: 紧急修复分支

### 分支命名规范

```bash
# 功能开发
feature/user-management
feature/cost-analysis-module
feature/supplier-evaluation

# 发布版本
release/v1.2.0

# 紧急修复
hotfix/login-security-issue
```

### 提交信息规范

使用[Conventional Commits](https://www.conventionalcommits.org/)规范：

```bash
feat(auth): add JWT token refresh mechanism
fix(api): resolve database connection timeout issue
docs(readme): update deployment instructions
style(frontend): improve button hover effects
refactor(backend): optimize cost calculation logic
test(frontend): add component unit tests
chore(deps): update vue-tsc to v2.0.6
```

### 本地开发流程

```bash
# 1. 克隆仓库
git clone <repository-url>
cd web_project

# 2. 创建功能分支
git checkout -b feature/your-feature-name

# 3. 开发完成后提交
git add .
git commit -m "feat: add new functionality description"

# 4. 推送分支
git push origin feature/your-feature-name

# 5. 创建Pull Request
```

### 代码审查要求

- 所有功能开发必须通过Pull Request
- 需要至少1个审查者
- 必须通过CI/CD检查
- 遵循代码规范和最佳实践

## 部署和发布

### 环境变量配置

生产环境变量存储在腾讯云密钥管理服务中：
- 数据库连接信息
- JWT密钥
- API配置参数

### CI/CD流水线

使用GitHub Actions进行自动化部署：

1. **代码推送**到main分支
2. **自动测试**后端和前端
3. **构建生产版本**
4. **部署到腾讯云**

### 版本发布流程

```bash
# 1. 创建release分支
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# 2. 版本号更新和文档完善
# 3. 测试完成后合并
git checkout main
git merge release/v1.2.0
git tag v1.2.0
git push origin main --tags
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

### 贡献者指南

1. Fork本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 联系方式

如有问题，请联系项目负责人。

---

**最后更新**: 2025年2月9日