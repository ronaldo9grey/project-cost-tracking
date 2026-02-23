# 微信通知系统文档

## 功能概述

企业微信通知系统支持将日报相关提醒、评价通知等推送到用户个人微信，实现实时消息提醒。

## 前置条件

### 1. 企业微信配置

需要先在[企业微信管理后台](https://work.weixin.qq.com/wework_admin)创建应用：

1. 登录企业微信管理后台
2. 进入「应用管理」→「自建」→「创建应用」
3. 填写应用信息：
   - 应用名称：项目管理系统
   - 应用头像：上传应用图标
   - 可见成员：选择可见范围
4. 获取应用凭证：
   - `AgentId`：应用ID
   - `Secret`：应用凭证密钥

### 2. 获取企业ID

在「我的企业」页面底部找到 `CorpID`

### 3. 配置可信域名

在应用详情页设置「可信域名」，确保能正常接收消息

## API接口

### 1. 初始化微信服务

**接口**: `POST /api/v1/notifications/wechat/init`

**请求参数**:
```json
{
  "corp_id": "wwxxxxxxxxxxxxxxxx",
  "corp_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "agent_id": "1000002"
}
```

**返回结果**:
```json
{
  "code": 200,
  "message": "企业微信通知服务初始化成功",
  "data": null
}
```

### 2. 发送自定义消息

**接口**: `POST /api/v1/notifications/wechat/send`

**请求参数**:
```json
{
  "user_id": "ZhangSan",
  "message_type": "textcard",
  "title": "日报提醒",
  "content": "请尽快填写今日日报",
  "url": "https://your-system.com/daily-report"
}
```

### 3. 获取通知设置

**接口**: `GET /api/v1/notifications/settings`

**返回结果**:
```json
{
  "code": 200,
  "message": "获取通知设置成功",
  "data": {
    "daily_report_reminder": true,
    "evaluation_notification": true,
    "pending_evaluation_reminder": true,
    "reminder_time": "18:00",
    "wechat_user_id": "ZhangSan"
  }
}
```

### 4. 更新通知设置

**接口**: `PUT /api/v1/notifications/settings`

**请求参数**:
```json
{
  "daily_report_reminder": true,
  "evaluation_notification": true,
  "pending_evaluation_reminder": true,
  "reminder_time": "18:00"
}
```

### 5. 绑定企业微信ID

**接口**: `POST /api/v1/notifications/settings/wechat-user-id`

**请求参数**:
```json
{
  "wechat_user_id": "ZhangSan"
}
```

### 6. 测试日报提醒

**接口**: `POST /api/v1/notifications/test/daily-report-reminder`

发送测试消息到当前用户的企业微信。

## 通知类型

### 1. 日报填写提醒

**触发时间**: 每天18:00（可配置）

**推送对象**: 当天未填写日报的用户

**消息格式**:
```
标题：⏰ 日报填写提醒
内容：您好，张三！请尽快填写 2026-02-23 的工作日报。
```

### 2. 评价通知

**触发时机**: 日报被评价后

**推送对象**: 被评价人

**消息格式**:
```
标题：⭐ 日报评价通知
内容：您的日报已被 李四 评价
评价等级：B (按目标达成)
评语：工作完成情况良好...
```

### 3. 待评价提醒

**触发时间**: 每天10:00

**推送对象**: 有待评价日报的管理者

**消息格式**:
```
标题：📋 待评价提醒
内容：您有 3 份日报待评价
请及时完成评价工作。
```

## 环境变量配置

在 `.env` 文件中添加：

```bash
# 企业微信配置
WECHAT_CORP_ID=wwxxxxxxxxxxxxxxxx
WECHAT_CORP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WECHAT_AGENT_ID=1000002
```

## 前端集成

### 1. 通知设置页面

```vue
<template>
  <div class="notification-settings">
    <el-card>
      <template #header>
        <span>通知设置</span>
      </template>
      
      <el-form :model="settings" label-width="150px">
        <el-form-item label="企业微信ID">
          <el-input v-model="settings.wechat_user_id" placeholder="请输入企业微信ID">
            <template #append>
              <el-button @click="saveWechatId">保存</el-button>
            </template>
          </el-input>
          <div class="tip">在企业微信「我」→「个人信息」中查看</div>
        </el-form-item>
        
        <el-form-item label="日报填写提醒">
          <el-switch v-model="settings.daily_report_reminder" />
        </el-form-item>
        
        <el-form-item label="评价通知">
          <el-switch v-model="settings.evaluation_notification" />
        </el-form-item>
        
        <el-form-item label="提醒时间">
          <el-time-picker
            v-model="settings.reminder_time"
            format="HH:mm"
            placeholder="选择时间"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="saveSettings">保存设置</el-button>
          <el-button @click="testNotification">测试通知</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>
```

### 2. 消息通知组件

```vue
<template>
  <div class="notification-badge">
    <el-badge :value="unreadCount" :max="99">
      <el-icon><Bell /></el-icon>
    </el-badge>
    
    <el-dropdown @command="handleCommand">
      <span class="el-dropdown-link">
        消息<i class="el-icon-arrow-down el-icon--right"></i>
      </span>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item v-for="msg in notifications" :key="msg.id">
            <div :class="{ unread: !msg.is_read }">
              <p>{{ msg.title }}</p>
              <small>{{ msg.created_at }}</small>
            </div>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>
```

## 定时任务配置

使用 cron 配置定时任务发送提醒：

```bash
# 编辑 crontab
crontab -e

# 日报提醒（每天18:00）
0 18 * * * cd /path/to/project && python scripts/send_daily_reminder.py

# 待评价提醒（每天10:00）
0 10 * * * cd /path/to/project && python scripts/send_evaluation_reminder.py
```

或使用 APScheduler：

```python
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.wechat_notification import get_wechat_service

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', hour=18, minute=0)
def daily_report_reminder():
    """日报填写提醒"""
    service = get_wechat_service()
    if service:
        # 查询未填写日报的用户并发送提醒
        pass

@scheduler.scheduled_job('cron', hour=10, minute=0)
def pending_evaluation_reminder():
    """待评价提醒"""
    service = get_wechat_service()
    if service:
        # 查询有待评价日报的管理者并发送提醒
        pass

scheduler.start()
```

## 注意事项

1. **用户绑定**: 需要用户手动绑定企业微信ID才能接收通知
2. **消息频率**: 注意控制消息发送频率，避免打扰用户
3. **失败重试**: 发送失败的消息需要记录并支持重试
4. **隐私保护**: 消息内容避免包含敏感信息
5. **测试环境**: 建议先在测试环境验证后再上线

## 故障排查

### 1. 发送消息失败

- 检查 corp_id, corp_secret, agent_id 是否正确
- 确认应用可见范围包含接收人
- 检查 access_token 是否过期

### 2. 用户收不到消息

- 确认用户已关注企业微信应用
- 检查用户的企业微信ID是否正确
- 确认用户在企业微信可见范围内

### 3. API调用限制

企业微信API有调用频率限制：
- 每应用每企业最多20次/秒
- 超出限制会被拦截，请控制调用频率
