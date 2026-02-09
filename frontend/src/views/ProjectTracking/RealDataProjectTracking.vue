<template>
  <div class="project-tracking-container">
    <!-- 页面头部 -->
    <div class="page-header">
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-filter">
      <el-row :gutter="20" align="middle">
        <el-col :span="6">
          <el-input
            v-model="searchParams.project_name"
            placeholder="项目名称"
            :prefix-icon="Search"
            clearable
          />
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchParams.status" placeholder="项目状态" clearable>
            <el-option label="进行中" value="进行中" />
            <el-option label="已完成" value="已完成" />
            <el-option label="规划中" value="规划中" />
            <el-option label="已暂停" value="已暂停" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="searchParams.risk_level" placeholder="风险等级" clearable>
            <el-option label="高风险" value="高风险" />
            <el-option label="中风险" value="中风险" />
            <el-option label="低风险" value="低风险" />
          </el-select>
        </el-col>

        <el-col :span="6">
          <el-button type="primary" :icon="Search" @click="fetchData">
            搜索
          </el-button>

          <el-button type="primary" :icon="Refresh" @click="refreshData">
            刷新
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">

      <!-- 项目统计概览 -->
      <div class="stats-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="stat-card total-projects">
              <div class="stat-content">
                <div class="stat-icon">
                  <el-icon size="32" color="#409eff"><Trophy /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ projectList.length }}</div>
                  <div class="stat-label">项目总数</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card in-progress">
              <div class="stat-content">
                <div class="stat-icon">
                  <el-icon size="32" color="#e6a23c"><Odometer /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ getStatusCount('进行中') }}</div>
                  <div class="stat-label">进行中项目</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card completed">
              <div class="stat-content">
                <div class="stat-icon">
                  <el-icon size="32" color="#67c23a"><CircleCheckFilled /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ getStatusCount('已完成') }}</div>
                  <div class="stat-label">已完成项目</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card high-risk">
              <div class="stat-content">
                <div class="stat-icon">
                  <el-icon size="32" color="#f56c6c"><WarningFilled /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-value">{{ getStatusCount('高风险') }}</div>
                  <div class="stat-label">高风险项目</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 图表分析区域 -->
      <div class="charts-section">
        <!-- 项目状态分布 -->
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>项目状态分布</span>
              <el-popover
                placement="right-start"
                :width="400"
                trigger="click"
              >
                <template #reference>
                  <el-button size="small" type="text">查看详情</el-button>
                </template>
                <template #default>
                  <div class="enhanced-drill-down">
                    <h4 class="popover-title">
                      <el-icon><DataAnalysis /></el-icon>
                      项目状态详情分析
                    </h4>
                    <div class="status-grid">
                      <div v-for="item in statusData" :key="item.name" class="status-item">
                        <div class="status-icon" :class="getStatusIconClass(item.name)">
                          <el-icon v-if="item.name === '进行中'"><Loading /></el-icon>
                          <el-icon v-else-if="item.name === '已完成'"><Check /></el-icon>
                          <el-icon v-else-if="item.name === '规划中'"><EditPen /></el-icon>
                          <el-icon v-else-if="item.name === '已暂停'"><VideoPause /></el-icon>
                          <el-icon v-else><QuestionFilled /></el-icon>
                        </div>
                        <div class="status-content">
                          <div class="status-header">
                            <strong class="status-name">{{ item.name }}</strong>
                            <el-tag :type="getStatusTagType(item.name)" size="small">{{ item.value }}个</el-tag>
                          </div>
                          <div class="status-description">
                            <span v-if="item.name === '进行中'">项目正在积极推进中，需要持续关注进度</span>
                            <span v-else-if="item.name === '已完成'">项目已成功交付，质量符合要求</span>
                            <span v-else-if="item.name === '规划中'">项目处于前期规划阶段，准备工作进行中</span>
                            <span v-else-if="item.name === '已暂停'">项目因各种原因暂停执行</span>
                            <span v-else>其他状态项目</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </template>
              </el-popover>
            </div>
          </template>
          <div ref="statusChart" class="chart-container" style="height: 300px;"></div>
        </el-card>

        <!-- 项目进度分布 -->
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>项目进度分布</span>
              <el-popover
                placement="right-start"
                :width="420"
                trigger="click"
              >
                <template #reference>
                  <el-button size="small" type="text">查看详情</el-button>
                </template>
                <template #default>
                  <div class="enhanced-drill-down">
                    <h4 class="popover-title">
                      <el-icon><TrendCharts /></el-icon>
                      项目进度阶段分析
                    </h4>
                    <div class="progress-grid">
                      <div v-for="item in progressData" :key="item.name" class="progress-item">
                        <div class="progress-icon" :class="getProgressIconClass(item.name)">
                          <el-icon v-if="item.name === '0-30%'"><Warning /></el-icon>
                          <el-icon v-else-if="item.name === '30-60%'"><Odometer /></el-icon>
                          <el-icon v-else-if="item.name === '60-90%'"><SuccessFilled /></el-icon>
                          <el-icon v-else-if="item.name === '90-100%'"><Trophy /></el-icon>
                        </div>
                        <div class="progress-content">
                          <div class="progress-header">
                            <strong class="progress-name">{{ item.name }}</strong>
                            <el-tag :type="getProgressTagType(item.name)" size="small">{{ item.value }}个</el-tag>
                          </div>
                          <div class="progress-description">
                            <span v-if="item.name === '0-30%'">项目处于起步阶段，需要加速推进</span>
                            <span v-else-if="item.name === '30-60%'">项目进展良好，中期成果可见</span>
                            <span v-else-if="item.name === '60-90%'">项目接近收尾，关键节点把控重要</span>
                            <span v-else-if="item.name === '90-100%'">项目即将完成，验收和交付准备</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </template>
              </el-popover>
            </div>
          </template>
          <div ref="progressChart" class="chart-container" style="height: 300px;"></div>
        </el-card>

        <!-- 风险等级分析 -->
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>风险等级分析</span>
              <el-popover
                placement="right-start"
                :width="450"
                trigger="click"
              >
                <template #reference>
                  <el-button size="small" type="text">查看详情</el-button>
                </template>
                <template #default>
                  <div class="enhanced-drill-down">
                    <h4 class="popover-title">
                      <el-icon><WarningFilled /></el-icon>
                      风险等级深度解析
                    </h4>
                    <div class="risk-grid">
                      <div v-for="item in riskData" :key="item.name" class="risk-item">
                        <div class="risk-icon" :class="getRiskIconClass(item.name)">
                          <el-icon v-if="item.name === '高风险'"><WarningFilled /></el-icon>
                          <el-icon v-else-if="item.name === '中风险'"><QuestionFilled /></el-icon>
                          <el-icon v-else-if="item.name === '低风险'"><CircleCheckFilled /></el-icon>
                        </div>
                        <div class="risk-content">
                          <div class="risk-header">
                            <strong class="risk-name">{{ item.name }}</strong>
                            <el-tag :type="getRiskTagType(item.name)" size="small">{{ item.value }}个</el-tag>
                          </div>
                          <div v-if="item.name === '高风险'" class="risk-explanation">
                            <div class="risk-criteria">
                              <p><strong>🔴 高风险项目判断标准:</strong></p>
                              <ul>
                                <li>项目截止日期已过但状态非"已完成"</li>
                                <li>延期超过7天的项目</li>
                                <li>进度严重滞后于计划</li>
                                <li>需要立即采取补救措施</li>
                              </ul>
                            </div>
                          </div>
                          <div v-else-if="item.name === '中风险'" class="risk-explanation">
                            <div class="risk-criteria">
                              <p><strong>🟡 中风险项目判断标准:</strong></p>
                              <ul>
                                <li>项目截止日期在7天内但状态非"已完成"</li>
                                <li>轻微延期但影响可控</li>
                                <li>需要加强监控和资源投入</li>
                              </ul>
                            </div>
                          </div>
                          <div v-else-if="item.name === '低风险'" class="risk-explanation">
                            <div class="risk-criteria">
                              <p><strong>🟢 低风险项目特征:</strong></p>
                              <ul>
                                <li>项目时间充裕，进展正常</li>
                                <li>进度符合预期或超前</li>
                                <li>风险可控，继续保持</li>
                              </ul>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </template>
              </el-popover>
            </div>
          </template>
          <div ref="riskChart" class="chart-container" style="height: 300px;"></div>
        </el-card>
      </div>

      <!-- 项目跟踪列表 -->
      <el-card class="project-list-card">
        <template #header>
          <div class="card-header">
            <el-button type="primary" size="small" @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>
        
        <!-- 默认显示高风险TOP5项目 -->
        <div v-if="projectList.length > 0" class="projects-container">
          <div class="view-mode-tabs">
            <el-button-group>
              <el-button 
                :type="viewMode === 'cards' ? 'primary' : 'default'"
                @click="viewMode = 'cards'"
              >
                卡片视图
              </el-button>
              <el-button 
                :type="viewMode === 'table' ? 'primary' : 'default'"
                @click="viewMode = 'table'"
              >
                表格视图
              </el-button>
            </el-button-group>
          </div>
          


          <!-- 卡片视图 -->
          <div v-if="viewMode === 'cards'" class="cards-container">
            <div 
              v-for="project in displayedProjects" 
              :key="project.id"
              class="project-card"
              :class="{ 'high-risk': project.risk_level === '高风险' }"
            >
              <!-- 卡片头部 -->
              <div class="card-header">
                <div class="project-title">
                  <h3 @click="goToDetail(project)">{{ project.project_name }}</h3>
                  <div class="project-meta">
                    <span class="leader">负责人：{{ project.leader }}</span>
                    <span class="dates">{{ project.project_start_date }} ~ {{ project.project_end_date }}</span>
                  </div>
                </div>
                <div class="card-actions">
                  <el-tag :type="getStatusType(project.project_status)" size="small">
                    {{ project.project_status }}
                  </el-tag>
                  <el-tag 
                    :type="getRiskTagType(project.risk_level)" 
                    size="small"
                    :class="project.risk_level === '高风险' ? 'risk-high' : ''"
                  >
                    {{ project.risk_level }}
                  </el-tag>
                </div>
              </div>

              <!-- 进度条 -->
              <div class="progress-section">
                <div class="progress-header">
                  <span>项目进度</span>
                  <span class="progress-value">{{ Math.round(project.overall_progress) }}%</span>
                </div>
                <el-progress 
                  :percentage="project.overall_progress" 
                  :show-text="false" 
                  :stroke-width="8"
                  :color="getProgressColor(project.overall_progress)"
                />
              </div>

              <!-- 任务流程显示 -->
              <div class="task-flow-section">
                <div class="section-title">任务流程</div>
                <div v-if="project.task_name && project.task_name !== '无当前任务'" class="task-info">
                  <div class="current-task">
                    <div class="task-name">{{ project.task_name }}</div>
                    <div class="task-meta">
                      <span class="status">{{ project.task_status || '未开始' }}</span>
                      <span class="assignee">负责人：{{ project.task_assignee }}</span>
                    </div>
                    <div v-if="project.task_progress > 0" class="task-progress">
                      <el-progress 
                        :percentage="project.task_progress" 
                        :stroke-width="4"
                        :show-text="false"
                        :color="project.task_progress >= 100 ? '#67c23a' : '#409eff'"
                      />
                      <span class="progress-text">{{ project.task_progress }}%</span>
                    </div>
                  </div>
                </div>
                <div v-else class="no-tasks">
                  <el-icon><DocumentRemove /></el-icon>
                  暂无任务信息
                </div>
              </div>

              <!-- 展开甘特图 -->
              <div class="expand-section">
                <el-button 
                  type="text" 
                  size="small"
                  @click.stop="toggleGanttView(project.project_id)"
                  :icon="expandedProjects.has(project.project_id) ? 'ArrowUp' : 'ArrowDown'"
                >
                  {{ expandedProjects.has(project.project_id) ? '收起' : '查看时间线甘特图' }}
                </el-button>
              </div>

              <!-- 甘特图展开区域 -->
              <div v-if="expandedProjects.has(project.project_id)" class="gantt-section">
                <ProjectGanttChart 
                  v-if="ganttData[project.project_id]"
                  :project="ganttData[project.project_id].project"
                  :tasks="ganttData[project.project_id].tasks"
                  :reports-count="ganttData[project.project_id].reports_count"
                />
                <div v-else class="loading-gantt">
                  <el-skeleton :rows="3" animated />
                </div>
              </div>

              <!-- 卡片底部信息 -->
              <div class="card-footer">
                <div class="footer-info">
                  <span class="reports">
                    <el-icon><Document /></el-icon>
                    本周日报：{{ project.weekly_reports_count || 0 }}篇
                  </span>
                  <span class="warning" v-if="project.warning_info">
                    <el-icon><WarningFilled /></el-icon>
                    {{ project.warning_info }}
                  </span>
                </div>
                <span class="update-time">更新：{{ formatDate(project.updated_at) }}</span>
              </div>
            </div>
          </div>

          <!-- 表格视图 (保留原有表格) -->
          <div v-else class="table-container">
            <el-table 
              :data="displayedProjects" 
              style="width: 100%" 
              :loading="loading"
              @row-click="goToDetail"
              :row-class-name="getRowClassName"
              :row-key="getRowKey"
            >
              <!-- 项目信息 -->
              <el-table-column label="项目信息" min-width="180">
                <template #default="{ row }">
                  <div class="project-info">
                    <div class="project-name" @click.stop="goToDetail(row)">{{ row.project_name }}</div>
                    <div class="project-leader">负责人：{{ row.leader }}</div>
                  </div>
                </template>
              </el-table-column>
              
              <!-- 任务流程 -->
              <el-table-column label="任务流程" min-width="300">
                <template #default="{ row }">
                  <div v-if="row.task_name && row.task_name !== '无当前任务'" class="table-task-info">
                    <div class="task-name">{{ row.task_name }}</div>
                    <div class="task-meta">
                      <span class="status">{{ row.task_status || '未开始' }}</span>
                      <span class="assignee">负责人：{{ row.task_assignee }}</span>
                    </div>
                    <div v-if="row.task_progress > 0" class="task-progress">
                      <el-progress 
                        :percentage="row.task_progress" 
                        :stroke-width="4"
                        :show-text="false"
                        :color="row.task_progress >= 100 ? '#67c23a' : '#409eff'"
                      />
                      <span class="progress-text">{{ row.task_progress }}%</span>
                    </div>
                  </div>
                  <div v-else class="no-task">暂无任务</div>
                </template>
              </el-table-column>
              
              <!-- 项目状态 -->
              <el-table-column label="项目状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.project_status)" size="small">
                    {{ row.project_status }}
                  </el-tag>
                </template>
              </el-table-column>
              
              <!-- 项目进度 -->
              <el-table-column label="项目进度" width="120">
                <template #default="{ row }">
                  <el-progress 
                    :percentage="row.overall_progress" 
                    :stroke-width="8"
                    :color="getProgressColor(row.overall_progress)"
                  />
                </template>
              </el-table-column>
              
              <!-- 风险等级 -->
              <el-table-column label="风险等级" width="100">
                <template #default="{ row }">
                  <el-tag :type="getRiskTagType(row.risk_level)" size="small">
                    {{ row.risk_level }}
                  </el-tag>
                </template>
              </el-table-column>
              
              <!-- 预警信息 -->
              <el-table-column label="预警信息" width="150">
                <template #default="{ row }">
                  <div v-if="row.warning_info" class="warning-info">
                    <el-icon class="warning-icon"><WarningFilled /></el-icon>
                    <span>{{ row.warning_info }}</span>
                  </div>
                  <span v-else class="normal-info">正常</span>
                </template>
              </el-table-column>
              
              <!-- 本周日报 -->
              <el-table-column label="本周日报" width="100">
                <template #default="{ row }">
                  <el-link 
                    type="primary" 
                    @click.stop="viewTaskReports(row)"
                    :disabled="!row.task_id"
                  >
                    {{ row.weekly_reports_count }}条
                  </el-link>
                </template>
              </el-table-column>
              
              <!-- 更新时间 -->
              <el-table-column label="更新时间" width="140">
                <template #default="{ row }">
                  <span class="date-text">{{ formatDate(row.updated_at) }}</span>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 显示更多按钮 -->
          <div v-if="showLoadMore" class="load-more-section">
            <el-button 
              type="primary" 
              size="large"
              @click="loadMoreProjects"
              :loading="loadingMore"
            >
              {{ loadingMore ? '加载中...' : `显示更多项目 (还有 ${projectList.length - displayedProjects.length} 个)` }}
            </el-button>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-state">
          <el-empty description="暂无项目数据" />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Refresh, DataAnalysis, Loading, Check, EditPen, VideoPause, QuestionFilled, TrendCharts, Warning, Odometer, SuccessFilled, Trophy, WarningFilled, CircleCheckFilled } from '@element-plus/icons-vue'
