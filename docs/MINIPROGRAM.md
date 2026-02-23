# 微信小程序使用文档

## 项目概述

项目成本跟踪系统微信小程序，提供移动端日报快捷填报、查看、评价等功能。

## 目录结构

```
miniprogram/
├── pages/                    # 页面目录
│   ├── index/               # 首页
│   ├── daily-report/        # 日报填报
│   ├── statistics/          # 统计页面
│   └── profile/             # 个人中心
├── components/              # 组件目录
├── utils/                   # 工具函数
│   └── api.js              # API接口封装
├── assets/                  # 静态资源
├── app.js                  # 应用入口
├── app.json                # 应用配置
├── app.wxss                # 全局样式
└── project.config.json     # 项目配置
```

## 页面说明

### 1. 首页 (pages/index)

**功能**：
- 显示用户欢迎信息
- 快速统计（今日日报状态、待评价数量、本月提交数）
- 快速操作入口（快速填报、AI生成、查看日报、待评价）
- 最近日报列表

**截图**：
- 顶部蓝色渐变卡片显示问候语和日期
- 四个快捷功能按钮
- 最近日报列表卡片

### 2. 日报填报 (pages/daily-report)

**功能**：
- 日期选择
- 工作目标填写
- 关键进展填写
- 工作事项管理（添加/删除）
- 明日计划
- 自我评价选择
- AI辅助生成

**特色**：
- 支持AI自动生成日报
- 表单验证
- 草稿保存

### 3. 统计页面 (pages/statistics)

**功能**：
- 工作量趋势图表
- 日报提交统计
- 评价等级分布

### 4. 个人中心 (pages/profile)

**功能**：
- 用户信息展示
- 通知设置
- 企业微信绑定
- 关于页面

## API接口

小程序通过 `utils/api.js` 封装了与后端API的通信：

### 认证相关
- `login(code)` - 微信登录
- `getUserInfo()` - 获取用户信息
- `checkLogin()` - 检查登录状态

### 日报相关
- `getTodayReport()` - 获取今日日报
- `getReportList(params)` - 获取日报列表
- `submitReport(data)` - 提交日报
- `updateReport(id, data)` - 更新日报
- `generateAIReport(data)` - AI生成日报
- `quickGenerateReport()` - 快速生成日报

### 评价相关
- `getPendingEvaluations()` - 获取待评价列表
- `submitEvaluation(data)` - 提交评价

### 统计相关
- `getStatistics()` - 获取统计数据
- `getWorkloadTrend(days)` - 获取工作量趋势

### 通知相关
- `getNotificationSettings()` - 获取通知设置
- `updateNotificationSettings(data)` - 更新通知设置
- `bindWechatId(wechatUserId)` - 绑定企业微信ID

## 使用流程

### 1. 首次使用

1. 打开小程序
2. 点击登录，授权微信登录
3. 绑定企业微信ID（用于接收通知）
4. 完善个人信息

### 2. 填写日报

**方式一：手动填写**
1. 点击底部「日报」Tab
2. 填写工作目标、关键进展
3. 添加工作事项
4. 填写明日计划
5. 选择自我评价
6. 点击提交

**方式二：AI生成**
1. 点击「AI生成」按钮
2. 简要描述工作内容
3. AI自动生成完整日报
4. 根据需要修改
5. 提交日报

### 3. 查看统计

1. 点击「统计」Tab
2. 查看工作量趋势
3. 查看日报提交情况

## 开发配置

### 1. 修改API地址

在 `app.js` 中修改 `apiBaseUrl`：

```javascript
globalData: {
  apiBaseUrl: 'https://your-api-domain.com/api/v1',
  // ...
}
```

### 2. 配置小程序AppID

在 `project.config.json` 中修改：

```json
{
  "appid": "wxYOUR_APPID_HERE"
}
```

### 3. 配置服务器域名

在微信公众平台配置合法域名：
- request合法域名：`https://your-api-domain.com`
- uploadFile合法域名（如有文件上传）
- downloadFile合法域名（如有文件下载）

## 部署步骤

### 1. 开发者工具导入

1. 下载安装[微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 选择「导入项目」
3. 选择 `miniprogram` 目录
4. 填写AppID（测试可使用测试号）
5. 点击确定导入

### 2. 开发调试

1. 修改 `utils/api.js` 中的 `BASE_URL` 为本地或测试服务器地址
2. 开启「不校验合法域名」选项（开发阶段）
3. 进行开发和调试

### 3. 上传发布

1. 代码开发完成后，点击「上传」
2. 填写版本号和项目备注
3. 登录微信公众平台
4. 进入「版本管理」
5. 将开发版本提交审核
6. 审核通过后发布

## 注意事项

1. **HTTPS要求**：生产环境必须使用HTTPS
2. **域名配置**：所有API域名必须在微信公众平台配置
3. **登录授权**：微信登录需要用户授权
4. **存储限制**：本地存储有大小限制，重要数据应存服务器
5. **性能优化**：图片懒加载、列表分页、减少setData调用

## 常见问题

### Q: 请求失败，提示域名不合法？
A: 在开发者工具中勾选「详情」→「本地设置」→「不校验合法域名」，或在微信公众平台配置合法域名。

### Q: 登录失败？
A: 检查后端登录接口是否正常，AppID和AppSecret是否正确配置。

### Q: AI生成日报失败？
A: 检查Moonshot API密钥是否正确配置，API调用额度是否充足。

### Q: 如何调试？
A: 使用微信开发者工具的调试功能，查看Console日志，使用Network面板查看请求。

## 更新日志

### v1.0.0 (2026-02-23)
- ✅ 基础功能完成
- ✅ 日报填报
- ✅ AI生成日报
- ✅ 数据统计
- ✅ 个人中心
- ✅ 企业微信通知绑定
