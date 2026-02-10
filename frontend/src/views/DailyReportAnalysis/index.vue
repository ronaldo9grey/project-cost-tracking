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

      <el-row :gutter="20" style="margin-top: 20px;">
        <!-- 评价分析图表 -->
        <el-col :span="12">
          <div class="chart-container">
            <div class="chart-header">
              <h3>主管评价分析</h3>
              <div class="chart-controls">
                <el-tag :type="evaluationData.qualityRate >= 80 ? 'success' : 'warning'">
                  平均评分: {{ evaluationData.avgScore }}
                </el-tag>
              </div>
            </div>
            <div class="chart-content">
              <div ref="evaluationChartRef" class="chart-canvas"></div>
            </div>
          </div>
        </el-col>

        <!-- 评分分布分析 -->
        <el-col :span="12">
          <div class="chart-container">
            <div class="chart-header">
              <h3>评分分布分析</h3>
              <div class="chart-controls">
                <el-tag>{{ evaluationData.totalEvaluations }}条评价</el-tag>
              </div>
            </div>
            <div class="chart-content">
              <div ref="scoreDistributionChartRef" class="chart-canvas"></div>
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
import * as echarts from 'echarts'
import {
  getAnalysisOverview,
  getHoursTrend,
  getProjectDistribution,
  getEmployeeRanking,
  getTaskCompletion,
  getEvaluationAnalysis,
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
const evaluationChartRef = ref<HTMLElement>()
const scoreDistributionChartRef = ref<HTMLElement>()

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
const evaluationData = ref({
  avgScore: 0,
  totalEvaluations: 0,
  totalSupervisors: 0,
  qualityRate: 0,
  scoreDistribution: {},
  supervisorRanking: [],
  employeeEvaluationRanking: []
})
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

const loadEvaluationAnalysis = async () => {
  try {
    const params: any = {}
    if (dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    if (selectedProject.value) {
      params.project_id = selectedProject.value
    }
    
    const response = await getEvaluationAnalysis(params)
    if (response.code === 200) {
      const data = response.data
      evaluationData.value = {
        avgScore: data.avg_score || 0,
        totalEvaluations: data.total_evaluations || 0,
        totalSupervisors: data.total_supervisors || 0,
        qualityRate: data.quality_rate || 0,
        scoreDistribution: data.score_distribution || {},
        supervisorRanking: data.supervisor_ranking || [],
        employeeEvaluationRanking: data.employee_evaluation_ranking || []
      }
    }
  } catch (error) {
    console.error('获取评价分析数据失败:', error)
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
      loadHoursTrend(),
      loadEvaluationAnalysis()
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
  if (!hoursChartRef.value) return
  
  // 初始化或获取图表实例
  const chart = echarts.getInstanceByDom(hoursChartRef.value) || echarts.init(hoursChartRef.value)
  
  // 准备数据
  const dates = hoursTrendData.value.map(item => item.date)
  const hours = hoursTrendData.value.map(item => item.total_hours)
  
  // 配置图表选项
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function(params) {
        const data = params[0]
        return `
          <div style="padding: 8px;">
            <div><strong>日期:</strong> ${data.name}</div>
            <div><strong>工时:</strong> ${data.value}h</div>
          </div>
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: dates.length > 10 ? 45 : 0,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      name: '工时(小时)',
      axisLabel: {
        formatter: '{value}h'
      }
    },
    series: [
      {
        name: '工时投入',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: {
          color: '#5470c6'
        },
        lineStyle: {
          color: '#5470c6',
          width: 3
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(84, 112, 198, 0.3)' },
            { offset: 1, color: 'rgba(84, 112, 198, 0.1)' }
          ])
        },
        data: hours
      }
    ]
  }
  
  chart.setOption(option, true)
  
  // 响应式处理
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 评价分析图表渲染
const renderEvaluationChart = () => {
  if (!evaluationChartRef.value) return
  
  // 初始化或获取图表实例
  const chart = echarts.getInstanceByDom(evaluationChartRef.value) || echarts.init(evaluationChartRef.value)
  
  // 准备数据 - 显示主管评价排名前5名
  const data = evaluationData.value.supervisorRanking.slice(0, 5)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        const data = params[0]
        const supervisorData = data.data
        return `
          <div style="padding: 8px;">
            <div><strong>${data.name}</strong></div>
            <div>平均评分: ${supervisorData.value}分</div>
            <div>评价数量: ${supervisorData.evaluation_count}条</div>
          </div>
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '评分',
      min: 0,
      max: 5,
      axisLabel: {
        formatter: '{value}分'
      }
    },
    yAxis: {
      type: 'category',
      data: data.map(item => item.supervisor_name),
      axisLabel: {
        fontSize: 10
      }
    },
    series: [
      {
        name: '平均评分',
        type: 'bar',
        data: data.map(item => ({
          value: item.avg_score,
          evaluation_count: item.evaluation_count,
          itemStyle: {
            color: item.avg_score >= 4 
              ? '#13ce66' 
              : item.avg_score >= 3 
                ? '#20a0ff' 
                : '#e6a23c'
          }
        })),
        barWidth: '60%'
      }
    ]
  }
  
  chart.setOption(option, true)
  
  // 响应式处理
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 评分分布图表渲染
const renderScoreDistributionChart = () => {
  if (!scoreDistributionChartRef.value) return
  
  // 初始化或获取图表实例
  const chart = echarts.getInstanceByDom(scoreDistributionChartRef.value) || echarts.init(scoreDistributionChartRef.value)
  
  // 准备数据
  const scoreData = evaluationData.value.scoreDistribution
  const data = [
    { name: '1分', value: scoreData.score_1 || 0, color: '#ff4949' },
    { name: '2分', value: scoreData.score_2 || 0, color: '#e6a23c' },
    { name: '3分', value: scoreData.score_3 || 0, color: '#20a0ff' },
    { name: '4分', value: scoreData.score_4 || 0, color: '#5470c6' },
    { name: '5分', value: scoreData.score_5 || 0, color: '#13ce66' }
  ].filter(item => item.value > 0)
  
  if (data.length === 0) {
    // 如果没有数据，显示空状态
    chart.clear()
    chart.setOption({
      graphic: {
        type: 'text',
        left: 'center',
        top: 'middle',
        style: {
          text: '暂无评价数据',
          fontSize: 16,
          fill: '#909399'
        }
      }
    })
    return
  }
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        return `
          <div style="padding: 8px;">
            <div><strong>${params.name}</strong></div>
            <div>数量: ${params.value}条</div>
            <div>占比: ${params.percent}%</div>
          </div>
        `
      }
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle',
      textStyle: {
        fontSize: 12
      }
    },
    series: [
      {
        name: '评分分布',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          position: 'outside',
          formatter: function(params) {
            return `${params.name}\n${params.percent}%`
          },
          fontSize: 12
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        data: data
      }
    ]
  }
  
  chart.setOption(option, true)
  
  // 响应式处理
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

const renderProjectChart = () => {
  if (!projectChartRef.value) return
  
  // 初始化或获取图表实例
  const chart = echarts.getInstanceByDom(projectChartRef.value) || echarts.init(projectChartRef.value)
  
  // 准备数据
  const data = projectDetailData.value.slice(0, 10) // 限制为前10个项目
  const option = projectChartType.value === 'pie' 
    ? {
        tooltip: {
          trigger: 'item',
          formatter: function(params) {
            return `
              <div style="padding: 8px;">
                <div><strong>${params.name}</strong></div>
                <div>工时: ${params.value}h</div>
                <div>占比: ${params.percent}%</div>
                <div>人数: ${data.find(d => d.project_name === params.name)?.employee_count || 0}人</div>
              </div>
            `
          }
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          top: 'middle',
          textStyle: {
            fontSize: 12
          }
        },
        series: [
          {
            name: '项目工时',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['60%', '50%'],
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
                fontSize: 16,
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: data.map((item, index) => ({
              value: item.total_hours,
              name: item.project_name,
              itemStyle: {
                color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#91cc75'][index % 10]
              }
            }))
          }
        ]
      }
    : {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: function(params) {
            const data = params[0]
            const projectData = data.data
            return `
              <div style="padding: 8px;">
                <div><strong>${data.name}</strong></div>
                <div>工时: ${projectData.value}h</div>
                <div>参与人数: ${projectData.employee_count}人</div>
                <div>完成率: ${projectData.completion_rate}%</div>
              </div>
            `
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: data.map(item => item.project_name),
          axisLabel: {
            interval: 0,
            rotate: 45,
            fontSize: 10
          }
        },
        yAxis: {
          type: 'value',
          name: '工时(小时)',
          axisLabel: {
            formatter: '{value}h'
          }
        },
        series: [
          {
            name: '项目工时',
            type: 'bar',
            data: data.map(item => ({
              value: item.total_hours,
              employee_count: item.employee_count,
              completion_rate: item.completion_rate,
              itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: '#5470c6' },
                  { offset: 1, color: '#91cc75' }
                ])
              }
            })),
            barWidth: '60%'
          }
        ]
      }
  
  chart.setOption(option, true)
  
  // 响应式处理
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