import { projectTrackingApi } from '../../api/projectTracking'
import * as echarts from 'echarts'
import { ElPopover } from 'element-plus'
// import TaskFlowDisplay from '@/components/TaskFlowDisplay.vue'
import ProjectGanttChart from '@/components/ProjectGanttChart.vue'

// 项目数据接口 - 流程化任务序列导向
interface Project {
  // 项目基本信息
  id: number
  name: string
  status: string
  progress: number
  leader: string
  start_date: string
  end_date: string
  updated_at: string
  
  // 任务序列信息
  task_id?: string
  task_name: string
  task_assignee: string
  task_start_date?: string
  task_end_date?: string
  task_actual_end_date?: string
  task_status?: string
  task_progress: number
  task_budget_cost: number
  task_actual_cost: number
  task_sequence: number
  is_current_task: boolean
  
  // 任务流程信息
  prev_task_name?: string
  prev_task_status?: string
  prev_task_end?: string
  next_task_name?: string
  next_task_status?: string
  next_task_end?: string
  
  // 风险管控信息
  risk_level: string
  warning_info: string
  weekly_reports_count: number
}

// 搜索参数
const searchParams = reactive({
  project_name: '',
  status: '',
  risk_level: ''
})

// 数据状态
const loading = ref(false)
const projectList = ref<Project[]>([])

