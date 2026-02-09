# 项目跟踪系统设计方案

## 🎯 需求概述

开发一个项目跟踪的一级菜单，功能是对项目全生命周期进行跟踪，把项目任务和日报进行关联，可以点击任务，打开对应的日报信息，可能是多人多个日报，基于此形成一个项目档案，如果日报有CDE的自我评价，要能够重点提醒和消息推送。

---

## 📊 一、核心功能分析

### 1.1 功能特性
- **项目全生命周期跟踪**：项目 → 任务 → 日报关联
- **任务日报联动**：点击任务查看关联的多个日报
- **项目档案形成**：基于任务和日报形成完整项目记录
- **CDE评价提醒**：重点标识和消息推送

### 1.2 用户场景
1. **项目管理员**：查看项目整体进度，监控关键任务
2. **项目经理**：跟踪任务完成情况，查看团队日报
3. **任务负责人**：查看自己负责的任务和关联日报
4. **团队成员**：查看项目进展，了解CDE评价

---

## 🗄️ 二、数据库模型设计

### 2.1 现有数据结构分析

#### Project模型（项目）
```python
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    status = Column(String(50), default="进行中")
    progress = Column(Integer, default=0)
    start_date = Column(Date)
    end_date = Column(Date)
    # 其他项目字段...
```

#### ProjectTask模型（任务）
```python
class ProjectTask(Base):
    __tablename__ = "project_tasks"
    
    task_id = Column(String(50), primary_key=True)
    project_id = Column(String(50), nullable=False)
    task_name = Column(String(200), nullable=False)
    assignee = Column(String(100), nullable=True)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(50), default="未开始")
    progress = Column(Float, default=0.0)
    # 其他任务字段...
```

#### DailyReport模型（日报）
```python
class DailyReport(Base):
    __tablename__ = "daily_reports"
    
    id = Column(Integer, primary_key=True)
    report_date = Column(Date, nullable=False)
    employee_id = Column(String(50), nullable=False)
    employee_name = Column(String(100), nullable=False)
    status = Column(String(20), default="待提交")
    # 其他日报字段...
```

#### DailyWorkItem模型（工作事项）
```python
class DailyWorkItem(Base):
    __tablename__ = "daily_work_items"
    
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey("daily_reports.id"))
    project_id = Column(String(50), nullable=True)
    project_name = Column(String(200), nullable=True)
    task_id = Column(String(50), nullable=True)
    task_name = Column(String(200), nullable=True)
    work_content = Column(Text, nullable=False)
    hours_spent = Column(Float, default=0)
    progress_status = Column(String(20), default="正常")
    evaluation = Column(String(1), nullable=True)  # CDE评价字段
    # 其他工作事项字段...
```

### 2.2 新增数据模型设计

#### ProjectTracking（项目跟踪主表）
```python
class ProjectTracking(Base):
    __tablename__ = "project_trackings"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(50), nullable=False, index=True)
    project_name = Column(String(200), nullable=False)
    
    # 跟踪状态
    overall_progress = Column(Float, default=0.0)  # 整体进度
    tracking_status = Column(String(20), default="进行中")  # 跟踪状态
    last_update_time = Column(DateTime, server_default=func.now())
    
    # 统计信息
    total_tasks = Column(Integer, default=0)  # 总任务数
    completed_tasks = Column(Integer, default=0)  # 已完成任务数
    total_reports = Column(Integer, default=0)  # 总日报数
    cde_evaluations = Column(Integer, default=0)  # CDE评价数
    
    # 时间戳
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, index=True)
    
    # 关系
    task_tracking = relationship("TaskTracking", back_populates="project_tracking", cascade="all, delete-orphan")
    report_summary = relationship("ProjectReportSummary", back_populates="project_tracking", cascade="all, delete-orphan")
    notifications = relationship("TrackingNotification", back_populates="project_tracking", cascade="all, delete-orphan")
```

