<template>
  <div class="project-tracking-container">
    <!-- 页面标题和操作 -->
    <div class="page-header">
      <h1>项目跟踪</h1>
      <p class="page-subtitle">项目执行状态监控和绩效分析</p>
    </div>

    <!-- 搜索筛选 -->
    <div class="search-filter">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input 
            v-model="searchParams.project_name" 
            placeholder="搜索项目名称"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchParams.status" placeholder="项目状态" clearable>
            <el-option label="全部" value="" />
            <el-option label="进行中" value="进行中" />
            <el-option label="已完成" value="已完成" />
            <el-option label="已暂停" value="已暂停" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchParams.priority" placeholder="优先级" clearable>
            <el-option label="全部" value="" />
            <el-option label="高优先级" value="高" />
            <el-option label="中优先级" value="中" />
            <el-option label="低优先级" value="低" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchParams.risk_level" placeholder="风险等级" clearable>
            <el-option label="全部" value="" />
            <el-option label="高风险" value="高风险" />
            <el-option label="中风险" value="中风险" />
            <el-option label="低风险" value="低风险" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="fetchData">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetSearch">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <el-row :gutter="20">
        <!-- 左侧：项目跟踪列表 -->
        <el-col :span="14">
          <!-- 统计概览 -->
          <div class="stats-overview">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-number">{{ stats.total_projects }}</div>
                    <div class="stat-label">跟踪项目数</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-number">{{ stats.in_progress }}</div>
                    <div class="stat-label">进行中项目</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-number">{{ stats.completed }}</div>
                    <div class="stat-label">已完成项目</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-number">{{ stats.at_risk }}</div>
                    <div class="stat-label">风险项目</div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>

          <!-- 项目跟踪列表 -->
          <el-card class="project-list-card">
            <template #header>
              <div class="card-header">
                <span>项目跟踪列表</span>
                <el-button type="primary" size="small" @click="refreshData">
                  <el-icon><Refresh /></el-icon>
                  刷新
                </el-button>
              </div>
            </template>
            
            <el-table 
              :data="projectList" 
              style="width: 100%" 
              :loading="loading"
              @row-click="goToDetail"
              :row-class-name="getRowClassName"
            >
              <el-table-column prop="name" label="项目名称" min-width="150">
                <template #default="{ row }">
                  <div class="project-name-cell">
                    <span class="project-name">{{ row.name }}</span>
                    <el-tag v-if="row.risk_level === '高风险'" type="danger" size="small">
                      {{ row.risk_level }}
                    </el-tag>
                    <el-tag v-else-if="row.risk_level === '中风险'" type="warning" size="small">
                      {{ row.risk_level }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)">
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="progress" label="进度" width="120">
                <template #default="{ row }">
                  <el-progress 
                    :percentage="row.progress" 
                    :stroke-width="8"
                    :color="getProgressColor(row.progress)"
                  />
                </template>
              </el-table-column>
              <el-table-column prop="leader" label="负责人" width="100" />
              <el-table-column prop="priority_level" label="优先级" width="100">
                <template #default="{ row }">
                  <el-tag :type="getPriorityType(row.priority_level)" size="small">
                    {{ row.priority_level }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="end_date" label="计划结束" width="120" />
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button 
                    size="small" 
                    type="primary" 
                    @click.stop="goToDetail(row)"
                  >
                    查看详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>

        <!-- 右侧：统计图表 -->
        <el-col :span="10">
          <!-- 项目状态分布 -->
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>项目状态分布</span>
              </div>
            </template>
            <div ref="statusChart" class="chart-container" style="height: 250px;"></div>
          </el-card>

          <!-- 进度分布 -->
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>项目进度分布</span>
              </div>
            </template>
            <div ref="progressChart" class="chart-container" style="height: 250px;"></div>
          </el-card>

          <!-- 风险分析 -->
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>风险等级分析</span>
              </div>
            </template>
            <div ref="riskChart" class="chart-container" style="height: 250px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'

// 项目数据接口
interface Project {
  id: number
  name: string
  status: string
  progress: number
  leader: string
  priority_level: string
  risk_level: string
  end_date: string
  created_at: string
  updated_at: string
}

// 搜索参数
const searchParams = reactive({
  project_name: '',
  status: '',
  priority: '',
  risk_level: ''
})

// 数据
const projectList = ref<Project[]>([])
const loading = ref(false)

// 图表引用
const statusChart = ref<HTMLElement | null>(null)
const progressChart = ref<HTMLElement | null>(null)
const riskChart = ref<HTMLElement | null>(null)



// 计算属性
const stats = reactive({
  total_projects: computed(() => projectList.value.length),
  in_progress: computed(() => projectList.value.filter(p => p.status === '进行中').length),
  completed: computed(() => projectList.value.filter(p => p.status === '已完成').length),
  at_risk: computed(() => projectList.value.filter(p => p.risk_level === '高风险').length)
})

// 初始化数据 - 从真实API获取
const initializeData = async () => {
  await fetchData()
}

// 获取状态类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    '进行中': 'primary',
    '已完成': 'success',
    '已暂停': 'warning',
    '已取消': 'danger'
  }
  return statusMap[status] || 'info'
}