// 数据穿透状态 - 使用 Popover 实现浮动显示

// 图表数据
const statusData = ref<any[]>([])
const progressData = ref<any[]>([])
const riskData = ref<any[]>([])

// 图表引用
const statusChart = ref<HTMLElement>()
const progressChart = ref<HTMLElement>()
const riskChart = ref<HTMLElement>()



// 视图模式控制
const viewMode = ref<'cards' | 'table'>('cards')

// 显示的项目数量控制
const maxDisplayCount = ref(6)
const showLoadMore = computed(() => {
  return viewMode.value === 'cards' && projectList.value.length > maxDisplayCount.value
})

// 当前显示的项目列表
const displayedProjects = computed(() => {
  if (viewMode.value === 'cards') {
    return projectList.value.slice(0, maxDisplayCount.value)
  } else {
    return projectList.value
  }
})

// 甘特图数据存储
const ganttData = reactive<Record<string, any>>({})
const expandedProjects = reactive<Set<string>>(new Set())
const loadingMore = ref(false)



// 获取行key
const getRowKey = (row: any) => {
  return row.id.toString()
}

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '未设置'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return dateStr
  }
}

// 甘特图相关函数
const toggleGanttView = async (projectId: string) => {
  console.log('甘特图函数被调用，projectId:', projectId, '类型:', typeof projectId)
  
  // 检查projectId的有效性
  if (!projectId || projectId === 'undefined' || projectId === 'null') {
    console.error('无效的项目ID:', projectId)
    ElMessage.error('项目ID无效，请刷新页面重试')
    return
  }

  if (expandedProjects.has(projectId)) {
    expandedProjects.delete(projectId)
    return
  }

  // 添加到展开列表
  expandedProjects.add(projectId)

  // 如果数据不存在，调用API获取
  if (!ganttData[projectId]) {
    try {
      console.log('调用甘特图API，projectId:', projectId)
      const response = await projectTrackingApi.getProjectGanttData(projectId)
      console.log('甘特图API响应:', response)
      if (response && response.code === 200) {
        ganttData[projectId] = response.data
        console.log('甘特图数据设置成功')
      } else {
        console.error('获取甘特图数据失败:', response)
        expandedProjects.delete(projectId)
        ElMessage.error(`获取甘特图数据失败: ${response?.message || '未知错误'}`)
      }
    } catch (error) {
      console.error('获取甘特图数据异常:', error)
      expandedProjects.delete(projectId)
    }
  }
}