#### TaskTracking（任务跟踪表）
```python
class TaskTracking(Base):
    __tablename__ = "task_trackings"
    
    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(Integer, ForeignKey("project_trackings.id"), nullable=False)
    
    # 任务基本信息
    task_id = Column(String(50), nullable=False, index=True)
    task_name = Column(String(200), nullable=False)
    assignee = Column(String(100), nullable=True)
    assignee_id = Column(String(50), nullable=True)
    
    # 计划信息
    planned_start = Column(Date, nullable=True)
    planned_end = Column(Date, nullable=True)
    
    # 实际跟踪信息
    actual_start = Column(Date, nullable=True)
    actual_end = Column(Date, nullable=True)
    current_progress = Column(Float, default=0.0)
    delay_days = Column(Integer, default=0)  # 延迟天数
    
    # 关联信息
    related_reports_count = Column(Integer, default=0)  # 关联日报数
    cde_evaluation_count = Column(Integer, default=0)  # CDE评价数
    
    # 状态跟踪
    status = Column(String(20), default="未开始")
    priority_level = Column(String(10), default="中")  # 高/中/低
    risk_level = Column(String(10), default="低")  # 高/中/低
    
    # 时间戳
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, index=True)
    
    # 关系
    project_tracking = relationship("ProjectTracking", back_populates="task_tracking")
    report_links = relationship("TaskReportLink", back_populates="task_tracking", cascade="all, delete-orphan")
```

#### TaskReportLink（任务日报关联表）
```python
class TaskReportLink(Base):
    __tablename__ = "task_report_links"
    
    id = Column(Integer, primary_key=True, index=True)
    task_tracking_id = Column(Integer, ForeignKey("task_trackings.id"), nullable=False)
    
    # 关联的日报信息
    report_id = Column(Integer, ForeignKey("daily_reports.id"), nullable=False)
    work_item_id = Column(Integer, ForeignKey("daily_work_items.id"), nullable=False)
    
    # 关联详情
    employee_id = Column(String(50), nullable=False)
    employee_name = Column(String(100), nullable=False)
    report_date = Column(Date, nullable=False)
    
    # 工作详情
    work_content = Column(Text, nullable=False)
    hours_spent = Column(Float, default=0)
    progress_contribution = Column(Float, default=0.0)  # 对任务进度的贡献
    
    # CDE评价信息
    has_cde_evaluation = Column(Boolean, default=False)
    cde_evaluation_score = Column(Integer, nullable=True)
    cde_evaluation_content = Column(Text, nullable=True)
    
    # 时间戳
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, index=True)
    
    # 关系
    task_tracking = relationship("TaskTracking", back_populates="report_links")
    daily_report = relationship("DailyReport")
    daily_work_item = relationship("DailyWorkItem")
```

#### ProjectReportSummary（项目日报汇总）
```python
class ProjectReportSummary(Base):
    __tablename__ = "project_report_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(Integer, ForeignKey("project_trackings.id"), nullable=False)
    
    # 汇总期间
    summary_date = Column(Date, nullable=False, index=True)  # 汇总日期（通常是日报日期）
    
    # 人员统计
    involved_employees = Column(Integer, default=0)  # 参与人员数
    total_work_hours = Column(Float, default=0)  # 总工作时长
    
    # 任务进展
    tasks_progressed = Column(Integer, default=0)  # 有进展的任务数
    tasks_completed = Column(Integer, default=0)  # 当日完成任务数
    
    # CDE评价统计
    cde_evaluations_count = Column(Integer, default=0)
    cde_evaluations_detail = Column(Text, nullable=True)  # CDE评价详情JSON
    
    # 问题和风险
    issues_raised = Column(Integer, default=0)  # 提出问题数
    risks_identified = Column(Integer, default=0)  # 识别风险数
    
    # 汇总内容
    daily_summary = Column(Text, nullable=True)  # 当日工作汇总
    next_day_plan = Column(Text, nullable=True)  # 次日计划
    
    # 时间戳
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, index=True)
    
    # 关系
    project_tracking = relationship("ProjectTracking", back_populates="report_summary")
```

