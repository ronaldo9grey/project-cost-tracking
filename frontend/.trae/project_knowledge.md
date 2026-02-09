# 项目核心知识库

## 🚨 身份认证问题（已彻底解决）

### 问题描述
- **阶段1**: 编辑页面出现401认证错误："身份验证失效，请重新登录"
- **阶段2**: JWT token与用户映射混乱（EMP001登录显示0001）
- **阶段3**: API URL格式问题（末尾斜杠导致401错误）
- **阶段4**: 后端权限验证不一致导致403错误

### 根本原因
1. **前端硬编码用户信息** - 总是显示admin用户
2. **API URL格式不一致** - 末尾斜杠导致401错误
3. **后端权限验证逻辑不一致** - POST/DELETE使用错误字段比较
4. **用户-日报权限映射问题** - 权限验证逻辑bug

### 解决方案记录
- **文件**: `docs/KnowledgeBase/AuthenticationIssues.md`
- **规则**: `docs/Rules/AuthenticationRules.md`
- **状态**: 已彻底解决，所有问题已修复

### 关键修复
1. **前端硬编码用户信息** - 修复登录组件，使用后端API获取真实用户信息
2. **API URL格式不一致** - 移除API URL末尾斜杠，从 `/reports/10/` 改为 `/reports/10`
3. **后端权限验证逻辑不一致** - 修复POST/DELETE中的权限验证，使用`employee_id`而不是`id`
4. **优化HTTP拦截器** - 简化逻辑避免干扰

## 📚 知识库结构

```
docs/
├── README.md - 项目文档入口
├── Rules/
│   └── AuthenticationRules.md - 身份认证开发规则
├── KnowledgeBase/
│   └── AuthenticationIssues.md - 身份认证问题解决方案
└── Tools/ - 调试和测试工具
```

## 🔑 身份认证关键规则

### 禁止事项
- ❌ 硬编码用户信息（如 `id: '1'`）
- ❌ 不一致的API URL格式（有/无末尾斜杠）
- ❌ 绕过认证机制进行调试
- ❌ 后端权限验证逻辑不一致

### 必须遵循
- ✅ 使用后端API获取真实用户信息
- ✅ 统一API URL格式（无末尾斜杠）
- ✅ 验证JWT token内容正确性
- ✅ 保持前端-后端用户信息一致性
- ✅ 统一权限验证逻辑（使用employee_id字段）

## 🛠️ 调试工具

### 用户数据分析
```javascript
// 检查用户信息和JWT token
debugUserData()
```

### API端点测试
```javascript
// 测试不同API调用格式
testApiEndpoints()
```

## 🚀 快速解决方案

### 当遇到401认证错误时
1. 运行 `debugUserData()` 检查用户信息一致性
2. 运行 `testApiEndpoints()` 验证API URL格式
3. 检查是否有硬编码用户信息
4. 确认JWT token与登录用户匹配

### 编辑页面问题
- 检查URL格式：使用 `/reports/10` 而不是 `/reports/10/`
- 验证权限验证：确认日报属于当前用户
- 测试token状态：确保token在页面跳转时有效

## 📝 重要提醒

这个身份认证问题在2026-01-15被彻底解决，所有修复已应用到代码中。在未来的开发中：
1. 严格遵循认证规则
2. 使用提供的调试工具
3. 定期更新知识库文档
4. 对新功能进行认证测试

**知识库位置**: `docs/KnowledgeBase/AuthenticationIssues.md`
**开发规则**: `docs/Rules/AuthenticationRules.md`
**文档入口**: `docs/README.md`