const loadMoreProjects = async () => {
  loadingMore.value = true
  try {
    // 加载更多项目（这里可以实现更复杂的分页逻辑）
    maxDisplayCount.value += 10
    await new Promise(resolve => setTimeout(resolve, 500)) // 模拟加载时间
  } finally {
    loadingMore.value = false
  }
}

// 获取项目跟踪列表
const fetchData = async () => {
  loading.value = true
  
  try {
    console.log('获取项目跟踪列表...')
    
    // 调用真实API
    const response = await projectTrackingApi.getProjectTrackings({
      page: 1,
      limit: 50,
      project_name: searchParams.project_name || undefined,
      status: searchParams.status || undefined,
      risk_level: searchParams.risk_level || undefined
    })
    
    // 健壮的API响应处理
    if (!response) {
      throw new Error('API响应为空')
    }
    
    let items = null
    
    // 健壮的API响应数据解析
    console.log('前端解析响应:', response)
    console.log('响应类型:', typeof response)
    console.log('响应键:', response ? Object.keys(response) : 'null')
    
    // axios拦截器应该返回 {items: [...], total: 54, page: 1, limit: 3}
    if (response && response.items && Array.isArray(response.items)) {
      items = response.items
      console.log('✅ 成功解析response.items，长度:', items.length)
    }
    // 如果拦截器没有处理，直接解析原始后端响应
    else if (response && response.data && response.data.items && Array.isArray(response.data.items)) {
      items = response.data.items
      console.log('✅ 成功解析response.data.items，长度:', items.length)
    }
    // 如果响应本身就是数组
    else if (response && Array.isArray(response)) {
      items = response
      console.log('✅ 成功解析response数组，长度:', items.length)
    }
    // 兜底：如果都解析不了，输出详细信息用于调试
    else {
      console.error('❌ 无法解析API响应格式:', response)
      console.error('响应结构:', {
        hasResponse: !!response,
        responseType: typeof response,
        responseKeys: response ? Object.keys(response) : null,
        hasItems: response && 'items' in response,
        hasData: response && 'data' in response,
        dataType: response && response.data ? typeof response.data : null,
        dataKeys: response && response.data ? Object.keys(response.data) : null
      })
      
      // 如果没有标准格式，尝试查找任何可能的数组
      if (response && typeof response === 'object') {
        for (const key in response) {
          if (Array.isArray(response[key])) {
            console.log('✅ 找到数组字段:', key, '长度:', response[key].length)
            items = response[key]
            break
          }
        }
      }
      
      // 如果还是没有数据，抛出错误让用户知道
      if (!items) {
        throw new Error(`API响应格式解析失败: ${JSON.stringify(response)}`)
      }
    }
    
    console.log('解析后的items:', items)
    
    if (items && items.length > 0) {
      console.log('原始API数据:', items)
      
      // 将后端数据转换为前端需要的格式
      let mappedProjects = items.map((item: any) => ({
        id: String(item.project_id || ''),
        project_id: item.project_id || '',
        project_name: item.project_name || '未知项目',
        project_status: item.project_status || '未设置',
        overall_progress: Math.round(Number(item.overall_progress || 0)),
        leader: item.leader || '未指定',
        
        // 项目基本信息
        project_start_date: item.project_start_date || '未设置',
        project_end_date: item.project_end_date || '未设置',
        updated_at: item.updated_at || '',
        
        // 任务序列信息
        task_id: item.task_id || '',
        task_name: item.task_name || '无当前任务',
        task_assignee: item.task_assignee || '未指定',
        task_start_date: item.task_start_date || '',
        task_end_date: item.task_end_date || '',
        task_actual_end_date: item.task_actual_end_date || '',
        task_status: item.task_status || '未开始',
        task_progress: Math.round(Number(item.task_progress || 0)),
        task_budget_cost: Number(item.budget_cost || 0),
        task_actual_cost: Number(item.actual_cost || 0),
        task_sequence: Number(item.task_sequence || 0),
        is_current_task: Boolean(item.is_current_task || false),
        
        // 任务流程信息（简化）
        prev_task_name: null,
        prev_task_status: null,
        prev_task_end: null,
        next_task_name: null,
        next_task_status: null,
        next_task_end: null,
        
        // 风险管控信息
        risk_level: item.risk_level || '低风险',
        warning_info: item.warning_info || '正常',
        weekly_reports_count: Number(item.weekly_reports_count || 0)
      }))
      
      // 对项目列表进行排序：有任务的项目在前，无任务的项目在后
      const projectsWithTasks = mappedProjects.filter(p => p.task_name !== null && p.task_name !== undefined && p.task_name !== '')
      const projectsWithoutTasks = mappedProjects.filter(p => p.task_name === null || p.task_name === undefined || p.task_name === '')
      // 排序有任务的项目
      projectsWithTasks.sort((a, b) => {
        // 按风险等级排序（高风险在前）
        const riskOrder = { '高风险': 0, '中风险': 1, '低风险': 2 }
        const aRiskOrder = riskOrder[a.risk_level] || 3
        const bRiskOrder = riskOrder[b.risk_level] || 3
        
        if (aRiskOrder !== bRiskOrder) {
          return aRiskOrder - bRiskOrder
        }
        
        // 风险等级相同时，按项目名称排序
        return a.project_name.localeCompare(b.project_name)
      })
      
      // 排序无任务的项目
      projectsWithoutTasks.sort((a, b) => {
        return a.project_name.localeCompare(b.project_name)
      })
      
      // 合并：先放有任务的项目，再放无任务的项目
      mappedProjects = [...projectsWithTasks, ...projectsWithoutTasks]
      
      // 对项目进行去重：基于项目ID去重，保留第一个出现的项目
      const uniqueProjects = mappedProjects.filter((project, index, self) => 
        index === self.findIndex(p => p.project_id === project.project_id)
      )
      
      console.log('去重后的项目数量:', uniqueProjects.length)
      console.log('去重后的项目列表:', uniqueProjects)
      
      projectList.value = uniqueProjects
      
      // 更新图表数据
      updateChartData()
      console.log('使用真实API数据')
    } else {
      console.log('API响应无效，使用空数据')
      projectList.value = []
      updateChartData()
      ElMessage.error('API响应数据格式不正确，请联系管理员')
    }
    
  } catch (apiError) {
    console.error('API调用失败:', apiError)
    ElMessage.error('获取项目跟踪数据失败')
    projectList.value = []
    updateChartData()
  } finally {
    loading.value = false
  }
}