#### TrackingNotification（跟踪通知表）
```python
class TrackingNotification(Base):
    __tablename__ = "tracking_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    tracking_id = Column(Integer, ForeignKey("project_trackings.id"), nullable=False)
    
    # 通知类型
    notification_type = Column(String(20), nullable=False)  # CDE评价/任务延迟/进度更新/风险预警
    priority_level = Column(String(10), default="中")  # 高/中/低
    
    # 通知内容
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    related_task_id = Column(String(50), nullable=True)
    related_report_id = Column(Integer, nullable=True)
    
    # 接收人信息
    recipient_id = Column(String(50), nullable=False)
    recipient_name = Column(String(100), nullable=False)
    recipient_role = Column(String(50), nullable=True)
    
    # 通知状态
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    sent_time = Column(DateTime, nullable=True)
    read_time = Column(DateTime, nullable=True)
    
    # 推送方式
    push_methods = Column(String(100), nullable=True)  # 站内信/邮件/短信/钉钉
    
    # 时间戳
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, index=True)
    
    # 关系
    project_tracking = relationship("ProjectTracking", back_populates="notifications")
```

---

## 🖥️ 三、前端界面架构设计

### 3.1 页面结构

```
ProjectTracking.vue (一级菜单入口)
├── ProjectTrackingList.vue (项目跟踪列表)
├── ProjectTrackingDetail.vue (项目跟踪详情)
│   ├── ProjectOverview.vue (项目概览)
│   ├── TaskProgress.vue (任务进度)
│   ├── ReportSummary.vue (日报汇总)
│   └── CDEAlerts.vue (CDE评价提醒)
└── TaskReportViewer.vue (任务日报查看器)
```

### 3.2 核心组件设计

#### 3.2.1 项目跟踪列表 (ProjectTrackingList.vue)
```vue
<template>
  <div class="project-tracking-list">
    <!-- 筛选和搜索 -->
    <div class="filter-bar">
      <el-input v-model="searchKeyword" placeholder="搜索项目名称" />
      <el-select v-model="statusFilter" placeholder="状态筛选">
        <el-option label="全部" value="" />
        <el-option label="进行中" value="进行中" />
        <el-option label="已完成" value="已完成" />
        <el-option label="已暂停" value="已暂停" />
      </el-select>
      <el-select v-model="priorityFilter" placeholder="优先级筛选">
        <el-option label="全部" value="" />
        <el-option label="高优先级" value="高" />
        <el-option label="中优先级" value="中" />
        <el-option label="低优先级" value="低" />
      </el-select>
    </div>
    
    <!-- 项目跟踪卡片 -->
    <div class="tracking-cards">
      <el-card 
        v-for="project in filteredProjects" 
        :key="project.id"
        class="tracking-card"
        @click="goToDetail(project.id)"
      >
        <template #header>
          <div class="card-header">
            <span class="project-name">{{ project.name }}</span>
            <el-tag :type="getStatusTagType(project.status)">
              {{ project.status }}
            </el-tag>
          </div>
        </template>
        
        <div class="card-content">
          <!-- 进度条 -->
          <div class="progress-section">
            <div class="progress-info">
              <span>整体进度</span>
              <span>{{ project.overall_progress }}%</span>
            </div>
            <el-progress 
              :percentage="project.overall_progress" 
              :status="getProgressStatus(project.overall_progress)"
            />
          </div>
          
          <!-- 任务统计 -->
          <div class="task-stats">
            <div class="stat-item">
              <span class="stat-label">任务进度</span>
              <span class="stat-value">{{ project.completed_tasks }}/{{ project.total_tasks }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">日报数量</span>
              <span class="stat-value">{{ project.total_reports }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">CDE评价</span>
              <el-badge :value="project.cde_evaluations" class="cde-badge">
                <el-icon><Star /></el-icon>
              </el-badge>
            </div>
          </div>
          
          <!-- 风险预警 -->
          <div v-if="project.risk_level !== '低'" class="risk-alert">
            <el-alert
              :title="`风险等级: ${project.risk_level}`"
              :type="getRiskAlertType(project.risk_level)"
              :closable="false"
              show-icon
            />
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>
```

