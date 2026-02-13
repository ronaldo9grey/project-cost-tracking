<template>
  <div class="project-tracking-detail-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button link @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h1 class="page-title">
          <el-icon><TrendCharts /></el-icon>
          {{ projectDetail?.project_name || '项目跟踪详情' }}
        </h1>
      </div>
      <div class="header-actions">
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
        <el-button @click="exportProjectArchive">
          <el-icon><Download /></el-icon>
          导出项目档案
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- 详情内容 -->
    <div v-else-if="projectDetail" class="detail-content">
      <!-- 项目概览 -->
      <div class="overview-section">
        <el-card shadow="never" class="overview-card">
          <template #header>
            <div class="card-header">
              <h2 class="section-title">项目概览</h2>
              <div class="header-meta">
                <el-tag :type="getStatusTagType(projectDetail.tracking.tracking_status)">
                  {{ projectDetail.tracking.tracking_status }}
                </el-tag>
                <el-tag :type="getPriorityTagType(projectDetail.tracking.priority_level)">
                  {{ projectDetail.tracking.priority_level }}优先级
                </el-tag>
                <el-tag v-if="projectDetail.tracking.risk_level !== '低'" 
                         :type="getRiskTagType(projectDetail.tracking.risk_level)">
                  {{ projectDetail.tracking.risk_level }}风险
                </el-tag>
              </div>
            </div>
          </template>
          
          <div class="overview-content">
            <el-row :gutter="24">
              <el-col :span="6">
                <el-statistic title="整体进度" :value="projectDetail.tracking.overall_progress">
                  <template #suffix>%</template>
                </el-statistic>
              </el-col>
              <el-col :span="6">
                <el-statistic title="已完成任务" :value="projectDetail.task_summary.completed">
                  <template #suffix>/ {{ projectDetail.task_summary.total }}</template>
                </el-statistic>
              </el-col>
              <el-col :span="6">
                <el-statistic title="日报总数" :value="projectDetail.tracking.total_reports" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="CDE评价" :value="projectDetail.tracking.cde_evaluations">
                  <template #suffix>条</template>
                </el-statistic>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </div>

      <!-- 标签页内容 -->
      <div class="tabs-section">
        <el-tabs v-model="activeTab" class="detail-tabs">
          <!-- 任务进度 -->
          <el-tab-pane label="任务进度" name="tasks">
            <div class="tasks-content">
              <div class="tasks-header">
                <h3>任务进度跟踪</h3>
                <div class="tasks-stats">
                  <el-tag type="success">已完成: {{ projectDetail.task_summary.completed }}</el-tag>
                  <el-tag type="primary">进行中: {{ projectDetail.task_summary.in_progress }}</el-tag>
                  <el-tag v-if="projectDetail.task_summary.delayed > 0" type="warning">
                    延迟: {{ projectDetail.task_summary.delayed }}
                  </el-tag>
                </div>
              </div>
              
              <div class="tasks-list">
                <el-table
                  :data="taskList"
                  style="width: 100%"
                  v-loading="taskLoading"
                  @row-click="handleTaskClick"
                >
                  <el-table-column prop="task_name" label="任务名称" min-width="200" />
                  <el-table-column prop="assignee" label="负责人" width="120" />
                  <el-table-column label="进度" width="200">
                    <template #default="{ row }">
                      <div class="progress-cell">
                        <el-progress
                          :percentage="row.current_progress"
                          :status="getProgressStatus(row.current_progress)"
                          :stroke-width="6"
                        />
                        <span class="progress-text">{{ row.current_progress }}%</span>
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column prop="status" label="状态" width="100">
                    <template #default="{ row }">
                      <el-tag :type="getStatusTagType(row.status)" size="small">
                        {{ row.status }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="delay_days" label="延迟天数" width="100">
                    <template #default="{ row }">
                      <span v-if="row.delay_days > 0" class="delay-text">
                        {{ row.delay_days }}天
                      </span>
                      <span v-else class="normal-text">正常</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="cde_evaluation_count" label="CDE评价" width="100">
                    <template #default="{ row }">
                      <el-badge :value="row.cde_evaluation_count" class="cde-badge">
                        <el-icon><Star /></el-icon>
                      </el-badge>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="120" fixed="right">
                    <template #default="{ row }">
                      <el-button 
                        type="primary" 
                        size="small" 
                        @click.stop="viewTaskReports(row)"
                      >
                        查看日报
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </el-tab-pane>

          <!-- 日报汇总 -->
          <el-tab-pane label="日报汇总" name="reports">
            <div class="reports-content">
              <h3>项目日报汇总</h3>
              <el-empty description="暂无日报数据" />
            </div>
          </el-tab-pane>

          <!-- CDE评价提醒 -->
          <el-tab-pane label="CDE评价" name="cde">
            <div class="cde-content">
              <div class="cde-header">
                <h3>CDE评价提醒</h3>
                <div class="cde-actions">
                  <el-button 
                    type="primary" 
                    @click="markAllAsRead"
                    :disabled="unreadAlerts.length === 0"
                  >
                    全部标记为已读
                  </el-button>
                </div>
              </div>
              
              <div v-if="cdeAlerts.length === 0" class="no-alerts">
                <el-empty description="暂无CDE评价提醒" />
              </div>
              
              <div v-else class="alerts-list">
                <el-card
                  v-for="alert in cdeAlerts"
                  :key="alert.id"
                  class="alert-card"
                  :class="{ 'unread': !alert.is_read }"
                  shadow="hover"
                >
                  <div class="alert-content">
                    <div class="alert-header">
                      <div class="alert-title">
                        <el-icon v-if="!alert.is_read" class="unread-icon"><Bell /></el-icon>
                        {{ alert.title }}
                      </div>
                      <div class="alert-meta">
                        <el-tag :type="getPriorityTagType(alert.priority_level)" size="small">
                          {{ alert.priority_level }}优先级
                        </el-tag>
                        <span class="alert-time">{{ formatDate(alert.create_time) }}</span>
                      </div>
                    </div>
                    <div class="alert-body">
                      {{ alert.content }}
                    </div>
                    <div class="alert-actions">
                      <el-button 
                        v-if="!alert.is_read"
                        size="small" 
                        @click="markAsRead(alert.id)"
                      >
                        标记为已读
                      </el-button>
                      <el-button 
                        v-if="alert.related_task_id"
                        size="small" 
                        @click="viewRelatedTask(alert.related_task_id)"
                      >
                        查看任务
                      </el-button>
                    </div>
                  </div>
                </el-card>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- 任务日报查看对话框 -->
    <TaskReportViewer
      v-model="showTaskReports"
      :task-id="selectedTask?.task_id"
      :task-info="selectedTask"
      @close="selectedTask = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  TrendCharts,
  Refresh,
  Download,
  Bell,
  Star
} from '@element-plus/icons-vue'
import { projectTrackingApi, type TaskTracking, type TrackingNotification } from '@/api/projectTracking'
import TaskReportViewer from './components/TaskReportViewer.vue'