// 获取状态项目数量
const getStatusCount = (status: string) => {
  return projectList.value.filter(project => {
    if (status === '高风险') {
      return project.risk_level === '高风险'
    }
    return project.project_status === status
  }).length
}

// 更新图表数据
const updateChartData = () => {
  console.log('更新图表数据，当前项目列表:', projectList.value)
  
  // 状态分布数据
  const statusCounts = projectList.value.reduce((acc, project) => {
    const status = project.project_status || project.status || '未知'
    acc[status] = (acc[status] || 0) + 1
    return acc
  }, {})
  
  statusData.value = Object.entries(statusCounts).map(([status, count]) => ({
    name: status,
    value: count
  }))
  
  console.log('状态分布数据:', statusData.value)
  
  // 进度分布数据
  const progressGroups = {
    '0-30%': 0,
    '30-60%': 0,
    '60-90%': 0,
    '90-100%': 0
  }
  
  projectList.value.forEach(project => {
    if (project.progress <= 30) progressGroups['0-30%']++
    else if (project.progress <= 60) progressGroups['30-60%']++
    else if (project.progress <= 90) progressGroups['60-90%']++
    else progressGroups['90-100%']++
  })
  
  progressData.value = Object.entries(progressGroups).map(([range, count]) => ({
    name: range,
    value: count
  }))
  
  console.log('进度分布数据:', progressData.value)
  
  // 风险分布数据
  const riskCounts = projectList.value.reduce((acc, project) => {
    acc[project.risk_level] = (acc[project.risk_level] || 0) + 1
    return acc
  }, {})
  
  riskData.value = Object.entries(riskCounts).map(([risk, count]) => ({
    name: risk,
    value: count
  }))
  
  console.log('风险分布数据:', riskData.value)
  
  // 更新图表
  updateCharts()
}

