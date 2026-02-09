<template>
  <div class="project-tracking-container">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><TrendCharts /></el-icon>
          项目跟踪
        </h1>
        <p class="page-description">项目全生命周期跟踪管理</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建跟踪
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 筛选和搜索栏 -->
    <div class="filter-bar">
      <div class="search-group">
        <el-input
          v-model="searchParams.project_name"
          placeholder="搜索项目名称"
          clearable
          style="width: 300px"
          @keyup.enter="fetchData"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="filter-group">
        <el-select
          v-model="searchParams.status"
          placeholder="状态筛选"
          clearable
          style="width: 150px"
        >
          <el-option label="全部" value="" />
          <el-option label="进行中" value="进行中" />
          <el-option label="已完成" value="已完成" />
          <el-option label="已暂停" value="已暂停" />
          <el-option label="规划中" value="规划中" />
        </el-select>
        <el-select
          v-model="searchParams.priority"
          placeholder="优先级筛选"
          clearable
          style="width: 150px"
        >
          <el-option label="全部" value="" />
          <el-option label="高优先级" value="高" />
          <el-option label="中优先级" value="中" />
          <el-option label="低优先级" value="低" />
        </el-select>
        <el-button type="primary" @click="fetchData">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-overview">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="跟踪项目数" :value="stats.total_projects">
              <template #prefix>
                <el-icon class="stat-icon blue"><FolderOpened /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="进行中项目" :value="stats.in_progress">
              <template #prefix>
                <el-icon class="stat-icon green"><TrendCharts /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="已完成项目" :value="stats.completed">
              <template #prefix>
                <el-icon class="stat-icon success"><Check /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="CDE评价数" :value="stats.total_cde">
              <template #prefix>
                <el-icon class="stat-icon orange"><Star /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 项目跟踪列表 -->
    <div class="tracking-list">
      <div v-loading="loading" class="list-container">
        <div v-if="trackingList.length === 0" class="empty-state">
          <el-empty description="暂无项目跟踪数据">
            <el-button type="primary" @click="showCreateDialog = true">
              创建第一个项目跟踪
            </el-button>
          </el-empty>
        </div>
        
        <div v-else class="cards-grid">
          <el-card
            v-for="tracking in trackingList"
            :key="tracking.id"
            class="tracking-card"
            shadow="hover"
            @click="goToDetail(tracking.id)"
          >
            <template #header>
              <div class="card-header">
                <div class="project-info">
                  <h3 class="project-name">{{ tracking.project_name }}</h3>
                  <el-tag
                    :type="getStatusTagType(tracking.tracking_status)"
                    size="small"
                  >
                    {{ tracking.tracking_status }}
                  </el-tag>
                </div>
                <div class="card-actions">
                  <el-tag
                    :type="getPriorityTagType(tracking.priority_level)"
                    size="small"
                  >
                    {{ tracking.priority_level }}优先级
                  </el-tag>
                </div>
              </div>
            </template>

            <div class="card-content">
              <!-- 进度条 -->
              <div class="progress-section">
                <div class="progress-header">
                  <span class="progress-label">整体进度</span>
                  <span class="progress-value">{{ tracking.overall_progress.toFixed(1) }}%</span>
                </div>
                <el-progress
                  :percentage="tracking.overall_progress"
                  :status="getProgressStatus(tracking.overall_progress)"
                  :stroke-width="8"
                />
              </div>

              <!-- 统计信息 -->
              <div class="stats-section">
                <div class="stat-item">
                  <el-icon class="stat-icon blue"><List /></el-icon>
                  <div class="stat-content">
                    <span class="stat-label">任务进度</span>
                    <span class="stat-value">{{ tracking.completed_tasks }}/{{ tracking.total_tasks }}</span>
                  </div>
                </div>
                <div class="stat-item">
                  <el-icon class="stat-icon green"><Document /></el-icon>
                  <div class="stat-content">
                    <span class="stat-label">日报数量</span>
                    <span class="stat-value">{{ tracking.total_reports }}</span>
                  </div>
                </div>
                <div class="stat-item">
                  <el-icon class="stat-icon orange"><Star /></el-icon>
                  <div class="stat-content">
                    <span class="stat-label">CDE评价</span>
                    <span class="stat-value">{{ tracking.cde_evaluations }}</span>
                  </div>
                </div>
              </div>

              <!-- 风险预警 -->
              <div v-if="tracking.risk_level !== '低'" class="risk-alert">
                <el-alert
                  :title="`风险等级: ${tracking.risk_level}`"
                  :type="getRiskAlertType(tracking.risk_level)"
                  :closable="false"
                  size="small"
                  show-icon
                />
              </div>

              <!-- 最后更新时间 -->
              <div class="update-time">
                <el-icon><Clock /></el-icon>
                最后更新: {{ formatDate(tracking.last_update_time) }}
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <!-- 创建项目跟踪对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建项目跟踪"
      width="500px"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="项目ID" prop="project_id">
          <el-input
            v-model="createForm.project_id"
            placeholder="请输入项目ID"
          />
        </el-form-item>
        <el-form-item label="项目名称" prop="project_name">
          <el-input
            v-model="createForm.project_name"
            placeholder="请输入项目名称"
          />
        </el-form-item>
        <el-form-item label="跟踪状态" prop="tracking_status">
          <el-select v-model="createForm.tracking_status" style="width: 100%">
            <el-option label="进行中" value="进行中" />
            <el-option label="规划中" value="规划中" />
            <el-option label="已完成" value="已完成" />
            <el-option label="已暂停" value="已暂停" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" prop="priority_level">
          <el-select v-model="createForm.priority_level" style="width: 100%">
            <el-option label="高优先级" value="高" />
            <el-option label="中优先级" value="中" />
            <el-option label="低优先级" value="低" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="handleCreate">
            创建
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  TrendCharts,
  Plus,
  Refresh,
  Search,
  FolderOpened,
  Check,
  Star,
  List,
  Document,
  Clock
} from '@element-plus/icons-vue'
import { projectTrackingApi, type ProjectTracking } from '@/api/projectTracking'

