<template>
  <div class="daily-report-analysis">
    <!-- 页面标题和筛选器 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">日报数据分析</h1>
        <p class="page-subtitle">基于已提交日报数据的汇总分析</p>
      </div>
      <div class="header-controls">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          unlink-panels
          @change="handleDateRangeChange"
          style="width: 300px;"
        />
        <el-select 
          v-model="selectedProject" 
          placeholder="选择项目" 
          clearable 
          filterable
          :filter-method="filterProjects"
          style="width: 250px;"
        >
          <el-option
            v-for="project in filteredProjectList"
            :key="project.project_id"
            :label="project.project_name"
            :value="project.project_id"
          />
        </el-select>
        <el-button type="primary" @click="refreshAnalysis" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 分析概览卡片 -->
    <div class="overview-cards">
      <div class="metric-card">
        <div class="metric-icon total-hours">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="metric-content">
          <div class="metric-value">{{ formatNumber(overviewStats.totalHours) }}</div>
          <div class="metric-label">总工时投入</div>
          <div class="metric-change positive">{{ overviewStats.hoursChange }}</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon projects">
          <el-icon><FolderOpened /></el-icon>
        </div>
        <div class="metric-content">
          <div class="metric-value">{{ overviewStats.activeProjects }}</div>
          <div class="metric-label">活跃项目数</div>
          <div class="metric-change">{{ overviewStats.projectChange }}</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon tasks">
          <el-icon><List /></el-icon>
        </div>
        <div class="metric-content">
          <div class="metric-value">{{ overviewStats.completedTasks }}</div>
          <div class="metric-label">已完成任务</div>
          <div class="metric-change positive">{{ overviewStats.taskChange }}</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon efficiency">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="metric-content">
          <div class="metric-value">{{ overviewStats.efficiencyRate }}%</div>
          <div class="metric-label">平均效率</div>
          <div class="metric-change" :class="{ positive: overviewStats.efficiencyTrend > 0, negative: overviewStats.efficiencyTrend < 0 }">
            {{ overviewStats.efficiencyTrend > 0 ? '↗' : '↘' }} {{ Math.abs(overviewStats.efficiencyTrend) }}%
          </div>
        </div>
      </div>
    </div>

    <!-- 分析图表区域 -->
    <div class="charts-section">
      <el-row :gutter="20">
        <!-- 工时趋势图 -->
        <el-col :span="12">
          <div class="chart-container">
            <div class="chart-header">
              <h3>工时投入趋势</h3>
              <div class="chart-controls">
                <el-radio-group v-model="hoursChartType" size="small">
                  <el-radio-button label="day">按日</el-radio-button>
                  <el-radio-button label="week">按周</el-radio-button>
                  <el-radio-button label="month">按月</el-radio-button>
                </el-radio-group>
              </div>
            </div>
            <div class="chart-content">
              <div ref="hoursChartRef" class="chart-canvas"></div>
            </div>
          </div>
        </el-col>

        <!-- 项目工时分布 -->
        <el-col :span="12">
          <div class="chart-container">
            <div class="chart-header">
              <h3>项目工时分布</h3>
              <div class="chart-controls">
                <el-dropdown @command="changeProjectChartType">
                  <span class="el-dropdown-link">
                    {{ projectChartType === 'pie' ? '饼图' : '柱状图' }}
                    <el-icon><ArrowDown /></el-icon>
                  </span>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="pie">饼图</el-dropdown-item>
                      <el-dropdown-item command="bar">柱状图</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
            <div class="chart-content">
              <div ref="projectChartRef" class="chart-canvas"></div>
            </div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <!-- 人员工时排名 -->
        <el-col :span="12">
          <div class="chart-container">
            <div class="chart-header">
              <h3>人员工时排名</h3>
              <div class="chart-controls">
                <el-select v-model="employeeTopN" size="small" style="width: 80px;">
                  <el-option label="Top 5" :value="5" />
                  <el-option label="Top 10" :value="10" />
                  <el-option label="Top 15" :value="15" />
                </el-select>
              </div>
            </div>
            <div class="chart-content">
              <div ref="employeeChartRef" class="chart-canvas"></div>
            </div>
          </div>
        </el-col>

        <!-- 任务完成率分析 -->
        <el-col :span="12">
          <div class="chart-container">
            <div class="chart-header">
              <h3>任务完成率分析</h3>
              <div class="chart-controls">
                <el-tag :type="completionRateType">{{ completionRate }}%</el-tag>
              </div>
            </div>
            <div class="chart-content">
              <div ref="completionChartRef" class="chart-canvas"></div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 详细数据表格 -->
    <div class="data-tables-section">
      <el-row :gutter="20">
        <!-- 项目工时明细 -->
        <el-col :span="12">
          <div class="table-container">
            <div class="table-header">
              <h3>项目工时明细</h3>
              <div class="table-controls">
                <el-button size="small" @click="exportProjectData">
                  <el-icon><Download /></el-icon>
                  导出
                </el-button>
              </div>
            </div>
            <el-table 
              :data="projectDetailData" 
              stripe 
              style="width: 100%"
              :height="400"
            >
              <el-table-column prop="project_name" label="项目名称" min-width="120" />
              <el-table-column prop="total_hours" label="总工时" width="80">
                <template #default="{ row }">
                  {{ formatNumber(row.total_hours) }}h
                </template>
              </el-table-column>
              <el-table-column prop="employee_count" label="参与人数" width="80" />
              <el-table-column prop="avg_hours_per_employee" label="人均工时" width="90">
                <template #default="{ row }">
                  {{ formatNumber(row.avg_hours_per_employee) }}h
                </template>
              </el-table-column>
              <el-table-column prop="completion_rate" label="完成率" width="80">
                <template #default="{ row }">
                  <el-progress 
                    :percentage="row.completion_rate" 
                    :color="getProgressColor(row.completion_rate)"
                    :stroke-width="8"
                    :show-text="false"
                  />
                  <span style="margin-left: 8px;">{{ row.completion_rate }}%</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-col>

        <!-- 人员工作明细 -->
        <el-col :span="12">
          <div class="table-container">
            <div class="table-header">
              <h3>人员工作明细</h3>
              <div class="table-controls">
                <el-button size="small" @click="exportEmployeeData">
                  <el-icon><Download /></el-icon>
                  导出
                </el-button>
              </div>
            </div>
            <el-table 
              :data="employeeDetailData" 
              stripe 
              style="width: 100%"
              :height="400"
            >
              <el-table-column prop="employee_name" label="姓名" width="100" />
              <el-table-column prop="total_hours" label="总工时" width="80">
                <template #default="{ row }">
                  {{ formatNumber(row.total_hours) }}h
                </template>
              </el-table-column>
              <el-table-column prop="projects_count" label="参与项目" width="80" />
              <el-table-column prop="tasks_count" label="完成任务" width="80" />
              <el-table-column prop="efficiency_score" label="效率评分" width="80">
                <template #default="{ row }">
                  <el-rate 
                    v-model="row.efficiency_score" 
                    disabled 
                    show-score 
                    text-color="#ff9900"
                    score-template="{value}分"
                  />
                </template>
              </el-table-column>
              <el-table-column label="工作负荷" width="100">
                <template #default="{ row }">
                  <el-tag :type="getWorkloadType(row.workload_level)">
                    {{ row.workload_level }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Clock,
  FolderOpened,
  List,
  TrendCharts,
  ArrowDown,
  Download
} from '@element-plus/icons-vue'
import {
  getAnalysisOverview,
  getHoursTrend,
  getProjectDistribution,
  getEmployeeRanking,
  getTaskCompletion,
  getAnalysisProjectList
} from '../../api/dailyReport'