// 获取优先级类型
const getPriorityType = (priority: string) => {
  const priorityMap: Record<string, string> = {
    '高': 'danger',
    '中': 'warning',
    '低': 'info'
  }
  return priorityMap[priority] || 'info'
}

// 获取进度条颜色
const getProgressColor = (progress: number) => {
  if (progress >= 80) return '#67c23a'
  if (progress >= 50) return '#e6a23c'
  return '#f56c6c'
}

// 获取行样式类名
const getRowClassName = ({ row }: { row: Project }) => {
  if (row.risk_level === '高风险') {
    return 'risk-row'
  }
  return ''
}

// 重置搜索
const resetSearch = () => {
  searchParams.project_name = ''
  searchParams.status = ''
  searchParams.priority = ''
  searchParams.risk_level = ''
  fetchData()
}

// 获取项目跟踪列表 - 基于真实表结构
const fetchData = async () => {
  loading.value = true
  try {
    console.log('获取项目跟踪列表...')
    
    const response = await projectTrackingApi.getProjectTrackings({
      page: 1,
      limit: 50,
      project_name: searchParams.project_name || undefined,
      tracking_status: searchParams.status || undefined,
      risk_level: searchParams.risk_level || undefined,
      priority_level: searchParams.priority || undefined
    })
    
    console.log('API响应:', response)
    
    // 处理API响应数据 - 基于真实的project_trackings表结构
    if (response.data && response.data.items) {
      // 将后端数据转换为前端需要的格式
      projectList.value = response.data.items.map(item => ({
        id: item.tracking_id || item.id,
        name: item.project_name,
        status: item.tracking_status || item.status,
        progress: Math.round(item.overall_progress || 0),
        leader: item.leader || '未指定',
        priority_level: item.priority_level || '中',
        risk_level: item.risk_level || '低风险',
        end_date: item.planned_end_date || '未设置',
        created_at: item.create_time || new Date().toISOString(),
        updated_at: item.update_time || new Date().toISOString(),
        
        // 统计数据
        total_tasks: item.total_tasks || 0,
        completed_tasks: item.completed_tasks || 0,
        total_reports: item.total_reports || 0,
        cde_evaluations: item.cde_evaluations || 0
      }))
    } else {
      projectList.value = []
    }
    
    console.log('处理后的项目列表:', projectList.value)
    
  } catch (error) {
    console.error('获取项目跟踪列表失败:', error)
    ElMessage.error('获取项目跟踪数据失败')
    
    // 如果API失败，使用空数组而不是模拟数据
    projectList.value = []
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  fetchData()
}

// 跳转到详情页
const goToDetail = (project: Project) => {
  const router = useRouter()
  router.push(`/project-tracking/${project.id}`)
}

// 初始化图表
const initCharts = () => {
  // 初始化图表逻辑
  console.log('初始化图表')
}

// 组件挂载时初始化
onMounted(() => {
  initializeData()
  initCharts()
})
</script>

<style scoped>
.project-tracking-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  color: #303133;
  margin-bottom: 10px;
  font-size: 28px;
}

.page-subtitle {
  color: #606266;
  font-size: 16px;
}

.search-filter {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.main-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stats-overview {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  padding: 10px;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.project-list-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.project-name {
  font-weight: 500;
  color: #303133;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-container {
  width: 100%;
  min-height: 250px;
}

:deep(.el-table .risk-row) {
  background-color: #fef0f0;
}

:deep(.el-table .cell) {
  padding: 8px 12px;
}

:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>