// 路由
const router = useRouter()

// 响应式数据
const loading = ref(false)
const trackingList = ref<ProjectTracking[]>([])
const showCreateDialog = ref(false)

// 搜索参数
const searchParams = reactive({
  project_name: '',
  status: '',
  priority: ''
})

// 创建表单
const createForm = reactive({
  project_id: '',
  project_name: '',
  tracking_status: '进行中',
  priority_level: '中'
})

// 表单验证规则
const createRules = {
  project_id: [
    { required: true, message: '请输入项目ID', trigger: 'blur' }
  ],
  project_name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' }
  ]
}

// 统计概览 - 计算属性
const stats = reactive({
  total_projects: computed(() => trackingList.value.length),
  in_progress: computed(() => trackingList.value.filter(t => t.tracking_status === '进行中').length),
  completed: computed(() => trackingList.value.filter(t => t.tracking_status === '已完成').length),
  total_cde: computed(() => trackingList.value.reduce((sum, t) => sum + t.cde_evaluations, 0))
})

// 获取项目跟踪列表 - 修复：基于现有项目进行跟踪状态管理
const fetchData = async () => {
  loading.value = true
  try {
    // 使用修复后的API：获取现有项目并筛选跟踪状态
    const response = await projectTrackingApi.getProjectTrackings({
      ...searchParams,
      skip: 0,
      limit: 100
    })
    
    console.log('获取项目列表响应:', response)
    
    // 处理响应数据 - 项目跟踪是对现有项目的跟踪状态管理
    if (response.data && response.data.items) {
      // 将项目数据转换为跟踪列表格式
      trackingList.value = response.data.items.map(project => ({
        id: project.id,
        project_id: project.id.toString(),
        project_name: project.name || '未知项目',
        overall_progress: project.progress || 0,
        tracking_status: project.tracking_status || '未跟踪',
        total_tasks: project.total_tasks || 0,
        completed_tasks: project.completed_tasks || 0,
        total_reports: project.total_reports || 0,
        cde_evaluations: project.cde_evaluations || 0,
        risk_level: project.risk_level || '低风险',
        priority_level: project.priority_level || '中',
        last_update_time: project.updated_at || new Date().toISOString(),
        create_time: project.created_at || new Date().toISOString(),
        update_time: project.updated_at || new Date().toISOString()
      }))
    } else {
      // 如果没有数据，设置为空数组
      trackingList.value = []
    }
  } catch (error) {
    console.error('获取项目跟踪列表失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  fetchData()
}

// 跳转到详情页 - 修复：基于项目ID
const goToDetail = (projectId: number) => {
  router.push(`/project-tracking/${projectId}`)
}

// 创建项目跟踪
const handleCreate = async () => {
  try {
    const response = await projectTrackingApi.createProjectTracking(createForm)
    
    if (response.data.success) {
      ElMessage.success('创建成功')
      showCreateDialog.value = false
      // 重置表单
      Object.assign(createForm, {
        project_id: '',
        project_name: '',
        tracking_status: '进行中',
        priority_level: '中'
      })
      // 刷新列表
      fetchData()
    } else {
      ElMessage.error(response.data.message || '创建失败')
    }
  } catch (error) {
    console.error('创建项目跟踪失败:', error)
    ElMessage.error('创建失败')
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
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

// 获取进度状态
const getProgressStatus = (progress: number) => {
  if (progress >= 100) return 'success'
  if (progress >= 80) return ''
  if (progress >= 50) return 'warning'
  return 'exception'
}

// 获取风险预警类型
const getRiskAlertType = (riskLevel: string) => {
  switch (riskLevel) {
    case '高':
      return 'error'
    case '中':
      return 'warning'
    default:
      return 'info'
  }
}

// 生命周期
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.project-tracking-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-left {
  flex: 1;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
}

.page-description {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.search-group {
  display: flex;
  gap: 16px;
}

.filter-group {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 统计概览 */
.stats-overview {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.stat-icon {
  font-size: 20px;
  margin-right: 8px;
}

.stat-icon.blue {
  color: #3b82f6;
}

.stat-icon.green {
  color: #10b981;
}

.stat-icon.success {
  color: #22c55e;
}

.stat-icon.orange {
  color: #f59e0b;
}

/* 跟踪列表 */
.tracking-list {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.list-container {
  min-height: 400px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.tracking-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.tracking-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.project-name {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

/* 进度部分 */
.progress-section {
  margin-bottom: 20px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.progress-label {
  font-size: 14px;
  color: #6b7280;
}

.progress-value {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

/* 统计部分 */
.stats-section {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  line-height: 1;
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

/* 风险预警 */
.risk-alert {
  margin-bottom: 12px;
}

/* 更新时间 */
.update-time {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #9ca3af;
  margin-top: 8px;
}

/* 响应式 */
@media (max-width: 768px) {
  .project-tracking-container {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .filter-bar {
    flex-direction: column;
    gap: 16px;
  }
  
  .cards-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-section {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