// 路由
const router = useRouter()
const route = useRoute()

// 响应式数据
const loading = ref(true)
const taskLoading = ref(false)
const projectDetail = ref<any>(null)
const taskList = ref<TaskTracking[]>([])
const cdeAlerts = ref<TrackingNotification[]>([])
const activeTab = ref('tasks')
const showTaskReports = ref(false)
const selectedTask = ref<TaskTracking | null>(null)

// 页面参数
const trackingId = route.params.trackingId as string

// 计算属性
const unreadAlerts = computed(() => 
  cdeAlerts.value.filter(alert => !alert.is_read)
)

// 获取项目跟踪详情
const fetchProjectDetail = async () => {
  loading.value = true
  try {
    const response = await projectTrackingApi.getProjectTrackingDetail(Number(trackingId))
    
    if (response.data.success) {
      projectDetail.value = response.data.data
      // 更新任务列表
      if (projectDetail.value.recent_tasks) {
        taskList.value = projectDetail.value.recent_tasks
      }
      // 更新CDE评价列表
      if (projectDetail.value.cde_alerts) {
        cdeAlerts.value = projectDetail.value.cde_alerts
      }
    } else {
      ElMessage.error(response.data.message || '获取项目详情失败')
    }
  } catch (error) {
    console.error('获取项目跟踪详情失败:', error)
    ElMessage.error('获取项目详情失败')
  } finally {
    loading.value = false
  }
}

// 获取任务跟踪列表
const fetchTaskList = async () => {
  taskLoading.value = true
  try {
    const response = await projectTrackingApi.getTrackingTasks(Number(trackingId))
    
    if (response.data.success) {
      taskList.value = response.data.data || []
    } else {
      ElMessage.error(response.data.message || '获取任务列表失败')
    }
  } catch (error) {
    console.error('获取任务跟踪列表失败:', error)
    ElMessage.error('获取任务列表失败')
  } finally {
    taskLoading.value = false
  }
}

// 获取CDE评价提醒
const fetchCDEAlerts = async () => {
  try {
    const response = await projectTrackingApi.getCDEAlerts(Number(trackingId))
    
    if (response.data.success) {
      cdeAlerts.value = response.data.data || []
    } else {
      ElMessage.error(response.data.message || '获取CDE评价提醒失败')
    }
  } catch (error) {
    console.error('获取CDE评价提醒失败:', error)
    ElMessage.error('获取CDE评价提醒失败')
  }
}