#### 3.2.2 项目跟踪详情 (ProjectTrackingDetail.vue)
```vue
<template>
  <div class="project-tracking-detail">
    <!-- 项目信息头部 -->
    <div class="project-header">
      <div class="project-info">
        <h1>{{ projectDetail.name }}</h1>
        <div class="project-meta">
          <el-tag :type="getStatusTagType(projectDetail.status)">
            {{ projectDetail.status }}
          </el-tag>
          <el-tag :type="getPriorityTagType(projectDetail.priority_level)">
            {{ projectDetail.priority_level }}优先级
          </el-tag>
          <span class="date-range">
            {{ formatDate(projectDetail.start_date) }} - {{ formatDate(projectDetail.end_date) }}
          </span>
        </div>
      </div>
      
      <div class="header-actions">
        <el-button @click="exportProjectArchive">导出项目档案</el-button>
        <el-button @click="refreshData">刷新数据</el-button>
      </div>
    </div>
    
    <!-- 统计概览 -->
    <div class="overview-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="整体进度" :value="projectDetail.overall_progress">
            <template #suffix>%</template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="已完成任务" :value="projectDetail.completed_tasks">
            <template #suffix>/ {{ projectDetail.total_tasks }}</template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="日报总数" :value="projectDetail.total_reports" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="CDE评价" :value="projectDetail.cde_evaluations">
            <template #suffix>条</template>
          </el-statistic>
        </el-col>
      </el-row>
    </div>
    
    <!-- 标签页内容 -->
    <el-tabs v-model="activeTab" class="detail-tabs">
      <el-tab-pane label="项目概览" name="overview">
        <ProjectOverview :project="projectDetail" />
      </el-tab-pane>
      
      <el-tab-pane label="任务进度" name="tasks">
        <TaskProgress 
          :tasks="projectTasks" 
          @task-click="viewTaskReports"
        />
      </el-tab-pane>
      
      <el-tab-pane label="日报汇总" name="reports">
        <ReportSummary 
          :reports="projectReports" 
          @report-click="viewReportDetail"
        />
      </el-tab-pane>
      
      <el-tab-pane label="CDE提醒" name="cde">
        <CDEAlerts 
          :alerts="cdeAlerts" 
          @alert-click="handleCDEAlert"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
```

#### 3.2.3 任务日报查看器 (TaskReportViewer.vue)
```vue
<template>
  <el-dialog 
    v-model="visible" 
    :title="`任务: ${taskInfo.task_name} - 关联日报`"
    width="80%"
    top="5vh"
  >
    <div class="task-report-viewer">
      <!-- 任务基本信息 -->
      <div class="task-info">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="任务名称">{{ taskInfo.task_name }}</el-descriptions-item>
          <el-descriptions-item label="负责人">{{ taskInfo.assignee }}</el-descriptions-item>
          <el-descriptions-item label="计划进度">{{ taskInfo.planned_progress }}%</el-descriptions-item>
          <el-descriptions-item label="实际进度">{{ taskInfo.actual_progress }}%</el-descriptions-item>
          <el-descriptions-item label="开始日期">{{ formatDate(taskInfo.start_date) }}</el-descriptions-item>
          <el-descriptions-item label="结束日期">{{ formatDate(taskInfo.end_date) }}</el-descriptions-item>
        </el-descriptions>
      </div>
      
      <!-- 关联日报列表 -->
      <div class="reports-section">
        <h3>关联日报 ({{ relatedReports.length }}条)</h3>
        
        <div class="reports-timeline">
          <el-timeline>
            <el-timeline-item 
              v-for="report in relatedReports"
              :key="report.id"
              :timestamp="formatDate(report.report_date)"
              :type="getReportType(report)"
            >
              <el-card class="report-card">
                <div class="report-header">
                  <div class="reporter-info">
                    <el-icon><User /></el-icon>
                    <span>{{ report.employee_name }}</span>
                  </div>
                  <div class="report-meta">
                    <el-tag size="small">{{ report.work_hours }}小时</el-tag>
                    <el-tag 
                      v-if="report.has_cde_evaluation"
                      size="small" 
                      type="warning"
                    >
                      CDE评价
                    </el-tag>
                  </div>
                </div>
                
                <div class="report-content">
                  <p>{{ report.work_content }}</p>
                  
                  <!-- CDE评价内容 -->
                  <div v-if="report.has_cde_evaluation" class="cde-evaluation">
                    <el-divider content-position="left">
                      <el-icon><Star /></el-icon>
                      CDE自我评价
                    </el-divider>
                    <div class="evaluation-content">
                      <p>{{ report.cde_evaluation_content }}</p>
                      <el-rate 
                        v-model="report.cde_evaluation_score" 
                        disabled 
                        show-score
                        text-color="#ff9900"
                      />
                    </div>
                  </div>
                  
                  <!-- 进度贡献 -->
                  <div class="progress-contribution">
                    <el-progress 
                      :percentage="report.progress_contribution" 
                      :text-inside="true" 
                      :stroke-width="20"
                    />
                    <span class="contribution-text">
                      对任务进度贡献: {{ report.progress_contribution }}%
                    </span>
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </div>
  </el-dialog>
</template>
```

