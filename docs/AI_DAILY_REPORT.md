# AI日报助手功能文档

## 功能概述

AI日报助手提供智能日报生成、摘要、评价建议等功能，帮助用户快速完成日报填写，同时为管理者提供智能评价参考。

## 功能模块

### 1. 日报智能生成

**接口**: `POST /api/v1/ai-daily/generate`

根据用户提供的工作事项，AI自动生成专业日报。

**请求参数**:
```json
{
  "projects": ["项目A", "项目B"],
  "tasks": [
    {"name": "完成任务1", "status": "已完成", "progress": 100, "time": 4},
    {"name": "开发功能模块", "status": "进行中", "progress": 60, "time": 3}
  ],
  "notes": "额外备注信息"
}
```

**返回结果**:
```json
{
  "code": 200,
  "message": "日报生成成功",
  "data": {
    "success": true,
    "content": "完整日报内容",
    "work_goals": "工作目标部分",
    "key_progress": "关键进展部分",
    "work_items": "具体事项部分",
    "tomorrow_plan": "明日计划部分"
  }
}
```

### 2. 日报智能摘要

**接口**: `POST /api/v1/ai-daily/summarize`

分析日报内容，提取关键信息和摘要。

**请求参数**:
```json
{
  "report_content": "日报完整内容..."
}
```

**返回结果**:
```json
{
  "code": 200,
  "message": "摘要生成成功",
  "data": {
    "success": true,
    "summary": "一句话摘要",
    "key_points": ["要点1", "要点2", "要点3"],
    "workload": "高",
    "completion_rate": "85%",
    "risk_items": ["风险项1"]
  }
}
```

### 3. 评价建议

**接口**: `POST /api/v1/ai-daily/evaluation-suggestions`

为管理者提供智能评价建议。

**请求参数**:
```json
{
  "report_content": "日报内容...",
  "user_role": "高级工程师",
  "department": "技术部"
}
```

**返回结果**:
```json
{
  "code": 200,
  "message": "评价建议生成成功",
  "data": {
    "success": true,
    "suggestions": "完整建议内容",
    "rating": "B",
    "highlights": ["亮点1", "亮点2"],
    "improvements": ["改进建议1", "改进建议2"]
  }
}
```

### 4. 工作量趋势分析

**接口**: `POST /api/v1/ai-daily/workload-trend`

分析用户近期日报数据，识别工作量趋势。

**请求参数**:
```json
{
  "days": 7
}
```

**返回结果**:
```json
{
  "code": 200,
  "message": "工作量趋势分析完成",
  "data": {
    "success": true,
    "analysis": "趋势分析报告",
    "statistics": {
      "total_reports": 7,
      "total_tasks": 25,
      "avg_tasks_per_day": 3.57,
      "analysis_period": 7
    }
  }
}
```

### 5. 快速生成日报

**接口**: `POST /api/v1/ai-daily/quick-generate`

根据用户今天的任务记录，快速生成日报草稿。

**返回结果**:
```json
{
  "code": 200,
  "message": "日报草稿生成成功",
  "data": {
    "type": "generated",
    "result": {
      "success": true,
      "content": "生成的日报内容",
      "work_goals": "...",
      "key_progress": "...",
      "work_items": "...",
      "tomorrow_plan": "..."
    }
  }
}
```

## 前端集成建议

### 1. 日报填报页面添加AI生成按钮

```vue
<template>
  <div class="ai-assistant">
    <el-button type="primary" @click="showAIGenerateDialog">
      <el-icon><Magic /></el-icon>
      AI生成日报
    </el-button>
    
    <el-dialog v-model="aiDialogVisible" title="AI日报助手">
      <AIReportGenerator 
        @generate="handleAIGenerate"
      />
    </el-dialog>
  </div>
</template>
```

### 2. 评价页面添加AI建议

```vue
<template>
  <div class="ai-evaluation">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>AI评价建议</span>
          <el-button @click="getAISuggestions">获取建议</el-button>
        </div>
      </template>
      <div v-if="aiSuggestions" class="suggestions">
        <p><strong>建议等级：</strong>{{ aiSuggestions.rating }}</p>
        <p><strong>工作亮点：</strong></p>
        <ul>
          <li v-for="h in aiSuggestions.highlights" :key="h">{{ h }}</li>
        </ul>
        <p><strong>改进建议：</strong></p>
        <ul>
          <li v-for="i in aiSuggestions.improvements" :key="i">{{ i }}</li>
        </ul>
      </div>
    </el-card>
  </div>
</template>
```

## 配置要求

### 环境变量

在 `.env` 文件中添加：

```bash
# Moonshot API (Kimi) 密钥
MOONSHOT_API_KEY=your-moonshot-api-key
```

### 依赖安装

```bash
pip install openai
```

## 注意事项

1. **API密钥安全**: 不要将 API 密钥提交到Git仓库
2. **调用频率限制**: 注意 Moonshot API 的调用频率限制
3. **数据隐私**: AI处理的数据应进行脱敏处理
4. **备用方案**: 建议提供手动填写作为备用方案
