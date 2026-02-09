<template>
  <div class="dashboard-container">
    <!-- 统计卡片 -->
    <el-row :gutter="10" style="margin-bottom: 20px;">
      <el-col :xs="24" :sm="12" :md="5" :lg="5" :xl="5">
        <el-card shadow="hover" class="stat-card" style="width: 100%;">
          <div class="stat-content" style="font-size: 12px;">
            <div class="stat-title" style="font-size: 14px;">项目总数</div>
            <div class="stat-value" style="font-size: 24px;">{{ dashboardData.totalProjects || 0 }}</div>
            <div class="stat-desc" style="font-size: 12px;">当前系统中所有项目</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="5" :lg="5" :xl="5">
        <el-card shadow="hover" class="stat-card" style="width: 100%;">
          <div class="stat-content" style="font-size: 12px;">
            <div class="stat-title" style="font-size: 14px;">合同金额</div>
            <div class="stat-value" style="font-size: 24px;">¥ {{ formatCurrency(dashboardData.totalContractAmount || 0) }}</div>
            <div class="stat-desc" style="font-size: 12px;">所有项目的总合同额</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="5" :lg="5" :xl="5">
        <el-card shadow="hover" class="stat-card" style="width: 100%;">
          <div class="stat-content" style="font-size: 12px;">
            <div class="stat-title" style="font-size: 14px;">预算成本</div>
            <div class="stat-value" style="font-size: 24px;">¥ {{ formatCurrency(dashboardData.totalBudgetCost || 0) }}</div>
            <div class="stat-desc" style="font-size: 12px;">所有项目的预算总成本</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="5" :lg="5" :xl="5">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content" style="font-size: 12px;">
            <div class="stat-title" style="font-size: 14px;">实际成本</div>
            <div class="stat-value" style="font-size: 24px;">¥ {{ formatCurrency(dashboardData.totalActualCost || 0) }}</div>
            <div class="stat-desc" style="font-size: 12px;">所有项目的实际总成本</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="4" :lg="4" :xl="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content" style="font-size: 12px;">
            <div class="stat-title" style="font-size: 14px;">成本偏差</div>
            <div class="stat-value" :class="(dashboardData.costVariance || 0) > 0 ? 'stat-value-negative' : 'stat-value-positive'" style="font-size: 24px;">
              {{ (dashboardData.costVariance || 0) >= 0 ? '+' : '' }}{{ formatCurrency(dashboardData.costVariance || 0) }}
            </div>
            <div class="stat-desc" style="font-size: 12px; line-height: 1.2;">实际成本与预算的偏差</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 项目状态分布图表 -->
      <el-col :span="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>项目状态分布</span>
              <el-button type="primary" size="small" @click="refreshData">刷新数据</el-button>
            </div>
          </template>
          <div ref="statusChart" class="chart-container" style="height: 400px;"></div>
        </el-card>
      </el-col>
      <!-- 延期任务分布图表 -->
      <el-col :span="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>延期任务分布</span>
              <el-button type="primary" size="small" @click="refreshData">刷新数据</el-button>
            </div>
          </template>
          <div ref="progressChart" class="chart-container" style="height: 400px;"></div>
        </el-card>
      </el-col>
      <!-- 人员工作量分布图表 -->
      <el-col :span="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>人员工作量分布</span>
              <el-button type="primary" size="small" @click="refreshData">刷新数据</el-button>
            </div>
          </template>
          <div ref="workloadChart" class="chart-container" style="height: 400px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 成本偏差排名图表（单独一行） -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>成本偏差排名Top10</span>
              <el-button type="primary" size="small" @click="refreshData">刷新数据</el-button>
            </div>
          </template>
          <div ref="costTrendChart" class="chart-container" style="height: 500px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 延期任务明细表 -->
    <el-row style="margin-top: 20px;">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>延期任务明细表</span>
              <el-button type="primary" size="small" @click="refreshData">
                刷新数据
              </el-button>
            </div>
          </template>
          <el-table :data="dashboardData.delayedTasks" style="width: 100%" border>
            <el-table-column prop="task_name" label="任务名称" sortable />
            <el-table-column prop="project_name" label="项目名称" sortable />
            <el-table-column prop="assignee" label="负责人" sortable />
            <el-table-column prop="start_date" label="开始日期" sortable />
            <el-table-column prop="end_date" label="计划结束日期" sortable />
            <el-table-column prop="actual_end_date" label="实际结束日期" sortable>
              <template #default="scope">
                {{ scope.row.actual_end_date || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="delayDays" label="延期天数" sortable>
              <template #default="scope">
                <span :style="{ color: scope.row.delayDays > 0 ? '#f56c6c' : '#67c23a' }">
                  {{ scope.row.delayDays }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 成本偏差排名表 -->
    <el-row style="margin-top: 20px;">
      <el-col :span="24">
        <el-card shadow="hover" class="deviation-ranking-card">
          <template #header>
            <div class="card-header">
              <span>成本偏差排名表</span>
              <el-button type="primary" size="small" @click="refreshData">
                刷新数据
              </el-button>
            </div>
          </template>
          <el-table 
            :data="dashboardData.projectDeviation" 
            style="width: 100%" 
            border 
            :row-style="{ cursor: 'pointer' }"
            :default-expanded-keys="[]"
          >
            <!-- 序号列作为展开触发点 -->
            <el-table-column type="expand">
              <template #default="props">
                <div class="expanded-content">
                  <!-- 项目基本信息 -->
                  <div class="project-basic-info">
                    <h4>项目基本信息</h4>
                    <el-row :gutter="20" style="margin-bottom: 15px;">
                      <el-col :span="12">
                        <div class="info-item">
                          <span class="info-label">项目负责人：</span>
                          <span class="info-value">{{ props.row.leader || '-' }}</span>
                        </div>
                        <div class="info-item">
                          <span class="info-label">开始日期：</span>
                          <span class="info-value">{{ props.row.start_date || '-' }}</span>
                        </div>
                        <div class="info-item">
                          <span class="info-label">计划结束日期：</span>
                          <span class="info-value">{{ props.row.end_date || '-' }}</span>
                        </div>
                      </el-col>
                      <el-col :span="12">
                        <div class="info-item">
                          <span class="info-label">实际结束日期：</span>
                          <span class="info-value">{{ props.row.actual_end_date || '-' }}</span>
                        </div>
                        <div class="info-item">
                          <span class="info-label">总预算：</span>
                          <span class="info-value">¥ {{ formatCurrency(props.row.budget_total_cost) }}</span>
                        </div>
                        <div class="info-item">
                          <span class="info-label">总成本：</span>
                          <span class="info-value">¥ {{ formatCurrency(props.row.actual_total_cost) }}</span>
                        </div>
                      </el-col>
                    </el-row>
                  </div>
                  
                  <!-- 成本维度详情 -->
                  <div class="cost-dimension-details">
                    <h4>成本维度详情</h4>
                    <el-table 
                      :data="[
                        { dimension: '物料/设备', budget: props.row.dimensions.material.budget, actual: props.row.dimensions.material.actual, deviation: props.row.dimensions.material.deviation },
                        { dimension: '外包服务', budget: props.row.dimensions.outsourcing.budget, actual: props.row.dimensions.outsourcing.actual, deviation: props.row.dimensions.outsourcing.deviation },
                        { dimension: '间接成本', budget: props.row.dimensions.indirect.budget, actual: props.row.dimensions.indirect.actual, deviation: props.row.dimensions.indirect.deviation },
                        { dimension: '人力成本', budget: props.row.dimensions.labor.budget, actual: props.row.dimensions.labor.actual, deviation: props.row.dimensions.labor.deviation }
                      ]" 
                      size="small" 
                      border 
                      style="margin-top: 10px;">
                      <el-table-column prop="dimension" label="维度" width="120" />
                      <el-table-column prop="budget" label="预算" align="right" width="120">
                        <template #default="scope">¥ {{ formatCurrency(scope.row.budget) }}</template>
                      </el-table-column>
                      <el-table-column prop="actual" label="实际" align="right" width="120">
                        <template #default="scope">¥ {{ formatCurrency(scope.row.actual) }}</template>
                      </el-table-column>
                      <el-table-column prop="deviation" label="偏差" align="right" width="150">
                        <template #default="scope">
                          <span :style="{ color: scope.row.deviation > 0 ? '#f56c6c' : '#67c23a' }">
                            {{ scope.row.deviation >= 0 ? '+' : '' }}{{ formatCurrency(scope.row.deviation) }}
                          </span>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </div>
              </template>
            </el-table-column>
            
            <!-- 序号列 -->
            <el-table-column 
              label="序号" 
              width="80" 
              align="center"
              fixed="left"
            >
              <template #default="scope">
                <div class="serial-number">
                  {{ scope.$index + 1 }}
                </div>
              </template>
            </el-table-column>
            
            <!-- 项目名称 -->
            <el-table-column 
              prop="name" 
              label="项目名称" 
              sortable
              min-width="200"
            />
            
            <!-- 偏差数据 -->
            <el-table-column 
              label="偏差数据" 
              sortable
              width="180"
              align="right"
            >
              <template #default="scope">
                <span 
                  class="deviation-value"
                  :class="scope.row.deviationAmount > 0 ? 'deviation-over' : 'deviation-under'"
                >
                  {{ scope.row.deviationAmount >= 0 ? '+' : '' }}{{ formatCurrency(scope.row.deviationAmount) }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 项目列表区域 -->
    <el-row style="margin-top: 20px;">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>近期项目Top10</span>
              <el-button type="primary" size="small" @click="navigateToProjects">
                <el-icon><View /></el-icon>
                更多项目
              </el-button>
            </div>
          </template>
          <el-table :data="projectList" style="width: 100%" border>
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
                <el-progress 
                  :percentage="scope.row.progress" 
                  :stroke-width="10" 
                  :show-text="false"
                ></el-progress>
              </template>
            </el-table-column>
            <el-table-column prop="contract_amount" label="合同金额" sortable>
              <template #default="scope">
                ¥ {{ formatCurrency(scope.row.contract_amount) }}
              </template>
            </el-table-column>
            <el-table-column prop="budget_total_cost" label="预算成本" sortable>
              <template #default="scope">
                ¥ {{ formatCurrency(scope.row.budget_total_cost) }}
              </template>
            </el-table-column>
            <el-table-column prop="actual_total_cost" label="实际成本" sortable>
              <template #default="scope">
                ¥ {{ formatCurrency(scope.row.actual_total_cost) }}
              </template>
            </el-table-column>
            <el-table-column prop="leader" label="项目经理" sortable />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button type="primary" size="small" @click="viewProjectDetails(scope.row)">
                  <el-icon><View /></el-icon>
                  详情
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
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { Plus, View } from '@element-plus/icons-vue'
import { getProjectOverviewStatistics, getProjects, getAllTasks } from '../../api/project'
import request from '../../api/axios'

// 定义类型
interface Project {
  id: number
  name: string
  status: string
  progress: number
  contract_amount: number
  budget_total_cost: number
  actual_total_cost: number
  leader: string
  created_at: string
}

interface StatusDistributionItem {
  name: string
  value: number
}

interface EmployeeWorkload {
  name: string
  actual_hours: number
}

interface DelayedTask {
  task_id: number
  project_id: number
  task_name: string
  assignee: string
  start_date: string
  end_date: string
  actual_end_date: string | null
  difdays: number
}

interface DashboardData {
  totalProjects: number
  totalContractAmount: number
  totalBudgetCost: number
  totalActualCost: number
  costVariance: number
  statusDistribution: StatusDistributionItem[]
  delayedTasks: DelayedTask[]
  costTrend: any[]
  projectDeviation: any[]
  employeeWorkload: EmployeeWorkload[]
}

// 看板数据
const dashboardData = ref<DashboardData>({
  totalProjects: 0,
  totalContractAmount: 0,
  totalBudgetCost: 0,
  totalActualCost: 0,
  costVariance: 0,
  statusDistribution: [],
  delayedTasks: [],
  costTrend: [],
  projectDeviation: [], // 项目预算与实际偏差排名数据
  employeeWorkload: [] // 人员工作量分布数据
})

// 项目列表数据
const projectList = ref<Project[]>([])

// 图表引用和实例
const statusChart = ref<HTMLElement | null>(null)
const progressChart = ref<HTMLElement | null>(null)
const costTrendChart = ref<HTMLElement | null>(null)
const workloadChart = ref<HTMLElement | null>(null)
const statusChartInstance = ref<echarts.ECharts | null>(null)
const progressChartInstance = ref<echarts.ECharts | null>(null)
const costTrendChartInstance = ref<echarts.ECharts | null>(null)
const workloadChartInstance = ref<echarts.ECharts | null>(null)

// 简化项目名称函数
const truncateProjectName = (name: string, maxLength: number = 10) => {
  if (!name || name.length <= maxLength) {
    return name
  }
  return name.substring(0, maxLength) + '...'
}

// 初始化router
const router = useRouter()

// 加载状态
const loading = ref(false)

// 格式化金额为金融风格
const formatCurrency = (amount: number | undefined) => {
  const numAmount = Number(amount || 0)
  return numAmount.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// 根据状态获取标签类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    '规划中': 'info',
    '进行中': 'primary',
    '已完成': 'success',
    '提前完成': 'success',
    '延期完成': 'warning',
    '已延期': 'warning',
    '已暂停': 'warning',
    '已取消': 'danger'
  }
  return statusMap[status] || 'default'
}

// 查看项目详情
const viewProjectDetails = (row: Project) => {
  router.push(`/projects/${row.id}`)
}

// 跳转到项目管理列表页面
const navigateToProjects = () => {
  router.push('/projects')
}

// 获取人员工作量数据
const fetchEmployeeWorkload = async () => {
  try {
    const data = await request.get('/api/v1/cost/labor/workload')
    console.log('人员工作量原始数据:', data)
    console.log('数据类型:', typeof data, Array.isArray(data))
    
    // axios拦截器已经修复，现在返回业务数据
    if (Array.isArray(data)) {
      return data
    }
    
    // 如果返回的是完整响应格式，提取data字段
    if (data && data.data && Array.isArray(data.data)) {
      return data.data
    }
    
    return []
  } catch (error) {
    console.error('获取人员工作量数据失败:', error)
    return []
  }
}

// 获取看板数据
const fetchDashboardData = async () => {
  try {
    loading.value = true
        // 调用真实API获取数据
        const statisticsResponse = await getProjectOverviewStatistics()
        // 获取最近10条创建时间最近的项目，用于近期项目显示
        const recentProjectsResponse = await getProjects({ 
          page: 1, 
          size: 10
        })
        // 获取所有项目数据来计算偏差排名，设置一个足够大的size参数
        const projectsResponse = await getProjects({ page: 1, size: 100 }) // 假设项目总数不超过100个
        // 获取所有任务数据来获取实际结束日期
        const tasksResponse = await getAllTasks()
        // 获取人员工作量数据
        const employeeWorkload = await fetchEmployeeWorkload()
        
        // 为每个项目获取第一个任务的实际结束日期
        const getActualEndDate = (projectId: number) => {
          // 确保tasksData是数组格式
          const tasksData = Array.isArray(tasksResponse) ? tasksResponse : 
                           (tasksResponse?.items || tasksResponse?.data || [])
          
          // 从task_id中提取项目ID（格式：projectId_taskId）
          const projectTasks = tasksData.filter(task => {
            const taskIdStr = String(task.task_id || '')
            const taskProjectId = taskIdStr.split('_')[0]
            return Number(taskProjectId) === projectId
          })
          
          // 找到第一个有实际结束日期的任务
          const taskWithActualEndDate = projectTasks.find(task => task.actual_end_date)
          return taskWithActualEndDate?.actual_end_date || null
        }
        
        // 计算项目预算与实际偏差排名和维度占比
        const calculateCostDeviation = (projects: any[]) => {
          // 计算每个项目的预算与实际偏差
          const projectsWithDeviation = projects.map(project => {
            // 确保数值类型正确
            const budgetTotalCost = Number(project.budget_total_cost || 0)
            const actualTotalCost = Number(project.actual_total_cost || 0)
            
            // 计算总偏差金额和偏差率
            const deviationAmount = actualTotalCost - budgetTotalCost
            const deviationRate = budgetTotalCost > 0 ? Math.abs(deviationAmount / budgetTotalCost) : 0
            
            // 计算各维度的预算和实际值
            const materialBudget = Number(project.material_budget || 0)
            const materialActual = Number(project.material_cost || 0)
            const outsourcingBudget = Number(project.outsourcing_budget || 0)
            const outsourcingActual = Number(project.outsourcing_cost || 0)
            const indirectBudget = Number(project.indirect_budget || 0)
            const indirectActual = Number(project.indirect_cost || 0)
            const laborBudget = Number(project.labor_budget || 0)
            const laborActual = Number(project.labor_cost || 0)
            
            // 计算各维度的偏差
            const materialDeviation = materialActual - materialBudget
            const outsourcingDeviation = outsourcingActual - outsourcingBudget
            const indirectDeviation = indirectActual - indirectBudget
            const laborDeviation = laborActual - laborBudget
            
            // 计算各维度占总偏差的比例
            const totalDeviation = Math.abs(deviationAmount)
            const materialRatio = totalDeviation > 0 ? Math.abs(materialDeviation) / totalDeviation : 0
            const outsourcingRatio = totalDeviation > 0 ? Math.abs(outsourcingDeviation) / totalDeviation : 0
            const indirectRatio = totalDeviation > 0 ? Math.abs(indirectDeviation) / totalDeviation : 0
            const laborRatio = totalDeviation > 0 ? Math.abs(laborDeviation) / totalDeviation : 0
            
            // 获取实际结束日期
            const actualEndDate = getActualEndDate(Number(project.id))
            
            return {
              ...project,
              name: project.name || '',
              leader: project.leader || '',
              start_date: project.start_date || '',
              end_date: project['计划结束日期'] || project.end_date || '', // 兼容两种字段名
              actual_end_date: project['实际结束日期'] || project.actual_end_date || null, // 从project_tasks表获取第一个actual_end_date
              budget_total_cost: budgetTotalCost,
              actual_total_cost: actualTotalCost,
              deviationAmount,
              deviationRate,
              // 各维度的预算和实际值
              dimensions: {
                material: { budget: materialBudget, actual: materialActual, deviation: materialDeviation, ratio: materialRatio },
                outsourcing: { budget: outsourcingBudget, actual: outsourcingActual, deviation: outsourcingDeviation, ratio: outsourcingRatio },
                indirect: { budget: indirectBudget, actual: indirectActual, deviation: indirectDeviation, ratio: indirectRatio },
                labor: { budget: laborBudget, actual: laborActual, deviation: laborDeviation, ratio: laborRatio }
              }
            }
          })
          
          // 按偏差金额绝对值从大到小排序，取前10个项目
          return projectsWithDeviation
            .sort((a, b) => Math.abs(b.deviationAmount) - Math.abs(a.deviationAmount))
            .slice(0, 10)
        }
    
    // 计算成本趋势（使用最近项目数据） - 保留原函数，但返回空数组，因为我们将使用新的成本偏差数据
    const calculateCostTrend = (projects: any[]) => {
      return []
    }
    
    // 分析延期任务 - 直接使用后端返回的延期任务数据
    const analyzeDelayedTasks = async () => {
      try {
        // 直接调用getAllTasks API获取后端处理好的延期任务数据
        const response = await getAllTasks()
        
        // 确保tasksData是数组格式
        const tasksData = Array.isArray(response) ? response : 
                         (response?.items || response?.data || [])
        
        // 确保tasks是数组
        if (!Array.isArray(tasksData)) {
          console.error('获取任务列表失败: 返回数据不是数组', response)
          return []
        }
        
        // 处理后端返回的数据，确保字段名与前端期望的一致
        return tasksData.map(task => {
          // 从task_id中提取项目ID（格式：projectId_taskId）
          const taskIdStr = String(task.task_id || '')
          const taskProjectId = taskIdStr.split('_')[0]
          
          return {
            ...task,
            // 确保有必要的字段，避免渲染错误
            id: task.task_id,
            project_id: Number(taskProjectId || 0),
            project_name: task.project_name || '', // 确保project_name存在
            delayDays: Number(task.difdays || 0), // 确保delayDays是数字类型
            // 确保日期字段是字符串，避免后续处理出错
            start_date: task.start_date || '',
            end_date: task.end_date || '',
            actual_end_date: task.actual_end_date || null
          }
        })
      } catch (error) {
        console.error('获取任务列表失败:', error)
        return []
      }
    }
    
    // 计算项目预算与实际偏差排名
    const projectsData = (projectsResponse as any)?.items || projectsResponse || []
    const projectDeviation = calculateCostDeviation(projectsData)
    
    // 更新统计数据
    const delayedTasks = await analyzeDelayedTasks()
    
    // 手动处理Object.entries for ES5 compatibility
    // 修复数据提取逻辑：axios拦截器返回的是 {items: [], total} 格式，需要提取data字段
    const rawResponse = statisticsResponse || {}
    const statisticsData = rawResponse.data || rawResponse || {}
    console.log('原始统计数据响应:', rawResponse)
    console.log('提取的统计对象:', statisticsData)
    
    const statusCounts = statisticsData.status_counts || {}
    console.log('状态计数数据:', statusCounts)
    
    const statusDistribution = []
    for (const name in statusCounts) {
      if (statusCounts.hasOwnProperty(name)) {
        const value = Number(statusCounts[name]) || 0
        console.log(`状态 ${name}: ${value}`)
        if (value > 0) { // 只添加有效的数据
          statusDistribution.push({ name, value })
        }
      }
    }
    
    console.log('处理后的状态分布数据:', statusDistribution)
    
    dashboardData.value = {
      totalProjects: statisticsData.total_projects || 0,
      totalContractAmount: statisticsData.total_contract_amount || 0,
      totalBudgetCost: statisticsData.total_budget_cost || 0,
      totalActualCost: statisticsData.total_actual_cost || 0,
      costVariance: statisticsData.cost_variance || 0,
      statusDistribution: statusDistribution,
      delayedTasks: delayedTasks,
      costTrend: calculateCostTrend(projectsData),
      projectDeviation: projectDeviation,
      employeeWorkload: employeeWorkload
    }
    
    // 更新项目列表数据（仅最近10个）
    const recentProjectsData = (recentProjectsResponse as any)?.items || recentProjectsResponse || []
    projectList.value = recentProjectsData as Project[]
  } catch (error) {
    console.error('获取看板数据失败:', error)
    
    // 错误处理：使用默认数据防止图表崩溃
    dashboardData.value = {
      totalProjects: 0,
      totalContractAmount: 0,
      totalBudgetCost: 0,
      totalActualCost: 0,
      costVariance: 0,
      statusDistribution: [],
      delayedTasks: [],
      costTrend: [],
      projectDeviation: [],
      employeeWorkload: []
    }
    
    projectList.value = []
  } finally {
    loading.value = false
  }
}

// 初始化项目状态分布图表
const initStatusChart = () => {
  if (statusChart.value && !statusChartInstance.value) {
    statusChartInstance.value = echarts.init(statusChart.value)
    
    // 使用真实数据或默认数据，确保数据格式正确
    const rawData = dashboardData.value.statusDistribution || []
    const statusData = Array.isArray(rawData) && rawData.length > 0 
      ? rawData.map(item => ({
          name: item.name || '未知',
          value: Number(item.value) || 0
        })).filter(item => item.value > 0)
      : [{ name: '暂无数据', value: 1 }]
    
    const option = {
      title: {
        text: '项目状态分布',
        left: 'center',
        top: '5%'
      },
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        top: '20%',
        data: statusData.map(item => item.name),
        textStyle: {
          fontSize: 12
        }
      },
      series: [
        {
          name: '项目状态',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 20,
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: statusData
        }
      ]
    }
    statusChartInstance.value.setOption(option)
  }
}

// 初始化延期任务分布图表
const initProgressChart = () => {
  if (progressChart.value && !progressChartInstance.value) {
    progressChartInstance.value = echarts.init(progressChart.value)
    
    // 准备延期任务数据
    const delayedTasks = dashboardData.value.delayedTasks
    const groups: Record<string, number> = {
      '1-7天': 0,
      '8-14天': 0,
      '15-30天': 0,
      '31-60天': 0,
      '60天以上': 0
    }
    
    // 分组统计延期任务
    delayedTasks.forEach(task => {
      const delayDays = Number(task.delayDays || 0)
      if (delayDays <= 7) {
        groups['1-7天']++
      } else if (delayDays <= 14) {
        groups['8-14天']++
      } else if (delayDays <= 30) {
        groups['15-30天']++
      } else if (delayDays <= 60) {
        groups['31-60天']++
      } else {
        groups['60天以上']++
      }
    })
    
    // 手动处理Object.keys and Object.values for ES5 compatibility
    const categories = Object.keys(groups)
    const values: number[] = []
    for (const category of categories) {
      values.push(groups[category])
    }
    
    // 确保有默认数据，防止图表崩溃
    const chartCategories = categories.length > 0 ? categories : ['1-7天', '8-14天', '15-30天', '31-60天', '60天以上']
    const chartValues = values.length > 0 ? values : [0, 0, 0, 0, 0]
    
    const option = {
          title: {
            text: '延期任务分布',
            left: 'center',
            top: '10%'
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'cross' // 十字线类型，适合折线图
            },
            formatter: (params: any) => {
              // 确保显示具体的整数任务数量
              const param = params[0]
              const taskCount = Number(param.value) // 确保是数字类型
              const intTaskCount = taskCount % 1 === 0 ? taskCount : Math.round(taskCount) // 整数直接显示，小数四舍五入
              return `${param.name}<br/>${param.seriesName}: ${intTaskCount}个任务`
            }
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '15%',
            top: '20%',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            data: chartCategories,
            axisLabel: {
              rotate: 0,
              fontSize: 12
            }
          },
          yAxis: {
            type: 'value',
            name: '任务数量',
            nameTextStyle: {
              fontSize: 12
            },
            axisLabel: {
              fontSize: 12
            },
            minInterval: 1 // 确保Y轴刻度为整数
          },
          series: [
            {
              name: '延期任务数',
              type: 'line',
              data: chartValues,
              smooth: true, // 平滑曲线
              lineStyle: {
                color: '#ff4d4f',
                width: 3
              },
              itemStyle: {
                color: '#ff4d4f',
                borderColor: '#fff',
                borderWidth: 2
              },
              emphasis: {
                itemStyle: {
                  color: '#ff4d4f',
                  borderColor: '#fff',
                  borderWidth: 3,
                  shadowBlur: 10,
                  shadowColor: 'rgba(255, 77, 79, 0.5)'
                }
              },
              symbol: 'circle',
              symbolSize: 8,
              label: {
                show: true, // 显示每个点的具体数量
                position: 'top', // 标签位置在点的上方
                formatter: (params: any) => {
                  const value = Number(params.value) // 确保是数字类型
                  const intValue = value % 1 === 0 ? value : Math.round(value) // 整数直接显示，小数四舍五入
                  return `${intValue}` // 只显示数字，不显示单位
                },
                fontSize: 12,
                color: '#333',
                fontWeight: 'bold'
              }
            }
          ]
        }
    progressChartInstance.value.setOption(option)
  }
}