---

## 🔌 四、后端API架构设计

### 4.1 API端点设计

#### 4.1.1 项目跟踪相关API

```python
# 项目跟踪CRUD
@router.get("/project-trackings")
async def get_project_trackings(
    skip: int = 0,
    limit: int = 100,
    project_name: str = None,
    status: str = None,
    priority: str = None
):
    """获取项目跟踪列表"""
    pass

@router.get("/project-trackings/{tracking_id}")
async def get_project_tracking_detail(tracking_id: int):
    """获取项目跟踪详情"""
    pass

@router.post("/project-trackings")
async def create_project_tracking(tracking_data: ProjectTrackingCreate):
    """创建项目跟踪"""
    pass

@router.put("/project-trackings/{tracking_id}")
async def update_project_tracking(tracking_id: int, update_data: ProjectTrackingUpdate):
    """更新项目跟踪"""
    pass

# 任务跟踪相关API
@router.get("/project-trackings/{tracking_id}/tasks")
async def get_tracking_tasks(tracking_id: int):
    """获取项目的任务跟踪列表"""
    pass

@router.get("/task-trackings/{task_id}/reports")
async def get_task_related_reports(task_id: str):
    """获取任务关联的日报"""
    pass

# 日报汇总相关API
@router.get("/project-trackings/{tracking_id}/reports/summary")
async def get_project_report_summary(
    tracking_id: int,
    start_date: date = None,
    end_date: date = None
):
    """获取项目日报汇总"""
    pass

# CDE评价相关API
@router.get("/project-trackings/{tracking_id}/cde-alerts")
async def get_cde_alerts(tracking_id: int, unread_only: bool = False):
    """获取CDE评价提醒"""
    pass

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: int):
    """标记通知为已读"""
    pass
```

#### 4.1.2 数据模型定义

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

# 项目跟踪创建模型
class ProjectTrackingCreate(BaseModel):
    project_id: str = Field(..., description="项目ID")
    project_name: str = Field(..., description="项目名称")
    tracking_status: str = Field("进行中", description="跟踪状态")
    priority_level: str = Field("中", description="优先级")

# 项目跟踪更新模型
class ProjectTrackingUpdate(BaseModel):
    overall_progress: Optional[float] = Field(None, ge=0, le=100, description="整体进度")
    tracking_status: Optional[str] = Field(None, description="跟踪状态")
    priority_level: Optional[str] = Field(None, description="优先级")

# 项目跟踪响应模型
class ProjectTrackingResponse(BaseModel):
    id: int
    project_id: str
    project_name: str
    overall_progress: float
    tracking_status: str
    total_tasks: int
    completed_tasks: int
    total_reports: int
    cde_evaluations: int
    risk_level: str
    last_update_time: datetime
    
    class Config:
        from_attributes = True

