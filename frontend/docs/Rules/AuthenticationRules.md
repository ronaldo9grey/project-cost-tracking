# 身份认证开发规则

## 🔒 核心原则

### 1. 禁止硬编码用户信息
```javascript
// ❌ 绝对禁止
const userInfo = {
  id: '1', // 硬编码
  username: 'admin'
}

// ✅ 正确做法
const userInfo = {
  id: userInfoResponse.id.toString(), // 从后端获取
  username: userInfoResponse.username
}
```

### 2. 统一API URL格式
```javascript
// ❌ 禁止使用末尾斜杠
/api/v1/daily-report/legacy/my-reports/10/ // 401错误

// ✅ 统一使用无斜杠
/api/v1/daily-report/legacy/my-reports/10 // 200成功
```

### 3. JWT Token验证标准
- JWT sub字段必须与登录用户名一致
- 前端必须从后端API获取真实用户信息
- 避免localStorage硬编码用户数据

## 🚀 开发流程

### 新功能开发检查清单
1. [ ] 检查是否存在用户信息硬编码
2. [ ] 验证API URL格式一致性
3. [ ] 确认JWT token生成正确
4. [ ] 测试不同用户登录流程
5. [ ] 验证权限验证逻辑

### 认证相关文件清单
- `src/views/Login/index.vue` - 登录组件
- `src/api/Auth.ts` - 认证API
- `src/api/unifiedApi.ts` - HTTP拦截器
- `src/views/DailyReportEdit/RefactoredDailyReportEdit.vue` - 编辑页面

## 🔧 问题解决模板

### 问题现象记录格式
```markdown
## 问题现象
- 具体错误信息
- 影响的用户功能
- 复现步骤

## 诊断过程
1. 步骤1
2. 步骤2
3. 步骤3

## 解决方案
1. 修复方案1
2. 修复方案2

## 验证结果
- 测试结果
- 修复确认
```

## 📚 知识库位置
- 完整文档：`docs/KnowledgeBase/AuthenticationIssues.md`
- 调试工具：`docs/Tools/`
- 最佳实践：`docs/BestPractices/`

## ⚡ 快速解决方案

### 当遇到401认证错误时
1. 检查JWT token内容
2. 验证用户信息一致性
3. 测试API URL格式
4. 确认权限验证逻辑

### 当遇到用户信息错误时
1. 检查硬编码问题
2. 验证后端API响应
3. 确认登录流程
4. 检查localStorage数据

---
**最后更新**: 2026-01-15
**状态**: 活跃规则
**适用**: 所有身份认证相关开发