// 更新图表
const updateCharts = () => {
  setTimeout(() => {
    initStatusChart()
    initProgressChart()
    initRiskChart()
  }, 100)
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

// 获取状态图标类
const getStatusIconClass = (status: string) => {
  const iconClassMap: Record<string, string> = {
    '进行中': 'status-icon-progress',
    '已完成': 'status-icon-success',
    '规划中': 'status-icon-planning',
    '已暂停': 'status-icon-paused'
  }
  return iconClassMap[status] || 'status-icon-default'
}

// 获取状态标签类型
const getStatusTagType = (status: string) => {
  const tagTypeMap: Record<string, string> = {
    '进行中': 'primary',
    '已完成': 'success',
    '规划中': 'info',
    '已暂停': 'warning'
  }
  return tagTypeMap[status] || 'info'
}

// 获取进度图标类
const getProgressIconClass = (progress: string) => {
  const iconClassMap: Record<string, string> = {
    '0-30%': 'progress-icon-early',
    '30-60%': 'progress-icon-mid',
    '60-90%': 'progress-icon-late',
    '90-100%': 'progress-icon-complete'
  }
  return iconClassMap[progress] || 'progress-icon-default'
}

// 获取进度标签类型
const getProgressTagType = (progress: string) => {
  const tagTypeMap: Record<string, string> = {
    '0-30%': 'danger',
    '30-60%': 'warning',
    '60-90%': 'primary',
    '90-100%': 'success'
  }
  return tagTypeMap[progress] || 'info'
}

// 获取风险图标类
const getRiskIconClass = (risk: string) => {
  const iconClassMap: Record<string, string> = {
    '高风险': 'risk-icon-high',
    '中风险': 'risk-icon-medium',
    '低风险': 'risk-icon-low'
  }
  return iconClassMap[risk] || 'risk-icon-default'
}

// 获取风险标签类型
const getRiskTagType = (risk: string) => {
  const tagTypeMap: Record<string, string> = {
    '高风险': 'danger',
    '中风险': 'warning',
    '低风险': 'success'
  }
  return tagTypeMap[risk] || 'info'
}

// 获取结束日期样式类
const getEndDateClass = (row: any) => {
  if (!row.end_date || row.end_date === '未设置') return ''
  
  const endDate = new Date(row.end_date)
  const now = new Date()
  
  if (endDate < now && row.risk_level === '高风险') {
    return 'date-overdue'
  } else if (endDate <= new Date(now.getTime() + 3 * 24 * 60 * 60 * 1000)) {
    return 'date-soon'
  }
  return ''
}

// 查看任务日报
const viewTaskReports = (row: any) => {
  if (row.task_id) {
    // 跳转到日报列表页，参数带task_id
    const router = useRouter()
    router.push(`/daily-report?task_id=${row.task_id}&task_name=${encodeURIComponent(row.task_name)}`)
  }
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

// 刷新数据
const refreshData = () => {
  fetchData()
}

// 跳转到详情页
const goToDetail = (project: Project) => {
  const router = useRouter()
  // 跳转到项目管理详情页面，而不是项目跟踪详情
  router.push(`/projects/${project.id}`)
}

// 数据穿透函数 - 使用 Popover 实现浮动显示，无需额外函数

// 图表实例存储
let statusChartInstance: any = null
let progressChartInstance: any = null
let riskChartInstance: any = null

// 初始化图表
const initCharts = async () => {
  await nextTick()
  if (statusData.value.length > 0) {
    initStatusChart()
  }
  if (progressData.value.length > 0) {
    initProgressChart()
  }
  if (riskData.value.length > 0) {
    initRiskChart()
  }
}

// 初始化状态分布图表
const initStatusChart = () => {
  const chartDom = statusChart.value
  if (!chartDom) return
  
  // 如果图表实例存在，则更新数据；否则创建新实例
  if (!statusChartInstance) {
    statusChartInstance = echarts.init(chartDom)
  }
  
  const option = {
    title: {
      text: '项目状态分布',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: '10%'
    },
    series: [
      {
        name: '项目状态',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '60%'],
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
            fontSize: '20',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: statusData.value
      }
    ],
    color: ['#409eff', '#67c23a', '#e6a23c', '#f56c6c']
  }
  
  statusChartInstance.setOption(option)
  
  // 窗口大小改变时重新调整图表
  window.addEventListener('resize', () => {
    statusChartInstance.resize()
  })
}

// 初始化进度分布图表
const initProgressChart = () => {
  const chartDom = progressChart.value
  if (!chartDom) return
  
  if (!progressChartInstance) {
    progressChartInstance = echarts.init(chartDom)
  }
  
  const option = {
    title: {
      text: '项目进度分布',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
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
      data: progressData.value.map(item => item.name),
      axisTick: {
        alignWithLabel: true
      }
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '项目数量',
        type: 'bar',
        barWidth: '60%',
        data: progressData.value.map(item => ({
          value: item.value,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#83bff6' },
              { offset: 0.5, color: '#188df0' },
              { offset: 1, color: '#188df0' }
            ])
          }
        }))
      }
    ]
  }
  
  progressChartInstance.setOption(option)
  
  window.addEventListener('resize', () => {
    progressChartInstance.resize()
  })
}