// 初始化人员工作量分布图表
const initWorkloadChart = () => {
  if (workloadChart.value && !workloadChartInstance.value) {
    workloadChartInstance.value = echarts.init(workloadChart.value)
    
    // 确保有默认数据，防止图表崩溃
    let workloadData = dashboardData.value.employeeWorkload || []
    
    // 安全处理数据
    if (!Array.isArray(workloadData)) {
      workloadData = []
    }
    
    // 准备图表数据
    const employeeNames = workloadData.map(item => item?.name || '未知')
    const actualHours = workloadData.map(item => Number(item?.actual_hours) || 0)
    
    if (workloadData.length === 0) {
      console.log('没有人员工作量数据，显示为空')
    } else {
      console.log('使用真实的人员工作量数据:', workloadData)
    }
    
    const option = {
      title: {
        text: '人员工作量分布',
        left: 'center',
        top: '5%'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: (params: any) => {
          const param = Array.isArray(params) ? params[0] : params
          return `${param?.name || ''}<br/>实际工时: ${param?.value || 0}小时`
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        top: '20%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: employeeNames,
        axisLabel: {
          rotate: 45,
          fontSize: 12,
          interval: 0
        }
      },
      yAxis: {
        type: 'value',
        name: '实际工时 (小时)',
        nameTextStyle: {
          fontSize: 12
        },
        axisLabel: {
          fontSize: 12
        },
        minInterval: 1
      },
      series: [
        {
          name: '实际工时',
          type: 'bar',
          data: actualHours,
          itemStyle: {
            color: '#1890ff'
          },
          label: {
            show: true,
            position: 'top',
            formatter: '{c}h',
            fontSize: 10,
            color: '#333'
          }
        }
      ],
      animationDuration: 1000
    }
    workloadChartInstance.value.setOption(option)
  }
}

// 初始化成本偏差排名图表
const initCostTrendChart = () => {
  if (costTrendChart.value && !costTrendChartInstance.value) {
    costTrendChartInstance.value = echarts.init(costTrendChart.value)
    
    // 确保有默认数据，防止图表崩溃
    const projectDeviationData = dashboardData.value.projectDeviation || []
    
    // 如果没有项目偏差数据，提供默认数据
    const chartData = projectDeviationData.length > 0 ? projectDeviationData : [
      {
        name: '默认项目1',
        deviationAmount: 50000,
        budget_total_cost: 100000,
        actual_total_cost: 150000,
        dimensions: {
          material: { deviation: 20000, ratio: 0.4 },
          outsourcing: { deviation: 15000, ratio: 0.3 },
          indirect: { deviation: 10000, ratio: 0.2 },
          labor: { deviation: 5000, ratio: 0.1 }
        }
      }
    ]
    
    // 准备图表数据
    const projectNames = chartData.map(item => truncateProjectName(item.name, 8))
    const materialDeviation = chartData.map(item => Math.abs(item.dimensions.material.deviation))
    const outsourcingDeviation = chartData.map(item => Math.abs(item.dimensions.outsourcing.deviation))
    const indirectDeviation = chartData.map(item => Math.abs(item.dimensions.indirect.deviation))
    const laborDeviation = chartData.map(item => Math.abs(item.dimensions.labor.deviation))
    
    // 计算Y轴的最大值，确保柱状图有合适的高度
    const totalDeviations = chartData.map(project => {
      return Math.abs(project.deviationAmount)
    })
    const maxDeviation = Math.max(...totalDeviations, 0)
    const yAxisMax = maxDeviation * 1.2 // 留20%的余量，使图表更美观
    
    const option = {
      title: {
        text: '成本偏差排名Top10',
        left: 'center',
        top: '5%'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: (params: any) => {
          // 获取当前项目数据
          const projectIndex = params[0].dataIndex
          const projectData = chartData[projectIndex]
          const deviationAmount = projectData.deviationAmount
          const deviationType = deviationAmount >= 0 ? '超支' : '节约'
          const deviationRate = (Math.abs(deviationAmount) / projectData.budget_total_cost * 100).toFixed(2)
          
          // 构建tooltip内容
          let tooltipContent = `${projectData.name}<br/>`
          tooltipContent += `总偏差: ${deviationType} ${formatCurrency(Math.abs(deviationAmount))} (${deviationRate}%)<br/>`
          tooltipContent += `预算: ${formatCurrency(projectData.budget_total_cost)}<br/>`
          tooltipContent += `实际: ${formatCurrency(projectData.actual_total_cost)}<br/><br/>`
          tooltipContent += '各维度偏差占比:<br/>'
          
          // 遍历各维度数据
          params.forEach((param: any) => {
            const dimensionName = {
              '物料/设备': 'material',
              '外包服务': 'outsourcing',
              '间接成本': 'indirect',
              '人力成本': 'labor'
            }[param.seriesName]
            
            if (dimensionName) {
              const dimensionData = projectData.dimensions[dimensionName]
              const ratio = (dimensionData.ratio * 100).toFixed(1)
              tooltipContent += `${param.seriesName}: ${formatCurrency(Math.abs(dimensionData.deviation))} (${ratio}%)<br/>`
            }
          })
          
          return tooltipContent
        }
      },
      legend: {
        data: ['物料/设备', '外包服务', '间接成本', '人力成本'],
        bottom: '5%',
        left: 'center',
        textStyle: {
          fontSize: 12
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '30%',
        top: '25%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: projectNames,
        axisLabel: {
          rotate: 30,
          fontSize: 10,
          interval: 0,
          formatter: (value: string) => {
            // 进一步缩短项目名称，确保显示完整
            return value.length > 6 ? value.substring(0, 6) + '...' : value
          }
        }
      },
      yAxis: {
        type: 'value',
        name: '偏差金额 (元)',
        nameTextStyle: {
          fontSize: 12
        },
        max: yAxisMax,
        axisLabel: {
          fontSize: 12,
          formatter: (value: number) => {
            if (value >= 10000) {
              return (value / 10000).toFixed(1) + '万'
            }
            return value.toString()
          }
        }
      },
      series: [
        {
          name: '物料/设备',
          type: 'bar',
          stack: 'total',
          data: materialDeviation,
          itemStyle: {
            color: '#1890ff'
          }
        },
        {
          name: '外包服务',
          type: 'bar',
          stack: 'total',
          data: outsourcingDeviation,
          itemStyle: {
            color: '#52c41a'
          }
        },
        {
          name: '间接成本',
          type: 'bar',
          stack: 'total',
          data: indirectDeviation,
          itemStyle: {
            color: '#faad14'
          }
        },
        {
          name: '人力成本',
          type: 'bar',
          stack: 'total',
          data: laborDeviation,
          itemStyle: {
            color: '#f56c6c'
          },
          label: {
            show: true,
            position: 'top',
            formatter: (params: any) => {
              const projectIndex = params.dataIndex
              const projectData = chartData[projectIndex]
              const deviationAmount = projectData?.deviationAmount || 0
              return formatCurrency(Math.abs(deviationAmount))
            },
            fontSize: 9,
            color: '#333',
            fontWeight: 'bold',
            overflow: 'breakAll',
            textBorderColor: '#fff',
            textBorderWidth: 2
          }
        }
      ]
    }
    costTrendChartInstance.value.setOption(option)
  }
}

// 初始化图表
const initCharts = () => {
  initStatusChart()
  initProgressChart()
  initWorkloadChart()
  initCostTrendChart()
}

// 调整图表大小
const resizeCharts = () => {
  statusChartInstance.value?.resize()
  progressChartInstance.value?.resize()
  workloadChartInstance.value?.resize()
  costTrendChartInstance.value?.resize()
}

// 销毁图表
const destroyCharts = () => {
  statusChartInstance.value?.dispose()
  progressChartInstance.value?.dispose()
  workloadChartInstance.value?.dispose()
  costTrendChartInstance.value?.dispose()
  statusChartInstance.value = null
  progressChartInstance.value = null
  workloadChartInstance.value = null
  costTrendChartInstance.value = null
}

// 监听窗口大小变化
const handleResize = () => {
  resizeCharts()
}

// 刷新数据
const refreshData = async () => {
  await fetchDashboardData()
  // 销毁旧图表实例
  destroyCharts()
  // 重新初始化图表，使用新数据
  setTimeout(() => {
    initCharts()
  }, 0)
}

// 监听dashboardData变化，更新图表
watch(() => dashboardData.value, () => {
  // 更新项目状态分布图表
  if (statusChartInstance.value) {
    const rawData = dashboardData.value.statusDistribution || []
    const statusData = Array.isArray(rawData) && rawData.length > 0 
      ? rawData.map(item => ({
          name: item.name || '未知',
          value: Number(item.value) || 0
        })).filter(item => item.value > 0)
      : [{ name: '暂无数据', value: 1 }]
    
    statusChartInstance.value.setOption({
      legend: {
        data: statusData.map(item => item.name)
      },
      series: [
        {
          data: statusData
        }
      ]
    })
  }
  
  // 更新延期任务分布图表
  if (progressChartInstance.value) {
    // 重新计算延期任务分组
    const delayedTasks = dashboardData.value.delayedTasks
    const groups: Record<string, number> = {
      '1-7天': 0,
      '8-14天': 0,
      '15-30天': 0,
      '31-60天': 0,
      '60天以上': 0
    }
    
    delayedTasks.forEach(task => {
      // 确保delayDays是数字，避免NaN导致的问题
      const delayDays = Number(task.difdays || 0)
      if (delayDays <= 7) {
        groups['1-7天']++
      } else if (delayDays <= 14) {
        groups['8-14天']++
      } else if (delayDays <= 30) {
        groups['15-30天']++
      } else if (delayDays <= 60) {
        groups['31-60天']++
      } else {
        groups['60天以上']++
      }
    })
    
    const categories = Object.keys(groups)
    // 手动处理Object.values for ES5 compatibility
    const values: number[] = []
    for (const category of categories) {
      values.push(groups[category])
    }
    
    progressChartInstance.value.setOption({
      xAxis: {
        data: categories
      },
      series: [
        {
          name: '延期任务数',
          type: 'line',
          data: values
        }
      ]
    })
  }
  
  // 更新人员工作量分布图表
  if (workloadChartInstance.value) {
    let workloadData = dashboardData.value.employeeWorkload || []
    
    if (!Array.isArray(workloadData)) {
      workloadData = []
    }
    
    const employeeNames = workloadData.map(item => item?.name || '未知')
    const actualHours = workloadData.map(item => Number(item?.actual_hours) || 0)
    
    workloadChartInstance.value.setOption({
      xAxis: {
        data: employeeNames
      },
      series: [
        {
          name: '实际工时',
          type: 'bar',
          data: actualHours
        }
      ]
    })
  }
  
  // 更新项目成本偏差排名图表
  if (costTrendChartInstance.value) {
    const projectDeviationData = dashboardData.value.projectDeviation || []
    
    // 如果没有项目偏差数据，提供默认数据
    const chartData = projectDeviationData.length > 0 ? projectDeviationData : [
      {
        name: '默认项目1',
        deviationAmount: 50000,
        budget_total_cost: 100000,
        actual_total_cost: 150000,
        dimensions: {
          material: { deviation: 20000, ratio: 0.4 },
          outsourcing: { deviation: 15000, ratio: 0.3 },
          indirect: { deviation: 10000, ratio: 0.2 },
          labor: { deviation: 5000, ratio: 0.1 }
        }
      }
    ]
    
    // 准备图表数据
    const projectNames = chartData.map(item => item.name)
    const materialDeviation = chartData.map(item => Math.abs(item.dimensions.material.deviation))
    const outsourcingDeviation = chartData.map(item => Math.abs(item.dimensions.outsourcing.deviation))
    const indirectDeviation = chartData.map(item => Math.abs(item.dimensions.indirect.deviation))
    const laborDeviation = chartData.map(item => Math.abs(item.dimensions.labor.deviation))
    const totalDeviations = chartData.map(item => Math.abs(item.deviationAmount))
    
    // 完整更新图表配置，包括重新设置tooltip和label formatter
    costTrendChartInstance.value.setOption({
      xAxis: {
        data: projectNames
      },
      series: [
        {
          name: '物料/设备',
          type: 'bar',
          stack: 'total',
          data: materialDeviation
        },
        {
          name: '外包服务',
          type: 'bar',
          stack: 'total',
          data: outsourcingDeviation
        },
        {
          name: '间接成本',
          type: 'bar',
          stack: 'total',
          data: indirectDeviation
        },
        {
          name: '人力成本',
          type: 'bar',
          stack: 'total',
          data: laborDeviation,
          label: {
            show: true,
            position: 'top',
            formatter: (params: any) => {
              const projectIndex = params.dataIndex
              const projectData = chartData[projectIndex]
              const deviationAmount = projectData?.deviationAmount || 0
              return formatCurrency(Math.abs(deviationAmount))
            },
            fontSize: 9,
            color: '#333',
            fontWeight: 'bold',
            overflow: 'breakAll',
            textBorderColor: '#fff',
            textBorderWidth: 2
          }
        }
      ]
    })
  }
}, { deep: true })

// 组件挂载时初始化
onMounted(() => {
  fetchDashboardData()
  // 延迟初始化图表，确保数据已获取
  setTimeout(() => {
    initCharts()
    // 监听窗口大小变化，调整图表大小
    window.addEventListener('resize', handleResize)
  }, 100)
})

// 组件卸载时销毁图表和事件监听
onUnmounted(() => {
  destroyCharts()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-card {
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.stat-title {
  font-weight: bold;
  color: #606266;
  margin-bottom: 10px;
}

.stat-value {
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

.stat-desc {
  color: #909399;
}

.stat-value-negative {
  color: #f56c6c;
}

.stat-value-positive {
  color: #67c23a;
}

.chart-container {
  width: 100%;
}

.chart-card {
  transition: transform 0.3s, box-shadow 0.3s;
}

.chart-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.no-projects {
  text-align: center;
  padding: 20px;
  color: #909399;
}

/* 成本偏差排名表样式 */
.deviation-ranking-card {
  transition: transform 0.3s, box-shadow 0.3s;
}

.deviation-ranking-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

/* 序号样式 */
.serial-number {
  font-weight: bold;
  color: #409eff;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  background-color: #ecf5ff;
  border-radius: 50%;
  margin: 0 auto;
}

/* 偏差数据样式 */
.deviation-value {
  font-weight: bold;
  font-size: 14px;
}

.deviation-over {
  color: #f56c6c;
}

.deviation-under {
  color: #67c23a;
}

/* 展开内容样式 */
.expanded-content {
  background-color: #fafafa;
  padding: 15px;
  border-radius: 4px;
  margin: 10px 0;
}

/* 项目基本信息样式 */
.project-basic-info h4,
.cost-dimension-details h4 {
  color: #303133;
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.project-basic-info {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.info-item {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.info-label {
  width: 120px;
  font-weight: bold;
  color: #606266;
}

.info-value {
  color: #303133;
  flex: 1;
}

/* 成本维度详情样式 */
.cost-dimension-details {
  margin-top: 15px;
}

/* 确保表格行高适中 */
:deep(.el-table__row) {
  height: 50px;
}

:deep(.el-table__expanded-cell) {
  padding: 10px;
  background-color: #fafafa;
}

:deep(.el-table__expand-icon) {
  color: #409eff;
  font-size: 16px;
}

:deep(.el-table__expand-icon--expanded) {
  color: #67c23a;
}

/* 确保展开内容中的表格样式统一 */
:deep(.expanded-content .el-table) {
  background-color: transparent;
}

:deep(.expanded-content .el-table__header-wrapper) {
  background-color: #f0f2f5;
}

:deep(.expanded-content .el-table__body-wrapper) {
  background-color: #ffffff;
}

:deep(.expanded-content .el-table th) {
  font-weight: bold;
  color: #606266;
  background-color: #f0f2f5;
}
</style>