// 刷新数据
const refreshData = () => {
  fetchProjectDetail()
  fetchTaskList()
  fetchCDEAlerts()
}

// 返回上一页
const goBack = () => {
  router.go(-1)
}

// 查看任务日报
const viewTaskReports = (task: TaskTracking) => {
  selectedTask.value = task
  showTaskReports.value = true
}

// 查看相关任务
const viewRelatedTask = (taskId: string) => {
  // 这里可以跳转到任务详情或相关页面
  ElMessage.info(`查看任务: ${taskId}`)
}

// 标记为已读
const markAsRead = async (notificationId: number) => {
  try {
    const response = await projectTrackingApi.markNotificationRead(notificationId)
    
    if (response.data.success) {
      // 更新本地状态
      const alert = cdeAlerts.value.find(a => a.id === notificationId)
      if (alert) {
        alert.is_read = true
      }
      ElMessage.success('标记为已读')
    } else {
      ElMessage.error(response.data.message || '标记失败')
    }
  } catch (error) {
    console.error('标记为已读失败:', error)
    ElMessage.error('标记为已读失败')
  }
}

// 全部标记为已读
const markAllAsRead = async () => {
  try {
    const promises = unreadAlerts.value.map(alert => 
      projectTrackingApi.markNotificationRead(alert.id)
    )
    
    await Promise.all(promises)
    
    // 更新本地状态
    unreadAlerts.value.forEach(alert => {
      alert.is_read = true
    })
    
    ElMessage.success('全部标记为已读')
  } catch (error) {
    console.error('批量标记失败:', error)
    ElMessage.error('批量标记失败')
  }
}

// 导出项目档案
const exportProjectArchive = () => {
  ElMessage.info('导出项目档案功能开发中...')
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取状态标签类型
const getStatusTagType = (status: string) => {
  switch (status) {
    case '进行中':
      return 'primary'
    case '已完成':
      return 'success'
    case '已暂停':
      return 'warning'
    case '规划中':
      return 'info'
    default:
      return ''
  }
}

// 获取优先级标签类型
const getPriorityTagType = (priority: string) => {
  switch (priority) {
    case '高':
      return 'danger'
    case '中':
      return 'warning'
    case '低':
      return 'success'
    default:
      return 'info'
  }
}

// 获取风险标签类型
const getRiskTagType = (risk: string) => {
  switch (risk) {
    case '高':
      return 'danger'
    case '中':
      return 'warning'
    case '低':
      return 'success'
    default:
      return 'info'
  }
}

// 获取进度状态
const getProgressStatus = (progress: number) => {
  if (progress >= 100) return 'success'
  if (progress >= 80) return ''
  if (progress >= 50) return 'warning'
  return 'exception'
}

// 处理任务点击
const handleTaskClick = (row: TaskTracking) => {
  viewTaskReports(row)
}

// 生命周期
onMounted(() => {
  fetchProjectDetail()
  fetchTaskList()
  fetchCDEAlerts()
})
</script>

<style scoped>
.project-tracking-detail-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 加载状态 */
.loading-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* 详情内容 */
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 项目概览 */
.overview-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.overview-card {
  border: none;
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.header-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 标签页部分 */
.tabs-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.detail-tabs {
  padding: 24px;
}

/* 任务内容 */
.tasks-content {
  padding: 0;
}

.tasks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.tasks-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.tasks-stats {
  display: flex;
  gap: 12px;
}

.tasks-list {
  margin-top: 20px;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-text {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  min-width: 35px;
}

.delay-text {
  color: #f59e0b;
  font-weight: 600;
}

.normal-text {
  color: #6b7280;
}

.cde-badge {
  color: #f59e0b;
}

/* 报告内容 */
.reports-content {
  padding: 0;
}

.reports-content h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

/* CDE评价内容 */
.cde-content {
  padding: 0;
}

.cde-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.cde-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.cde-actions {
  display: flex;
  gap: 12px;
}

.no-alerts {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.alert-card {
  border: none;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.alert-card.unread {
  border-left: 4px solid #409eff;
  background: #f0f9ff;
}

.alert-content {
  padding: 0;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.alert-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.unread-icon {
  color: #409eff;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.alert-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.alert-time {
  font-size: 12px;
  color: #6b7280;
}

.alert-body {
  color: #4b5563;
  line-height: 1.6;
  margin-bottom: 16px;
}

.alert-actions {
  display: flex;
  gap: 12px;
}

/* 响应式 */
@media (max-width: 768px) {
  .project-tracking-detail-container {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .header-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .tasks-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .cde-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .alert-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
