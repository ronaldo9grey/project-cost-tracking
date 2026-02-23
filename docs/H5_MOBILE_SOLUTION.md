# H5移动端日报填报方案

## 📱 方案概述

使用 **H5响应式网页** 替代微信小程序，实现移动端日报填报功能。

### ✅ 优点
- **无需申请** - 不需要申请小程序、不需要企业资质
- **即开即用** - 浏览器直接访问，微信内也可以打开
- **开发简单** - 纯HTML/CSS/JS，无需学习小程序框架
- **推送灵活** - 支持公众号、短信、邮件等多种推送方式

---

## 📁 文件说明

### 移动端页面
- `frontend/mobile/daily-report.html` - 日报填报页面

### 功能特性
- ✅ 响应式设计，适配各种手机屏幕
- ✅ 日期选择、工作目标、关键进展填写
- ✅ 动态添加/删除工作事项
- ✅ 工时和状态记录
- ✅ 明日计划
- ✅ 自我评价（A/B/C/D等级）
- ✅ **AI智能生成日报**
- ✅ 保存草稿/提交
- ✅ 表单验证
- ✅ 加载动画和Toast提示

---

## 🚀 部署方式

### 方式一：部署到现有前端项目

将 `daily-report.html` 复制到前端项目的 `public` 或 `static` 目录：

```bash
# Vue项目示例
cp frontend/mobile/daily-report.html frontend/public/mobile/

# 然后在前端添加入口链接
# 在首页或个人中心添加：
# <a href="/mobile/daily-report.html">📱 手机填报日报</a>
```

### 方式二：独立部署

使用 Nginx 或任何静态文件服务器：

```nginx
server {
    listen 80;
    server_name mobile.your-domain.com;
    
    location / {
        root /path/to/project-cost-tracking/frontend/mobile;
        index daily-report.html;
    }
}
```

### 方式三：内嵌到现有Web页面

使用 iframe 嵌入：

```html
<iframe src="/mobile/daily-report.html" 
        style="width: 100%; height: 100vh; border: none;">
</iframe>
```

---

## 🔗 访问方式

### 方式1：直接链接
用户通过手机浏览器访问：
```
https://your-domain.com/mobile/daily-report.html
```

### 方式2：扫码访问
生成二维码，用户扫码进入：
```bash
# 使用qrcode工具生成
npm install -g qrcode
qrcode -o daily-report.png "https://your-domain.com/mobile/daily-report.html"
```

### 方式3：微信收藏/浮窗
- 在微信中打开链接
- 点击右上角「...」→「收藏」或「浮窗」
- 以后从收藏或浮窗快速进入

### 方式4：添加到桌面
**iOS Safari：**
1. 打开网页
2. 点击底部分享按钮
3. 选择「添加到主屏幕」

**Android Chrome：**
1. 打开网页
2. 点击菜单 → 「添加到主屏幕」

---

## 📲 消息推送方案

由于不使用小程序，推送有以下几种替代方案：

### 方案A：微信公众号模板消息（推荐）

**前提：** 申请微信公众号（订阅号或服务号）

**步骤：**
1. 申请公众号并认证
2. 在公众号后台申请模板消息
3. 用户关注公众号后绑定账号
4. 通过公众号API推送消息

**优点：**
- 免费
- 用户点击消息直接进入H5页面
- 微信官方推送渠道

### 方案B：短信提醒

**使用阿里云/腾讯云短信服务**

```python
# 后端代码示例
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

def send_sms_reminder(phone, template_code, params):
    client = AcsClient('access_key', 'access_secret', 'cn-hangzhou')
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')
    
    request.add_query_param('PhoneNumbers', phone)
    request.add_query_param('SignName', '你的签名')
    request.add_query_param('TemplateCode', template_code)
    request.add_query_param('TemplateParam', json.dumps(params))
    
    response = client.do_action_with_exception(request)
    return response
```

**优点：**
- 到达率高
- 不需要安装任何APP
- 任何手机都能收到

**缺点：**
- 需要付费（约0.05元/条）

### 方案C：邮件提醒

**免费方案，适合内部系统**

```python
import smtplib
from email.mime.text import MIMEText

def send_email_reminder(to_email, subject, content):
    msg = MIMEText(content, 'html', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = 'system@your-domain.com'
    msg['To'] = to_email
    
    server = smtplib.SMTP('smtp.your-domain.com', 587)
    server.login('username', 'password')
    server.sendmail(msg['From'], [to_email], msg.as_string())
    server.quit()
```

### 方案D：飞书/钉钉机器人

如果团队使用飞书或钉钉：

**飞书机器人推送：**
```python
import requests

def send_feishu_reminder(webhook_url, content):
    payload = {
        "msg_type": "text",
        "content": {
            "text": content
        }
    }
    requests.post(webhook_url, json=payload)
```

---

## 🔐 安全考虑

### Token存储
H5页面使用 `localStorage` 存储登录Token：

```javascript
// 登录成功后
localStorage.setItem('token', 'your-jwt-token');

// 发送请求时
fetch('/api/xxx', {
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
});
```

### HTTPS必需
- 生产环境必须使用HTTPS
- 否则微信浏览器会拦截

### Token过期处理
```javascript
// 在API响应中处理401
if (response.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login.html';
}
```

---

## 📊 与小程序对比

| 功能 | H5网页 | 微信小程序 |
|------|--------|-----------|
| **申请门槛** | 无需申请 | 需要企业资质 |
| **开发成本** | 低 | 中等 |
| **用户体验** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **推送能力** | 公众号/短信/邮件 | 订阅消息 |
| **离线访问** | ❌ | ✅ |
| **性能** | 中等 | 优秀 |
| **分享传播** | 链接/二维码 | 卡片分享 |

---

## 🎯 推荐使用场景

### 使用H5方案
- 快速上线，不想申请小程序
- 内部系统，用户量不大
- 已有公众号，想用模板消息
- 预算有限，不想付小程序认证费

### 使用小程序方案
- 需要最佳用户体验
- 需要推送消息到微信
- 需要分享传播
- 长期使用，值得投入

---

## 📝 后续优化建议

1. **添加PWA支持** - 支持离线缓存、添加到桌面
2. **优化首屏加载** - 代码分割、懒加载
3. **添加骨架屏** - 提升感知性能
4. **支持图片上传** - 工作成果拍照上传
5. **语音输入** - 支持语音转文字填日报

---

## ❓ 常见问题

### Q: H5页面在微信里打不开？
A: 检查是否使用了HTTPS，微信强制要求HTTPS

### Q: 如何获取用户微信信息？
A: H5只能通过微信授权登录获取，需要接入微信OAuth

### Q: 推送消息有免费方案吗？
A: 公众号模板消息免费，但需要申请公众号

### Q: 能否做到像小程序一样的体验？
A: 使用PWA技术可以做到接近小程序的体验，包括添加到桌面、离线访问等