# 任务跟踪响应模型
class TaskTrackingResponse(BaseModel):
    id: int
    task_id: str
    task_name: str
    assignee: str
    current_progress: float
    status: str
    priority_level: str
    risk_level: str
    related_reports_count: int
    cde_evaluation_count: int
    delay_days: int
    
    class Config:
        from_attributes = True

# 任务关联日报响应模型
class TaskReportLinkResponse(BaseModel):
    id: int
    employee_id: str
    employee_name: str
    report_date: date
    work_content: str
    hours_spent: float
    progress_contribution: float
    has_cde_evaluation: bool
    cde_evaluation_score: Optional[int]
    cde_evaluation_content: Optional[str]
    
    class Config:
        from_attributes = True

# 项目日报汇总响应模型
class ProjectReportSummaryResponse(BaseModel):
    id: int
    summary_date: date
    involved_employees: int
    total_work_hours: float
    tasks_progressed: int
    tasks_completed: int
    cde_evaluations_count: int
    daily_summary: Optional[str]
    next_day_plan: Optional[str]
    
    class Config:
        from_attributes = True

# 跟踪通知响应模型
class TrackingNotificationResponse(BaseModel):
    id: int
    notification_type: str
    priority_level: str
    title: str
    content: str
    recipient_id: str
    recipient_name: str
    is_read: bool
    create_time: datetime
    
    class Config:
        from_attributes = True
```

### 4.2 核心业务逻辑

#### 4.2.1 项目跟踪数据同步逻辑

```python
class ProjectTrackingService:
    """项目跟踪业务逻辑服务"""
    
    async def sync_project_tracking(self, project_id: str):
        """同步项目跟踪数据"""
        # 1. 获取项目基本信息
        project = await self.get_project_by_id(project_id)
        
        # 2. 创建或更新跟踪记录
        tracking = await self.get_or_create_tracking(project_id)
        
        # 3. 同步任务数据
        await self.sync_task_tracking(tracking.id, project_id)
        
        # 4. 生成日报汇总
        await self.generate_report_summary(tracking.id)
        
        # 5. 检查CDE评价提醒
        await self.check_cde_alerts(tracking.id)
        
        return tracking
    
    async def sync_task_tracking(self, tracking_id: int, project_id: str):
        """同步任务跟踪数据"""
        # 获取项目下的所有任务
        tasks = await self.get_project_tasks(project_id)
        
        for task in tasks:
            # 创建或更新任务跟踪
            task_tracking = await self.get_or_create_task_tracking(tracking_id, task.task_id)
            
            # 更新任务进度信息
            await self.update_task_progress(task_tracking.id, task)
            
            # 同步任务关联的日报
            await self.sync_task_reports(task_tracking.id, task.task_id)
    
    async def check_cde_alerts(self, tracking_id: int):
        """检查并生成CDE评价提醒"""
        # 获取未处理的CDE评价
        new_cde_evaluations = await self.get_unprocessed_cde_evaluations(tracking_id)
        
        for evaluation in new_cde_evaluations:
            # 生成通知
            await self.create_cde_notification(tracking_id, evaluation)
            
            # 标记为已处理
            await self.mark_evaluation_processed(evaluation.id)
```

#### 4.2.2 CDE评价提醒逻辑

```python
class CDENotificationService:
    """CDE评价提醒服务"""
    
    async def create_cde_notification(
        self, 
        tracking_id: int, 
        evaluation: TaskReportLink
    ):
        """创建CDE评价通知"""
        # 获取任务信息
        task_info = await self.get_task_info(evaluation.task_tracking_id)
        
        # 获取项目信息
        project_info = await self.get_project_info(tracking_id)
        
        # 构建通知内容
        notification_data = {
            "tracking_id": tracking_id,
            "notification_type": "CDE评价",
            "priority_level": self.get_cde_priority_level(evaluation.cde_evaluation_score),
            "title": f"任务[{task_info.task_name}]收到CDE评价",
            "content": f"员工{evaluation.employee_name}在任务[{task_info.task_name}]中提交了CDE自我评价: {evaluation.cde_evaluation_content}",
            "related_task_id": task_info.task_id,
            "related_report_id": evaluation.report_id,
            "recipient_id": task_info.assignee_id,
            "recipient_name": task_info.assignee,
            "push_methods": "站内信,邮件"
        }
        
        # 创建通知记录
        notification = await self.create_notification(notification_data)
        
        # 发送通知
        await self.send_notification(notification)
        
        return notification
    
    def get_cde_priority_level(self, score: int) -> str:
        """根据CDE评价分数确定优先级"""
        if score >= 4:
            return "高"
        elif score >= 3:
            return "中"
        else:
            return "低"