// 响应式数据
const dateRange = ref<[string, string]>(['', ''])
const selectedProject = ref('')
const loading = ref(false)
const hoursChartType = ref('day')
const projectChartType = ref('pie')
const employeeTopN = ref(10)

// 图表引用
const hoursChartRef = ref<HTMLElement>()
const projectChartRef = ref<HTMLElement>()
const employeeChartRef = ref<HTMLElement>()
const completionChartRef = ref<HTMLElement>()

// 数据
const projectList = ref<any[]>([])
const overviewStats = ref({
  totalHours: 0,
  hoursChange: '0%',
  activeProjects: 0,
  projectChange: '0',
  completedTasks: 0,
  taskChange: '0',
  efficiencyRate: 0,
  efficiencyTrend: 0
})

const projectDetailData = ref<any[]>([])
const employeeDetailData = ref<any[]>([])
const hoursTrendData = ref<any[]>([])
const taskCompletionData = ref<any>({})
const filteredProjectList = ref<any[]>([])

// 计算属性
const completionRate = computed(() => {
  return Math.round(overviewStats.value.completedTasks / (overviewStats.value.completedTasks + 25) * 100)
})

const completionRateType = computed(() => {
  if (completionRate.value >= 90) return 'success'
  if (completionRate.value >= 80) return 'warning'
  return 'danger'
})

// 方法
const formatNumber = (num: number): string => {
  return num.toFixed(1)
}

const filterProjects = (query: string) => {
  if (!query) {
    filteredProjectList.value = projectList.value
  } else {
    filteredProjectList.value = projectList.value.filter(project => 
      project.project_name.toLowerCase().includes(query.toLowerCase()) ||
      project.project_id.toLowerCase().includes(query.toLowerCase())
    )
  }
}