const renderEmployeeChart = () => {
  if (!employeeChartRef.value) return
  
  // 初始化或获取图表实例
  const chart = echarts.getInstanceByDom(employeeChartRef.value) || echarts.init(employeeChartRef.value)
  
  // 准备数据 - 限制为前N名
  const data = employeeDetailData.value.slice(0, employeeTopN.value)
  
  // 准备图表配置
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: function(params) {
        const data = params[0]
        const employeeData = data.data
        return `
          <div style="padding: 8px;">
            <div><strong>${data.name}</strong></div>
            <div>总工时: ${employeeData.value}h</div>
            <div>参与项目: ${employeeData.projects_count}个</div>
            <div>完成任务: ${employeeData.tasks_count}个</div>
            <div>效率评分: ${employeeData.efficiency_score}分</div>
            <div>工作负荷: ${employeeData.workload_level}</div>
          </div>
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '工时(小时)',
      axisLabel: {
        formatter: '{value}h'
      }
    },
    yAxis: {
      type: 'category',
      data: data.map(item => item.employee_name),
      axisLabel: {
        fontSize: 10
      }
    },
    series: [
      {
        name: '工时',
        type: 'bar',
        data: data.map(item => ({
          value: item.total_hours,
          projects_count: item.projects_count,
          tasks_count: item.tasks_count,
          efficiency_score: item.efficiency_score,
          workload_level: item.workload_level,
          itemStyle: {
            color: item.workload_level === '较重' 
              ? '#ee6666' 
              : item.workload_level === '正常' 
                ? '#5470c6' 
                : '#73c0de'
          }
        })),
        barWidth: '60%'
      }
    ]
  }
  
  chart.setOption(option, true)
  
  // 响应式处理
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

const renderCompletionChart = () => {
  if (!completionChartRef.value) return
  
  // 初始化或获取图表实例
  const chart = echarts.getInstanceByDom(completionChartRef.value) || echarts.init(completionChartRef.value)
  
  // 准备数据
  const completionData = taskCompletionData.value
  const data = [
    { name: '已完成', value: completionData.completed_tasks || 0, color: '#13ce66' },
    { name: '进行中', value: completionData.in_progress_tasks || 0, color: '#20a0ff' },
    { name: '待开始', value: completionData.pending_tasks || 0, color: '#e6a23c' },
    { name: '延期', value: completionData.delayed_tasks || 0, color: '#ff4949' }
  ]
  
  const total = data.reduce((sum, item) => sum + item.value, 0)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        return `
          <div style="padding: 8px;">
            <div><strong>${params.name}</strong></div>
            <div>任务数: ${params.value}个</div>
            <div>占比: ${params.percent}%</div>
          </div>
        `
      }
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle',
      textStyle: {
        fontSize: 12
      }
    },
    series: [
      {
        name: '任务状态',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          position: 'outside',
          formatter: function(params) {
            return `${params.name}\n${params.percent}%`
          },
          fontSize: 12
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        data: data.map(item => ({
          value: item.value,
          name: item.name,
          itemStyle: {
            color: item.color
          }
        }))
      }
    ]
  }
  
  chart.setOption(option, true)
  
  // 响应式处理
  window.addEventListener('resize', () => {
    chart.resize()
  })
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
  renderEvaluationChart()
  renderScoreDistributionChart()
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