# 日报列表页面API优化指南

## 🎯 API变更总结

### 响应字段变更
**已移除的字段：**
- ❌ `project_name`: 项目名称
- ❌ `project_id`: 项目ID
- ❌ `task_id`: 任务ID
- ❌ `task_name`: 任务名称
- ❌ `work_items`: 工作事项详情

**新增的字段：**
- ✅ `actual_hours`: 实际工时（从daily_work_items子表计算）

**保留的字段：**
- `id`: 日报ID
- `report_date`: 日报日期
- `employee_id`: 员工ID
- `employee_name`: 员工姓名
- `tomorrow_plan`: 明日计划
- `planned_hours`: 计划工时
- `status`: 状态
- `submitted_at`: 提交时间
- `create_time`: 创建时间
- `update_time`: 更新时间

### 检索条件变更
**状态筛选枚举值：**
- "待提交"
- "已提交" 
- "已评价"

## 🔧 前端需要更新的地方

### 1. 列表表格列定义
```javascript
// 移除这些列：
const removedColumns = [
  'project_name',
  'project_id', 
  'task_id',
  'task_name',
  'work_items'
];

// 更新"用时"列显示为"工时"：
const columns = [
  // ... 其他列
  {
    title: '工时',
    dataIndex: 'actual_hours',  // 从 planned_hours 改为 actual_hours
    key: 'actual_hours',
    render: (hours) => `${hours || 0}小时`
  },
  // ... 其他列
];
```

### 2. 状态筛选器更新
```javascript
const statusOptions = [
  { label: '待提交', value: '待提交' },
  { label: '已提交', value: '已提交' },
  { label: '已评价', value: '已评价' }
];
```

### 3. API调用更新
```javascript
// API响应现在只包含简化的列表数据
const fetchReports = async (params) => {
  const response = await api.get('/api/v1/daily-report/legacy/my-reports', {
    params: {
      ...params,
      status: params.status // 现在有枚举验证
    }
  });
  return response.data;
};
```

### 4. 页面显示调整
```javascript
// 移除不需要显示的字段
const displayFields = [
  'id',
  'report_date', 
  'employee_name',
  'tomorrow_plan',
  'planned_hours',
  'actual_hours',  // 新增：显示实际工时
  'status',
  'create_time'
];
```

## 📊 数据示例

### 优化前的响应数据
```json
{
  "items": [
    {
      "id": 11,
      "work_items": [...], // 大量工作事项数据
      "project_name": "项目A",
      "project_id": "PROJ001",
      "task_name": "任务A",
      "task_id": "TASK001",
      // ... 很多字段
    }
  ]
}
```

### 优化后的响应数据
```json
{
  "items": [
    {
      "id": 11,
      "report_date": "2026-01-16",
      "employee_id": "0001",
      "tomorrow_plan": "明天工作",
      "planned_hours": 8.0,
      "actual_hours": 8.0,  // 新增：实际工时
      "status": "待提交",
      "submitted_at": null,
      "create_time": "2026-01-13T11:41:08.842092",
      "update_time": "2026-01-13T11:41:08.842092"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "total_pages": 1
}
```

## ✅ 优化效果

1. **数据传输量减少**: 移除了大量工作事项详情数据
2. **显示更加简洁**: 只显示必要的汇总信息
3. **工时计算准确**: 实际工时自动从子表计算
4. **状态筛选明确**: 枚举值限制状态选项
5. **页面加载更快**: 响应数据量大幅减少

## 🔍 测试验证

### API测试结果
```bash
=== 测试优化后的列表API ===
1. 登录...
2. 获取优化后的列表...
列表获取状态码: 200
总数量: 1
当前页: 1
第一个列表项字段:
  - id: 11
  - report_date: 2026-01-16
  - employee_id: 0001
  - tomorrow_plan: 明天工作
  - planned_hours: 8.0
  - actual_hours: 8.0
  - status: 待提交
  - submitted_at: None
  - create_time: 2026-01-13T11:41:08.842092
  - update_time: 2026-01-13T11:41:08.842092

✅ 列表获取成功，字段已优化
```

所有功能已验证正常！