const getProgressColor = (rate: number): string => {
  if (rate >= 90) return '#13ce66'
  if (rate >= 80) return '#20a0ff'
  if (rate >= 70) return '#e6a23c'
  return '#ff4949'
}

const getWorkloadType = (level: string): string => {
  switch (level) {
    case '较重': return 'danger'
    case '正常': return 'success'
    case '较轻': return 'info'
    default: return 'warning'
  }
}

const handleDateRangeChange = () => {
  refreshAnalysis()
}

const changeProjectChartType = (type: string) => {
  projectChartType.value = type
  // 重新渲染项目图表
  renderProjectChart()
}

const loadProjectList = async () => {
  try {
    const response = await getAnalysisProjectList()
    if (response.code === 200) {
      projectList.value = response.data || []
    }
  } catch (error) {
    console.error('获取项目列表失败:', error)
  }
}

const loadOverviewData = async () => {
  try {
    const params: any = {}
    if (dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    if (selectedProject.value) {
      params.project_id = selectedProject.value
    }
    
    const response = await getAnalysisOverview(params)
    if (response.code === 200) {
      const data = response.data
      overviewStats.value = {
        totalHours: data.total_hours || 0,
        hoursChange: data.hours_change || '0%',
        activeProjects: data.active_projects || 0,
        projectChange: data.project_change || '0',
        completedTasks: data.completed_tasks || 0,
        taskChange: data.task_change || '0',
        efficiencyRate: data.efficiency_rate || 0,
        efficiencyTrend: data.efficiency_trend || 0
      }
    }
  } catch (error) {
    console.error('获取概览数据失败:', error)
  }
}

const loadProjectDistribution = async () => {
  try {
    const params: any = { limit: 20 }
    if (dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    const response = await getProjectDistribution(params)
    if (response.code === 200) {
      projectDetailData.value = response.data || []
    }
  } catch (error) {
    console.error('获取项目分布数据失败:', error)
  }
}

const loadEmployeeRanking = async () => {
  try {
    const params: any = { limit: 20 }
    if (dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    if (selectedProject.value) {
      params.project_id = selectedProject.value
    }
    
    const response = await getEmployeeRanking(params)
    if (response.code === 200) {
      employeeDetailData.value = response.data || []
    }
  } catch (error) {
    console.error('获取员工排名数据失败:', error)
  }
}

const loadTaskCompletion = async () => {
  try {
    const params: any = {}
    if (dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    if (selectedProject.value) {
      params.project_id = selectedProject.value
    }
    
    const response = await getTaskCompletion(params)
    if (response.code === 200) {
      taskCompletionData.value = response.data || {}
    }
  } catch (error) {
    console.error('获取任务完成率数据失败:', error)
  }
}

const loadHoursTrend = async () => {
  try {
    // 确保日期参数有效
    const startDate = dateRange.value[0] && dateRange.value[0] !== '' 
      ? dateRange.value[0] 
      : getDefaultStartDate()
    const endDate = dateRange.value[1] && dateRange.value[1] !== ''
      ? dateRange.value[1] 
      : getDefaultEndDate()
    
    const params: any = {
      start_date: startDate,
      end_date: endDate,
      group_by: hoursChartType.value
    }
    if (selectedProject.value) {
      params.project_id = selectedProject.value
    }
    
    
    const response = await getHoursTrend(params)
    if (response.code === 200) {
      hoursTrendData.value = response.data || []
    }
  } catch (error) {
    console.error('获取工时趋势数据失败:', error)
  }
}

const getDefaultStartDate = () => {
  const date = new Date()
  date.setDate(date.getDate() - 30)
  return date.toLocaleDateString('en-CA') // 返回 YYYY-MM-DD 格式
}

const getDefaultEndDate = () => {
  const date = new Date()
  return date.toLocaleDateString('en-CA') // 返回 YYYY-MM-DD 格式
}

const refreshAnalysis = async () => {
  loading.value = true
  try {
    // 并发加载所有数据
    await Promise.all([
      loadOverviewData(),
      loadProjectDistribution(),
      loadEmployeeRanking(),
      loadTaskCompletion(),
      loadHoursTrend()
    ])
    
    ElMessage.success('数据刷新成功')
  } catch (error) {
    console.error('数据刷新失败:', error)
    ElMessage.error('数据刷新失败')
  } finally {
    loading.value = false
  }
}

const exportProjectData = () => {
  ElMessage.info('项目数据导出功能开发中...')
}

const exportEmployeeData = () => {
  ElMessage.info('人员数据导出功能开发中...')
}

// 图表渲染方法
const renderHoursChart = () => {
  // 模拟图表渲染
  if (hoursChartRef.value) {
    hoursChartRef.value.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: center; height: 300px; background: #f5f7fa; border-radius: 8px;">
        <div style="text-align: center; color: #909399;">
          <div style="font-size: 48px; margin-bottom: 8px;">📊</div>
          <div>工时趋势图表</div>
          <div style="font-size: 12px; margin-top: 4px;">(${hoursChartType.value === 'day' ? '按日' : hoursChartType.value === 'week' ? '按周' : '按月'})</div>
        </div>
      </div>
    `
  }
}

const renderProjectChart = () => {
  // 模拟图表渲染
  if (projectChartRef.value) {
    const chartType = projectChartType.value === 'pie' ? '🥧' : '📊'
    projectChartRef.value.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: center; height: 300px; background: #f5f7fa; border-radius: 8px;">
        <div style="text-align: center; color: #909399;">
          <div style="font-size: 48px; margin-bottom: 8px;">${chartType}</div>
          <div>项目工时分布图表</div>
          <div style="font-size: 12px; margin-top: 4px;">(${projectChartType.value === 'pie' ? '饼图' : '柱状图'})</div>
        </div>
      </div>
    `
  }
}

const renderEmployeeChart = () => {
  // 模拟图表渲染
  if (employeeChartRef.value) {
    employeeChartRef.value.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: center; height: 300px; background: #f5f7fa; border-radius: 8px;">
        <div style="text-align: center; color: #909399;">
          <div style="font-size: 48px; margin-bottom: 8px;">👥</div>
          <div>人员工时排名图表</div>
          <div style="font-size: 12px; margin-top: 4px;">(Top ${employeeTopN.value})</div>
        </div>
      </div>
    `
  }
}

const renderCompletionChart = () => {
  // 模拟图表渲染
  if (completionChartRef.value) {
    completionChartRef.value.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: center; height: 300px; background: #f5f7fa; border-radius: 8px;">
        <div style="text-align: center; color: #909399;">
          <div style="font-size: 48px; margin-bottom: 8px;">✅</div>
          <div>任务完成率分析</div>
          <div style="font-size: 12px; margin-top: 4px;">(完成率: ${completionRate.value}%)</div>
        </div>
      </div>
    `
  }
}

// 获取默认日期范围 - 当月1日到月末最后一天
const getDefaultDateRange = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth()
  
  // 当月1号
  const startDate = new Date(year, month, 1)
  // 当月最后一天（下个月1号减1天）
  const nextMonth = new Date(year, month + 1, 1)
  const endDate = new Date(nextMonth - 1)
  
  // 使用本地时间格式，避免时区偏移
  const formatDate = (date: Date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  
  return [
    formatDate(startDate),
    formatDate(endDate)
  ]
}

// 生命周期
onMounted(async () => {
  // 设置默认日期范围 - 当月1日到月末最后一天
  dateRange.value = getDefaultDateRange()
  
  console.log('初始化日期范围:', dateRange.value)
  
  // 确保日期设置后再加载数据
  await nextTick()
  
  // 加载项目列表
  await loadProjectList()
  
  // 加载分析数据
  await refreshAnalysis()
  
  // 渲染图表
  renderHoursChart()
  renderProjectChart()
  renderEmployeeChart()
  renderCompletionChart()
})
</script>

<style scoped>
.daily-report-analysis {
  padding: 24px;
  background: #f5f5f5;
  min-height: calc(100vh - 60px);
}

/* 页面标题区域 */
.page-header {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-left .page-title {
  margin: 0 0 8px;
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
}

.header-left .page-subtitle {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.header-controls {
  display: flex;
  gap: 16px;
  align-items: center;
}

/* 概览卡片 */
.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.metric-icon.total-hours {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.metric-icon.projects {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.metric-icon.tasks {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.metric-icon.efficiency {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 4px;
}

.metric-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
}

.metric-change {
  font-size: 12px;
  font-weight: 500;
}

.metric-change.positive {
  color: #13ce66;
}

.metric-change.negative {
  color: #ff4949;
}

/* 图表区域 */
.charts-section {
  margin-bottom: 24px;
}

.chart-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.chart-header {
  padding: 20px 24px 16px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.chart-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.chart-content {
  padding: 24px;
}

.chart-canvas {
  height: 300px;
  border-radius: 8px;
}

/* 数据表格区域 */
.data-tables-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 24px;
}

.table-container {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.table-controls {
  display: flex;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .overview-cards {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .header-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .overview-cards {
    grid-template-columns: 1fr;
  }
  
  .data-tables-section :deep(.el-col) {
    width: 100% !important;
    margin-bottom: 20px;
  }
}
</style>