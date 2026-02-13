<template>
  <div class="cost-analysis-container">
    <h1>成本分析</h1>
    
    <el-row :gutter="10" style="margin-bottom: 20px;" align="middle">
      <el-col :span="2">
        <span style="font-size: 14px; color: #606266; white-space: nowrap; float: right; line-height: 32px;">项目名称</span>
      </el-col>
      <el-col :span="4">
        <el-select
          v-model="selectedProject"
          placeholder="输入项目名称搜索"
          style="width: 100%;"
          filterable
          clearable
          remote
          :remote-method="filterProjects"
          :loading="loadingProjects"
          @change="onProjectChange"
        >
          <el-option
            v-for="project in filteredProjects"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          >
            <span>{{ project.name }}</span>
            <span style="float: right; color: #8492a6; font-size: 12px;">
              {{ project.leader }} | {{ project.status }}
            </span>
          </el-option>
        </el-select>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-title">总预算</div>
            <div class="stat-value">{{ formatCurrency(totalBudget) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-title">已用成本</div>
            <div class="stat-value">{{ formatCurrency(totalActual) }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-title">剩余预算</div>
            <div class="stat-value" :style="{ color: remainingBudget < 0 ? '#f56c6c' : '#1890ff' }">
              {{ formatCurrency(remainingBudget) }}
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-title">预算执行率</div>
            <div class="stat-value" :style="{ color: budgetExecutionRate > 100 ? '#f56c6c' : budgetExecutionRate > 90 ? '#e6a23c' : '#67c23a' }">
              {{ budgetExecutionRate }}%
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>成本分类分布</span>
            </div>
          </template>
          <div ref="costCategoryChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>预算 vs 实际</span>
            </div>
          </template>
          <div ref="budgetActualChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card shadow="hover" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>成本明细</span>
          <el-radio-group v-model="costTypeFilter" size="small" @change="loadCostDetails">
            <el-radio-button label="">全部</el-radio-button>
            <el-radio-button label="物料成本">物料成本</el-radio-button>
            <el-radio-button label="人力成本">人力成本</el-radio-button>
            <el-radio-button label="外包成本">外包成本</el-radio-button>
            <el-radio-button label="间接成本">间接成本</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <el-table :data="costDetails" style="width: 100%" v-loading="loadingDetails">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="cost_type" label="成本类型" width="100">
          <template #default="scope">
            <el-tag :type="getCostTypeTag(scope.row.cost_type)" size="small">
              {{ scope.row.cost_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
        <el-table-column prop="amount" label="金额" width="130" align="right">
          <template #default="scope">
            <span :style="{ color: scope.row.amount > 10000 ? '#f56c6c' : '#67c23a' }">
              {{ formatCurrency(scope.row.amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="date" label="日期" width="160" />
      </el-table>
      
      <div style="margin-top: 10px; text-align: right;">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalDetails"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { getProjects, type Project } from '../../api/project'
import { 
  getCostOverview, 
  getChartData, 
  getCostDetails,
  type CostOverview,
  type ChartData,
  type CostDetail
} from '../../api/costAnalysis'

const projects = ref<Project[]>([])
const filteredProjects = ref<Project[]>([])
const selectedProject = ref<number | null>(null)
const loadingProjects = ref(false)
const costTypeFilter = ref('')

const totalBudget = ref(0)
const totalActual = ref(0)
const remainingBudget = ref(0)
const budgetExecutionRate = ref(0)

const loadingDetails = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalDetails = ref(0)

const costDetails = ref<CostDetail[]>([])

const costCategoryChart = ref<HTMLElement | null>(null)
const budgetActualChart = ref<HTMLElement | null>(null)
let categoryChartInstance: echarts.ECharts | null = null
let budgetChartInstance: echarts.ECharts | null = null

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  }).format(value)
}

const getCostTypeTag = (type: string): string => {
  const typeMap: Record<string, string> = {
    '物料成本': '',
    '人力成本': 'success',
    '外包成本': 'warning',
    '间接成本': 'info'
  }
  return typeMap[type] || ''
}

const filterProjects = (query: string) => {
  if (query) {
    filteredProjects.value = projects.value.filter(project =>
      project.name.toLowerCase().includes(query.toLowerCase())
    )
  } else {
    filteredProjects.value = projects.value
  }
}

const loadProjects = async () => {
  loadingProjects.value = true
  try {
    const response = await getProjects({ page: 1, size: 100 })
    if (response.items && response.items.length > 0) {
      projects.value = response.items
      filteredProjects.value = response.items
      selectedProject.value = response.items[0].id
      await loadCostOverview()
    }
  } catch (error) {
    console.error('加载项目列表失败:', error)
    ElMessage.error('加载项目列表失败')
  } finally {
    loadingProjects.value = false
  }
}

const loadCostOverview = async () => {
  if (!selectedProject.value) return
  
  try {
    console.log('🔍 成本概览: 开始加载，project_id:', selectedProject.value)
    const response = await getCostOverview(selectedProject.value)
    console.log('🔍 成本概览: API响应原始数据:', response)
    
    // 处理后端统一响应格式 {code, data, message}
    let data: any
    if (response && typeof response === 'object' && 'data' in response) {
      console.log('🔍 成本概览: 检测到标准响应格式，提取data字段')
      data = response.data
    } else {
      console.log('🔍 成本概览: 直接数据格式')
      data = response
    }
    
    let overview: CostOverview | undefined
    
    if (Array.isArray(data)) {
      console.log('🔍 成本概览: data是数组，长度:', data.length)
      overview = data.find((item: CostOverview) => item.project_id === selectedProject.value)
      console.log('🔍 成本概览: 筛选结果:', overview)
    } else {
      console.log('🔍 成本概览: data是对象')
      overview = data as CostOverview
    }
    
    if (overview) {
      console.log('🔍 成本概览: 数据有效，开始设置')
      totalBudget.value = overview.total_budget || 0
      totalActual.value = overview.total_actual || 0
      remainingBudget.value = overview.remaining_budget || 0
      budgetExecutionRate.value = overview.budget_execution_rate || 0
      console.log('🔍 成本概览: 设置完成，totalBudget:', totalBudget.value)
      await loadChartData()
      await loadCostDetails()
    } else {
      console.warn('⚠️ 成本概览: 未找到匹配的概览数据')
      totalBudget.value = 0
      totalActual.value = 0
      remainingBudget.value = 0
      budgetExecutionRate.value = 0
    }
  } catch (error) {
    console.error('❌ 成本概览: 加载失败:', error)
    totalBudget.value = 0
    totalActual.value = 0
    remainingBudget.value = 0
    budgetExecutionRate.value = 0
  }
}

const loadChartData = async () => {
  if (!selectedProject.value) return
  
  try {
    console.log('📊 图表数据: 开始加载，project_id:', selectedProject.value)
    const response = await getChartData(selectedProject.value) as ChartData
    console.log('📊 图表数据: API响应:', response)
    
    // 处理后端统一响应格式
    let data: any
    if (response && typeof response === 'object' && 'data' in response) {
      console.log('📊 图表数据: 检测到标准响应格式，提取data字段')
      data = response.data
    } else {
      console.log('📊 图表数据: 直接数据格式')
      data = response
    }
    
    if (categoryChartInstance && data && data.pie_chart) {
      console.log('📊 图表数据: 设置饼图，pie_chart数据:', data.pie_chart)
      categoryChartInstance.setOption({
        tooltip: {
          trigger: 'item',
          formatter: (params: any) => {
            return `${params.name}: ${formatCurrency(params.value)} (${params.percent}%)`
          }
        },
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        series: [
          {
            name: '成本分类',
            type: 'pie',
            radius: '50%',
            data: data.pie_chart,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            label: {
              formatter: '{b}: {d}%'
            }
          }
        ]
      })
      console.log('📊 图表数据: 饼图设置完成')
    }
    
    if (budgetChartInstance && data && data.bar_chart) {
      console.log('📊 图表数据: 设置柱状图，bar_chart数据:', data.bar_chart)
      budgetChartInstance.setOption({
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: (params: any) => {
            let result = `${params[0].name}<br/>`
            params.forEach((param: any) => {
              result += `${param.marker} ${param.seriesName}: ${formatCurrency(param.value)}<br/>`
            })
            return result
          }
        },
        legend: {
          data: ['预算', '实际']
        },
        xAxis: {
          type: 'category',
          data: data.bar_chart.categories,
          axisLabel: {
            interval: 0,
            rotate: 30
          }
        },
        yAxis: {
          type: 'value',
          name: '金额 (元)',
          axisLabel: {
            formatter: (value: number) => formatCurrency(value)
          }
        },
        series: [
          {
            name: '预算',
            type: 'bar',
            data: data.bar_chart.budget,
            itemStyle: {
              color: '#409EFF'
            },
            label: {
              show: true,
              position: 'top',
              formatter: (params: any) => formatCurrency(params.value)
            }
          },
          {
            name: '实际',
            type: 'bar',
            data: data.bar_chart.actual,
            itemStyle: {
              color: '#F56C6C'
            },
            label: {
              show: true,
              position: 'top',
              formatter: (params: any) => formatCurrency(params.value)
            }
          }
        ]
      })
      console.log('📊 图表数据: 柱状图设置完成')
    }
  } catch (error) {
    console.error('❌ 加载图表数据失败:', error)
    ElMessage.error('加载图表数据失败')
  }
}

const loadCostDetails = async () => {
  if (!selectedProject.value) return
  
  loadingDetails.value = true
  try {
    console.log('📋 成本明细: 开始加载，project_id:', selectedProject.value)
    const response = await getCostDetails(
      selectedProject.value,
      costTypeFilter.value || undefined,
      (currentPage.value - 1) * pageSize.value,
      pageSize.value
    )
    console.log('📋 成本明细: API响应:', response)
    
    // 处理后端统一响应格式
    let data: any
    if (response && typeof response === 'object' && 'data' in response) {
      console.log('📋 成本明细: 检测到标准响应格式，提取data字段')
      data = response.data
    } else {
      console.log('📋 成本明细: 直接数据格式')
      data = response
    }
    
    costDetails.value = data.items || []
    totalDetails.value = data.total || 0
    console.log('📋 成本明细: 设置完成，条目数:', costDetails.value.length, '总数:', totalDetails.value)
  } catch (error) {
    console.error('❌ 加载成本明细失败:', error)
    ElMessage.error('加载成本明细失败')
  } finally {
    loadingDetails.value = false
  }
}

const initCharts = () => {
  if (costCategoryChart.value) {
    categoryChartInstance = echarts.init(costCategoryChart.value)
  }
  
  if (budgetActualChart.value) {
    budgetChartInstance = echarts.init(budgetActualChart.value)
  }
}

const onProjectChange = async () => {
  currentPage.value = 1
  console.log('🎯 项目选择: 开始加载成本概览...')
  await loadCostOverview()
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  loadCostDetails()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadCostDetails()
}

const handleResize = () => {
  categoryChartInstance?.resize()
  budgetChartInstance?.resize()
}

onMounted(async () => {
  await loadProjects()
  initCharts()
  
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.cost-analysis-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100%;
}

h1 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #303133;
}

.stat-card {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-content {
  text-align: center;
  width: 100%;
}

.stat-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #1890ff;
}

.chart-card {
  height: 420px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  width: 100%;
  height: 360px;
}

:deep(.el-select .el-select-dropdown__item) {
  height: auto;
  padding: 8px 12px;
}

:deep(.el-select .el-select-dropdown__item span) {
  display: block;
}
</style>
