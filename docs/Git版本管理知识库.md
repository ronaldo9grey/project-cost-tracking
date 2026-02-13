# 项目成本跟踪系统 - Git版本管理知识库

## 📋 概述

本文档记录了项目成本跟踪系统的完整版本管理解决方案，涵盖了从初始设置到日常开发的所有必要信息。

## 🎯 项目信息

- **项目名称**: project-cost-tracking
- **项目描述**: 项目成本跟踪系统 - 支持项目管理、成本分析、资源管理和供应商管理
- **仓库地址**: https://github.com/ronaldo9grey/project-cost-tracking
- **技术栈**: Python FastAPI + Vue 3 + PostgreSQL + Docker
- **部署环境**: 腾讯云

## 🏗️ 项目结构

```
project-cost-tracking/
├── README.md                    # 项目说明文档
├── .gitignore                   # Git忽略规则
├── docker-compose.yml          # Docker部署配置
├── deploy.sh                   # 部署脚本
├── backend/                    # 后端代码
│   ├── app/                   # FastAPI应用
│   │   ├── api/               # API路由
│   │   ├── core/              # 核心配置
│   │   ├── crud/              # 数据库操作
│   │   ├── models/             # 数据模型
│   │   └── schemas/            # Pydantic模式
│   ├── requirements.txt        # Python依赖
│   └── Dockerfile             # 后端容器配置
├── frontend/                   # 前端代码
│   ├── src/                   # Vue 3源代码
│   ├── package.json           # Node.js依赖
│   └── Dockerfile             # 前端容器配置
└── docs/                      # 项目文档
    └── Git版本管理知识库.md   # 本文档
```

## 🔧 Git仓库初始化

### 初始化命令
```bash
# 1. 进入项目目录
cd F:\myPro\projectA1127\projectA\web_project

# 2. 初始化Git仓库
git init

# 3. 创建主分支
git checkout -b main

# 4. 添加远程仓库
git remote add origin https://github.com/ronaldo9grey/project-cost-tracking.git

# 5. 初始提交
git add .
git commit -m "feat: initial project setup"
git push -u origin main
```

### .gitignore配置要点
- **Python**: 排除`__pycache__/`, `*.pyc`, 虚拟环境等
- **Node.js**: 排除`node_modules/`, `npm-debug.log*`等
- **前端构建**: 排除`frontend/dist/`, `*.local`等
- **环境变量**: 排除`.env`, `.env.*`文件
- **数据库**: 排除`*.db`, `*.sqlite`等
- **上传文件**: 排除`uploads/`目录
- **临时文件**: 排除调试和测试文件

## 🌐 远程仓库配置

### 主要仓库
- **平台**: GitHub
- **地址**: https://github.com/ronaldo9grey/project-cost-tracking
- **类型**: Private（私有仓库）
- **默认分支**: main

### 备份策略
推荐使用腾讯云Git作为备份仓库：
```bash
git remote add backup https://git.code.tencent.com/your-team/project-cost-tracking.git
git push -u backup main
```

## 🔄 分支管理策略

### GitFlow工作流

#### 主要分支
- **main**: 生产环境代码，只接受来自release和hotfix的合并
- **develop**: 开发主分支，包含最新开发功能

#### 支持分支
- **feature/**: 功能开发分支
  ```bash
  git checkout -b feature/user-management
  git checkout -b feature/cost-analysis-module
  git checkout -b feature/supplier-evaluation
  ```
- **release/**: 发布准备分支
  ```bash
  git checkout -b release/v1.2.0
  ```
- **hotfix/**: 紧急修复分支
  ```bash
  git checkout -b hotfix/login-security-issue
  ```

## 📝 提交信息规范

### Conventional Commits规范
```bash
# 格式
<type>[optional scope]: <description>

# 类型
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建过程或辅助工具的变动

# 示例
feat(auth): add JWT token refresh mechanism
fix(api): resolve database connection timeout issue
docs(readme): update deployment instructions
style(frontend): improve button hover effects
refactor(backend): optimize cost calculation logic
test(frontend): add component unit tests
chore(deps): update vue-tsc to v2.0.6
```

## 🚀 日常开发工作流

### 功能开发流程
```bash
# 1. 从main分支创建功能分支
git checkout main
git pull origin main
git checkout -b feature/new-functionality

# 2. 开发工作
# ... 进行代码修改 ...

# 3. 提交更改
git add .
git commit -m "feat: add new functionality description"

# 4. 推送分支
git push origin feature/new-functionality

# 5. 创建Pull Request到main分支
# 6. 代码审查通过后合并
```

### 快速开发流程（个人项目）
```bash
# 直接在main分支开发
git add .
git commit -m "feat: add new feature"
git push origin main
```

### 版本发布流程
```bash
# 1. 创建release分支
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# 2. 版本号更新、文档完善
# 3. 测试完成后合并
git checkout main
git merge release/v1.2.0
git tag v1.2.0
git push origin main --tags
```

## 🔐 安全配置

### 分支保护规则
- 保护main分支
- 强制Pull Request审查
- 要求状态检查通过

### 访问控制
- 私有仓库设置
- 定期审查团队成员权限
- 使用环境变量存储敏感信息

## 📱 多设备协作

### 克隆到其他设备
```bash
# 克隆仓库
git clone https://github.com/ronaldo9grey/project-cost-tracking.git
cd project-cost-tracking

# 设置分支跟踪
git checkout -b main
git branch --set-upstream-to=origin/main main
```

### 同步更新
```bash
# 拉取最新代码
git pull origin main

# 如果有冲突，解决冲突后
git add .
git commit -m "resolve merge conflicts"
git push origin main
```

## 🛠️ 故障排除

### 常见问题解决

#### 1. 推送被拒绝
```bash
# 强制推送（谨慎使用）
git push -f origin main

# 或者先拉取再推送
git pull origin main
git push origin main
```

#### 2. 合并冲突
```bash
# 查看冲突文件
git status

# 手动解决冲突后
git add .
git commit -m "resolve merge conflicts"
git push origin main
```

#### 3. 恢复误删文件
```bash
# 查看删除历史
git log --diff-filter=D --summary

# 恢复特定文件
git checkout <commit>~1 <deleted_file>
```

## 📚 相关资源

### 官方文档
- [Git官方文档](https://git-scm.com/docs)
- [GitHub官方文档](https://docs.github.com)
- [Conventional Commits](https://www.conventionalcommits.org/)

### 推荐工具
- **Git客户端**: Git for Windows, SourceTree, GitHub Desktop
- **编辑器**: VS Code + Git插件
- **图形化工具**: GitKraken, SmartGit

### 学习资源
- [Git学习指南](https://git-scm.com/book/zh/v2)
- [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)

## 📊 项目统计

- **代码行数**: 76,663行
- **文件数量**: 265个
- **提交记录**: 2个
- **仓库大小**: 1.80 MiB

---

**最后更新**: 2025年2月9日
**版本**: v1.0.0
**维护者**: 项目开发团队