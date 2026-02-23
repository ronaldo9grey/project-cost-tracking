# 微信公众号绑定与配置指南

## 📋 概述

使用微信公众号（订阅号或服务号）实现：
1. **微信授权登录** - 用户关注公众号后可快捷登录
2. **模板消息推送** - 日报提醒、评价通知等推送到微信
3. **H5日报填报** - 通过公众号菜单进入日报页面

---

## 🎯 方案特点

| 特性 | 个人订阅号 | 企业服务号 |
|------|-----------|-----------|
| **申请门槛** | 个人身份证即可 | 需要企业营业执照 |
| **认证费用** | 免费 | 300元/年 |
| **模板消息** | ❌ 不支持 | ✅ 支持 |
| **客服消息** | ✅ 支持（48小时内） | ✅ 支持 |
| **网页授权** | ✅ 支持 | ✅ 支持 |
| **自定义菜单** | ✅ 支持 | ✅ 支持 |

**结论：** 如果只需要**登录和网页功能**，个人订阅号够用；如果需要**模板消息推送**，必须用服务号。

---

## 🔧 第一步：申请公众号

### 申请流程

1. 访问[微信公众平台](https://mp.weixin.qq.com)
2. 点击「立即注册」
3. 选择账号类型：
   - **订阅号** - 个人/媒体适用，每天可群发1次
   - **服务号** - 企业适用，每月可群发4次，支持模板消息
4. 填写邮箱激活账号
5. 选择主体类型：
   - 个人订阅号：选「个人」，填写身份证信息
   - 企业服务号：选「企业」，上传营业执照
6. 填写公众号信息（名称、简介等）
7. 等待审核（通常1-3个工作日）

### 获取必要信息

申请成功后，在「开发」→「基本配置」中获取：
- **AppID(应用ID)**
- **AppSecret(应用密钥)**（需要点击重置获取）

---

## 🔐 第二步：配置服务器

### 2.1 配置服务器域名

1. 登录公众号后台
2. 进入「设置与开发」→「公众号设置」→「功能设置」
3. 设置「JS接口安全域名」- 填写你的H5页面域名
4. 设置「网页授权域名」- 填写你的后端API域名

### 2.2 配置IP白名单

1. 进入「开发」→「基本配置」
2. 找到「IP白名单」，点击「查看」
3. 添加你的服务器公网IP

---

## 📝 第三步：申请模板消息（仅服务号）

**注意：个人订阅号不支持模板消息，只能用客服消息或短信替代**

### 申请流程

1. 进入「广告与服务」→「模板消息」
2. 点击「模板库」，搜索以下模板：

#### 模板1：日报填写提醒
- **搜索关键词**：提醒、任务、日报
- **推荐模板**：任务提醒
- **关键词**：收件人、提醒日期、提醒内容、来源

#### 模板2：评价结果通知
- **搜索关键词**：评价、审核、结果
- **推荐模板**：审核结果通知
- **关键词**：被评价人、评价人、评价等级、评价时间

#### 模板3：待办提醒
- **搜索关键词**：待办、提醒、待评价
- **推荐模板**：待办提醒
- **关键词**：审核人、提醒内容、提醒时间、备注

3. 点击「添加」，选择需要的字段
4. 记录每个模板的**模板ID**

---

## ⚙️ 第四步：后端配置

### 4.1 配置环境变量

编辑 `backend/.env`：

```bash
# 微信公众号配置
WECHAT_OFFICIAL_APP_ID=wx你的公众号APPID
WECHAT_OFFICIAL_APP_SECRET=你的APP_SECRET

# 网站域名（用于生成回调URL）
DOMAIN=https://your-domain.com
```

### 4.2 更新模板ID

编辑 `backend/app/services/wechat_official.py`：

```python
TEMPLATES = {
    'daily_report_reminder': {
        'id': '申请到的日报提醒模板ID',
        'url': '/mobile/daily-report.html'
    },
    'evaluation_notification': {
        'id': '申请到的评价通知模板ID',
        'url': '/mobile/index.html'
    },
    'pending_evaluation': {
        'id': '申请到的待评价提醒模板ID',
        'url': '/mobile/index.html'
    }
}
```

### 4.3 初始化服务

调用API初始化：

```bash
curl -X POST http://localhost:8000/api/v1/wechat-official/init \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "wx你的APPID",
    "app_secret": "你的APP_SECRET"
  }'
```

---

## 🔗 第五步：绑定流程

### 5.1 用户绑定微信公众号

#### 流程图
```
用户登录系统 → 个人中心 → 点击"绑定微信" 
    ↓
后端生成授权URL → 用户点击跳转微信授权页面
    ↓
用户点击"同意授权" → 微信重定向回H5页面
    ↓
H5页面获取code → 调用后端API完成绑定
    ↓
绑定成功，可接收模板消息
```

#### 具体步骤

**Step 1：生成授权URL**

```bash
curl -X GET "http://localhost:8000/api/v1/wechat-official/auth-url?\
redirect_uri=https://your-domain.com/mobile/callback.html&\
scope=snsapi_userinfo&\
state=bind_123"
```

返回：
```json
{
  "code": 200,
  "data": {
    "auth_url": "https://open.weixin.qq.com/..."
  }
}
```

**Step 2：前端跳转授权**

```javascript
// 打开授权页面
window.location.href = auth_url;
```

**Step 3：授权回调处理**

创建 `mobile/callback.html`：

```html
<script>
// 获取URL参数
const urlParams = new URLSearchParams(window.location.search);
const code = urlParams.get('code');
const state = urlParams.get('state');

// 调用后端处理
fetch('/api/v1/wechat-official/auth/callback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, state })
})
.then(res => res.json())
.then(data => {
    if (data.code === 200) {
        // 获取到openid，调用绑定API
        const openid = data.data.openid;
        return fetch('/api/v1/wechat-official/bind-openid', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            },
            body: JSON.stringify({ openid })
        });
    }
})
.then(() => {
    alert('微信绑定成功！');
    window.location.href = '/mobile/profile.html';
});
</script>
```

---

## 🧪 第六步：测试推送

绑定完成后，测试模板消息推送：

```bash
curl -X POST http://localhost:8000/api/v1/wechat-official/test/daily-report-reminder \
  -H "Authorization: Bearer 你的TOKEN"
```

如果成功，你会在微信收到一条消息，点击可进入日报填报页面。

---

## 📱 第七步：配置公众号菜单

在公众号后台添加菜单，方便用户进入日报系统：

1. 进入「内容与互动」→「自定义菜单」
2. 添加菜单项：

| 菜单名称 | 类型 | 内容 |
|---------|------|------|
| 📝 填写日报 | 跳转网页 | `https://your-domain.com/mobile/daily-report.html` |
| 📊 我的统计 | 跳转网页 | `https://your-domain.com/mobile/statistics.html` |
| 👤 个人中心 | 跳转网页 | `https://your-domain.com/mobile/profile.html` |

---

## 🔒 安全注意事项

### 1. HTTPS必需
微信公众号要求所有URL必须使用HTTPS

### 2. 域名备案
如果使用国内服务器，域名需要ICP备案

### 3. AppSecret保护
- 不要泄露AppSecret
- 不要在客户端代码中使用AppSecret
- 定期更换AppSecret

### 4. 授权scope选择
- `snsapi_base`：静默授权，只获取openid
- `snsapi_userinfo`：需要用户同意，可获取昵称头像

---

## ❓ 常见问题

### Q: 个人订阅号能用吗？
A: 可以，但**不支持模板消息推送**。可以：
- 使用客服消息（用户主动发消息后48小时内可回复）
- 改用短信推送
- 引导用户到H5页面查看通知

### Q: 用户收不到模板消息？
A: 检查以下几点：
1. 是否使用服务号（订阅号不支持）
2. 用户是否已关注公众号
3. 模板ID是否正确
4. 是否已绑定openid
5. 模板参数格式是否正确

### Q: 可以推送给未关注用户吗？
A: 不可以。用户必须关注公众号才能接收模板消息。

### Q: 授权页面显示"scope参数错误或没有scope权限"？
A: 检查：
1. 公众号是否已认证
2. scope拼写是否正确（snsapi_base或snsapi_userinfo）
3. 网页授权域名是否已配置

---

## 📚 相关文档

- [微信公众号开发文档](https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html)
- [微信网页授权文档](https://developers.weixin.qq.com/doc/offiaccount/OA_Web_Apps/Wechat_webpage_authorization.html)
- [模板消息文档](https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Template_Message_Interface.html)

---

## 🚀 快速开始清单

- [ ] 申请公众号（订阅号/服务号）
- [ ] 获取AppID和AppSecret
- [ ] 配置服务器域名和IP白名单
- [ ] 申请模板消息（服务号）
- [ ] 配置后端环境变量
- [ ] 部署H5页面
- [ ] 测试微信授权绑定
- [ ] 测试模板消息推送
- [ ] 配置公众号菜单
