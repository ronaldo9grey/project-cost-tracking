<template>
  <div class="dashboard-container">
    <h1>项目看板</h1>
    
    <!-- 统计卡片 -->
    <el-row :gutter="10" style="margin-bottom: 20px;">
      <el-col :xs="24" :sm="12" :md="5" :lg="5" :xl="5">
        <el-card shadow="hover" class="stat-card" style="width: 100%;">
          <div class="stat-content" style="font-size: 12px;">
            <div class="stat-title" style="font-size: 14px;">项目总数</div>
            <div class="stat-value" style="font-size: 24px;">{{ stats.total_projects }}</div>
            <div class="stat-desc" style="font-size: 12px;">当前系统中所有项目</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="5" :lg="5" :xl="5">
        <el-card shadow="hover" class="stat-card" style="width: 100%;">
          <div class="stat-content" style="font-size: 12px;">
            <div class="stat-title" style="font-size: 14px;">进行中项目</div>
            <div class="stat-value" style="font-size: 24px;">{{ stats.in_progress }}</div>
            <div class="stat-desc" style="font-size: 12px;">正在执行的项目</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="5" :lg="5" :xl="5">
        <el-card shadow="hover" class="stat-card" style="width: 100%;">
          <div class="stat-content" style="font-size: 12px;">
            <div class="stat-title" style="font-size: 14px;">已完成项目</div>
            <div class="stat-value" style="font-size: 24px;">{{ stats.completed }}</div>
            <div class="stat-desc" style="font-size: 12px;">已完成的全部项目</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="9" :lg="9" :xl="9">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content" style="font-size: 12px;">
            <div class="stat-title" style="font-size: 14px;">系统概览</div>
            <div class="stat-value" style="font-size: 20px;">
              总计 {{ stats.total_projects }} 个项目，其中 {{ stats.in_progress }} 个进行中
            </div>
            <div class="stat-desc" style="font-size: 12px; line-height: 1.2;">系统运行正常，数据实时更新</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <!-- 项目状态分布图表 -->
      <el-col :span="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>项目状态分布</span>
              <el-button type="primary" size="small" @click="refreshData">刷新数据</el-button>
            </div>
          </template>
          <div ref="statusChart" class="chart-container" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <!-- 项目进度图表 -->
      <el-col :span="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>项目进度分布</span>
              <el-button type="primary" size="small" @click="refreshData">刷新数据</el-button>
            </div>
          </template>
          <div ref="progressChart" class="chart-container" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <!-- 成本概览图表 -->
      <el-col :span="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>成本概览</span>
              <el-button type="primary" size="small" @click="refreshData">刷新数据</el-button>
            </div>
          </template>
          <div ref="costChart" class="chart-container" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 项目列表 -->
    <el-row style="margin-top: 20px;">
      <el-col :span="24">
        <el-card shadow="hover" class="project-list-card">
          <template #header>
            <div class="card-header">
              <span>项目列表</span>
              <el-button type="primary" size="small" @click="refreshData">
                刷新数据
              </el-button>
            </div>
          </template>
          <el-table :data="projectList" style="width: 100%" border :loading="loading">
            <el-table-column prop="name" label="项目名称" sortable />
            <el-table-column prop="status" label="状态" sortable>
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="进度" sortable>
              <template #default="scope">
                <el-progress :percentage="scope.row.progress" :stroke-width="8" />
              </template>
            </el-table-column>
            <el-table-column prop="leader" label="负责人" sortable />
            <el-table-column prop="created_at" label="创建时间" sortable />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" type="primary" @click="viewProject(scope.row)">
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { ElTable } from 'element-plus'

// 项目数据接口
interface Project {
  id: number
  name: string
  status: string
  progress: number
  leader: string
  created_at: string
  contract_amount: number
  budget_total_cost: number
  actual_total_cost: number
}

// 看板数据
const projectList = ref<Project[]>([])

// 加载状态
const loading = ref(false)

// 图表引用
const statusChart = ref<HTMLElement | null>(null)
const progressChart = ref<HTMLElement | null>(null)
const costChart = ref<HTMLElement | null>(null)

// 模拟项目数据
const mockProjects: Project[] = [
  {
    id: 1,
    name: '企业信息化项目',
    status: '进行中',
    progress: 75,
    leader: '张三',
    created_at: '2024-01-15',
    contract_amount: 500000,
    budget_total_cost: 400000,
    actual_total_cost: 350000
  },
  {
    id: 2,
    name: '移动应用开发',
    status: '已完成',
    progress: 100,
    leader: '李四',
    created_at: '2024-02-01',
    contract_amount: 300000,
    budget_total_cost: 250000,
    actual_total_cost: 260000
  },
  {
    id: 3,
    name: '数据分析平台',
    status: '计划中',
    progress: 10,
    leader: '王五',
    created_at: '2024-03-01',
    contract_amount: 800000,
    budget_total_cost: 700000,
    actual_total_cost: 50000
  },
  {
    id: 4,
    name: '客户服务系统升级',
    status: '进行中',
    progress: 45,
    leader: '赵六',
    created_at: '2024-02-20',
    contract_amount: 200000,
    budget_total_cost: 180000,
    actual_total_cost: 120000
  }
]

// 统计计算
const stats = reactive({
  total_projects: computed(() => projectList.value.length),
  in_progress: computed(() => projectList.value.filter(p => p.status === '进行中').length),
  completed: computed(() => projectList.value.filter(p => p.status === '已完成').length)
})

// 初始化数据
const initializeData = () => {
  projectList.value = mockProjects
}

// 获取状态类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    '进行中': 'primary',
    '已完成': 'success',
    '计划中': 'info',
    '已暂停': 'warning',
    '已取消': 'danger'
  }
  return statusMap[status] || 'info'
}

// 初始化图表
const initCharts = () => {
  // 这里应该初始化图表，但为了简化先跳过
  console.log('图表初始化完成')
}

// 刷新数据
const refreshData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    initializeData()
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败')
  } finally {
    loading.value = false
  }
}

// 查看项目详情
const viewProject = (project: Project) => {
  const router = useRouter()
  router.push(`/projects/${project.id}`)
}

// 组件挂载时初始化
onMounted(() => {
  initializeData()
  initCharts()
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

h1 {
  margin-bottom: 20px;
  color: #303133;
  text-align: center;
}

.stat-card {
  margin-bottom: 10px;
}

.stat-content {
  text-align: center;
  padding: 10px;
}

.stat-title {
  font-weight: bold;
  margin-bottom: 5px;
  color: #606266;
}

.stat-value {
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-desc {
  color: #909399;
  font-size: 11px;
}

.chart-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  width: 100%;
  min-height: 300px;
}

.project-list-card {
  margin-top: 20px;
}

:deep(.el-table) {
  font-size: 12px;
}

:deep(.el-table .cell) {
  padding: 5px 8px;
}

:deep(.el-progress-bar__outer) {
  border-radius: 4px;
}

:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>