// 初始化风险分析图表
const initRiskChart = () => {
  const chartDom = riskChart.value
  if (!chartDom) return
  
  if (!riskChartInstance) {
    riskChartInstance = echarts.init(chartDom)
  }
  
  const option = {
    title: {
      text: '风险等级分析',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [
      {
        name: '风险等级',
        type: 'pie',
        radius: '60%',
        data: riskData.value,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          formatter: '{b}: {c}个\n({d}%)'
        }
      }
    ],
    color: ['#f56c6c', '#e6a23c', '#67c23a']
  }
  
  riskChartInstance.setOption(option)
  
  window.addEventListener('resize', () => {
    riskChartInstance.resize()
  })
}

// 组件挂载时初始化
onMounted(() => {
  fetchData()
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

.chart-value {
  font-weight: bold;
  color: #409eff;
  font-size: 18px;
}

/* 增强的浮动窗口样式 */
.enhanced-drill-down {
  max-width: 100%;
}

.popover-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 16px;
  font-weight: bold;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: 10px;
}

.popover-title .el-icon {
  color: #409eff;
  font-size: 18px;
}

/* 状态网格布局 */
.status-grid, .progress-grid, .risk-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-item, .progress-item, .risk-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background-color: #fafafa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.status-item:hover, .progress-item:hover, .risk-item:hover {
  background-color: #f5f7fa;
  border-color: #409eff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

/* 图标样式 */
.status-icon, .progress-icon, .risk-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-icon-progress {
  background: linear-gradient(135deg, #409eff, #66b3ff);
  color: white;
}

.status-icon-success {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  color: white;
}

.status-icon-planning {
  background: linear-gradient(135deg, #909399, #b3b6bd);
  color: white;
}

.status-icon-paused {
  background: linear-gradient(135deg, #e6a23c, #ebb563);
  color: white;
}

.progress-icon-early {
  background: linear-gradient(135deg, #f56c6c, #f78989);
  color: white;
}

.progress-icon-mid {
  background: linear-gradient(135deg, #e6a23c, #ebb563);
  color: white;
}

.progress-icon-late {
  background: linear-gradient(135deg, #409eff, #66b3ff);
  color: white;
}

.progress-icon-complete {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  color: white;
}

.risk-icon-high {
  background: linear-gradient(135deg, #f56c6c, #f78989);
  color: white;
}

.risk-icon-medium {
  background: linear-gradient(135deg, #e6a23c, #ebb563);
  color: white;
}

.risk-icon-low {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  color: white;
}

.status-icon, .progress-icon, .risk-icon .el-icon {
  font-size: 18px;
}

/* 内容区域 */
.status-content, .progress-content, .risk-content {
  flex: 1;
  min-width: 0;
}

.status-header, .progress-header, .risk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.status-name, .progress-name, .risk-name {
  color: #303133;
  font-size: 15px;
  font-weight: 600;
}

.status-description, .progress-description {
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
}

/* 风险解释样式 */
.risk-explanation {
  margin-top: 8px;
}

.risk-criteria p {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #606266;
}

.risk-criteria ul {
  margin: 0;
  padding-left: 16px;
}

.risk-criteria li {
  margin-bottom: 4px;
  color: #606266;
  font-size: 12px;
  line-height: 1.4;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .enhanced-drill-down {
    max-width: 300px;
  }
  
  .status-item, .progress-item, .risk-item {
    flex-direction: column;
    text-align: center;
  }
  
  .status-header, .progress-header, .risk-header {
    flex-direction: column;
    gap: 8px;
    align-items: center;
  }
}

.charts-section {
  margin-top: 20px;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
}

@media (max-width: 1200px) {
  .charts-section {
    grid-template-columns: 1fr;
  }
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
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

/* 风险管理样式 */
.project-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.project-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.project-leader {
  font-size: 12px;
  color: #606266;
}

.current-task {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-name {
  font-weight: 500;
  color: #303133;
  font-size: 13px;
}

.task-assignee {
  font-size: 12px;
  color: #606266;
}

.date-text {
  font-size: 12px;
  color: #303133;
}

.date-overdue {
  color: #f56c6c;
  font-weight: 600;
}

.date-soon {
  color: #e6a23c;
  font-weight: 600;
}

.warning-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.warning-icon {
  color: #f56c6c;
  font-size: 14px;
}

.normal-info {
  font-size: 12px;
  color: #909399;
}

/* 卡片视图样式 */
.projects-container {
  margin-top: 20px;
}

.view-mode-tabs {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-end;
}



.cards-container {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
}

.project-card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.project-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.project-card.high-risk {
  border-left: 4px solid #ff4d4f;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.project-title h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  cursor: pointer;
  transition: color 0.3s;
}

.project-title h3:hover {
  color: #1890ff;
}

.project-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: #666;
}

.card-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-section {
  margin-bottom: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
  color: #262626;
}

.progress-value {
  font-weight: 600;
  color: #1890ff;
}

.task-flow-section {
  margin-bottom: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 8px;
}

.no-tasks {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: #999;
  background: #f5f5f5;
  border-radius: 4px;
  font-size: 13px;
}

.expand-section {
  margin-bottom: 16px;
  text-align: center;
  border-top: 1px solid #f0f0f0;
  padding-top: 12px;
}

.gantt-section {
  margin-top: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 6px;
}

.loading-gantt {
  padding: 20px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  font-size: 12px;
}

.footer-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.reports {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
}

.warning {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #faad14;
}

.update-time {
  color: #999;
}

.table-container {
  margin-top: 20px;
}

.load-more-section {
  text-align: center;
  margin-top: 24px;
  padding: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .cards-container {
    grid-template-columns: 1fr;
  }
  
  .project-stats {
    flex-wrap: wrap;
    gap: 16px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .card-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}

/* 风险标签样式 */
.risk-high {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 77, 79, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(255, 77, 79, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 77, 79, 0);
  }
}

/* 统计卡片样式 */
.stats-section {
  margin-bottom: 20px;
}

.stat-card {
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.stat-card.total-projects {
  border-left: 4px solid #409eff;
}

.stat-card.in-progress {
  border-left: 4px solid #e6a23c;
}

.stat-card.completed {
  border-left: 4px solid #67c23a;
}

.stat-card.high-risk {
  border-left: 4px solid #f56c6c;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: rgba(64, 158, 255, 0.1);
  border-radius: 12px;
}

.stat-card.in-progress .stat-icon {
  background: rgba(230, 162, 60, 0.1);
}

.stat-card.completed .stat-icon {
  background: rgba(103, 194, 58, 0.1);
}

.stat-card.high-risk .stat-icon {
  background: rgba(245, 108, 108, 0.1);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  font-weight: 500;
}

@media (max-width: 1200px) {
  .stats-section .el-col {
    margin-bottom: 16px;
  }
}
</style>