```

---

## 📱 五、通知推送机制设计

### 5.1 推送方式

#### 5.1.1 多渠道推送
- **站内信**：系统内消息中心
- **邮件通知**：发送到项目成员邮箱
- **企业微信**：推送到企业微信群/个人
- **钉钉通知**：推送到钉钉群或个人

#### 5.1.2 推送触发条件
- **CDE评价提交**：立即推送
- **任务延迟预警**：每日定时检查
- **进度里程碑**：达到关键节点时推送
- **风险等级变更**：风险等级提升时推送

### 5.2 通知模板

#### 5.2.1 CDE评价通知模板
```json
{
  "title": "任务收到CDE评价",
  "content": "任务[{task_name}]收到来自{employee_name}的CDE自我评价:\n{evaluation_content}\n\n评分: {score}/5\n请及时查看并反馈。",
  "type": "CDE评价",
  "priority": "中",
  "action_url": "/project-tracking/{project_id}/tasks/{task_id}/reports"
}
```

#### 5.2.2 任务延迟预警模板
```json
{
  "title": "任务进度预警",
  "content": "项目[{project_name}]中的任务[{task_name}]已延迟{delay_days}天，当前进度{progress}%。\n负责人: {assignee}\n计划完成时间: {planned_end_date}",
  "type": "任务延迟",
  "priority": "高",
  "action_url": "/project-tracking/{project_id}/tasks/{task_id}"
}
```

---

## 🔧 六、实施建议

### 6.1 开发优先级

#### 第一阶段（核心功能）
1. **数据库模型创建**：创建项目跟踪相关表
2. **基础API开发**：项目跟踪CRUD接口
3. **前端页面开发**：项目跟踪列表和详情页
4. **任务日报关联**：点击任务查看关联日报

#### 第二阶段（增强功能）
1. **CDE评价提醒**：评价提醒功能
2. **通知推送系统**：多渠道推送
3. **项目档案导出**：完整项目记录导出
4. **数据统计仪表板**：可视化统计图表

#### 第三阶段（优化功能）
1. **实时数据同步**：自动同步项目进度
2. **智能风险预警**：基于历史数据的风险预测
3. **移动端适配**：响应式设计优化
4. **高级筛选搜索**：复杂查询条件支持

### 6.2 技术实现要点

#### 6.2.1 数据同步策略
- **增量同步**：只同步变化的数据
- **定时任务**：每日自动更新项目进度
- **手动触发**：支持管理员手动触发同步

#### 6.2.2 性能优化
- **数据缓存**：Redis缓存项目跟踪数据
- **分页查询**：大数据量分页加载
- **异步处理**：CDE评价提醒异步发送

#### 6.2.3 安全性考虑
- **权限控制**：基于角色的数据访问控制
- **数据验证**：严格的输入数据验证
- **操作日志**：记录所有关键操作日志

---

## 📋 七、总结

这个项目跟踪系统设计方案充分利用了现有系统的数据结构，通过新增项目跟踪相关模型，实现了项目全生命周期的跟踪管理。核心价值在于：

1. **任务日报联动**：点击任务可查看所有关联的日报信息
2. **CDE评价提醒**：及时推送重要评价信息
3. **项目档案形成**：基于任务和日报形成完整项目记录
4. **风险预警机制**：主动识别和推送项目风险

通过分阶段实施，可以逐步完善功能，最终形成一个完整的项目跟踪管理系统。
