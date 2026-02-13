<template>
  <div class="projects-container">
    <h1>项目管理</h1>
    
    <!-- 操作栏 -->
    <el-card shadow="hover" style="margin-bottom: 20px;">
      <el-collapse v-model="activeSearchPanel" accordion>
        <el-collapse-item title="基础搜索" name="basic">
          <div style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
            <el-select 
              v-model="statusFilter" 
              placeholder="项目状态" 
              style="width: 150px;"
              @change="handleSearch"
            >
              <el-option label="全部" value="" />
              <el-option label="规划中" value="规划中" />
              <el-option label="进行中" value="进行中" />
              <el-option label="提前完成" value="提前完成" />
              <el-option label="已完成" value="已完成" />
              <el-option label="延期完成" value="延期完成" />
              <el-option label="已延期" value="已延期" />
              <el-option label="已暂停" value="已暂停" />
              <el-option label="已取消" value="已取消" />
            </el-select>
            <el-input
              v-model="searchQuery"
              placeholder="搜索项目名称"
              style="flex: 1; min-width: 200px;"
              @keyup.enter="handleSearch"
            >
              <template #prepend>
                <el-icon><Document /></el-icon>
              </template>
            </el-input>
            <el-input
              v-model="managerFilter"
              placeholder="搜索项目经理"
              style="flex: 1; min-width: 200px;"
              @keyup.enter="handleSearch"
            >
              <template #prepend>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
            <div style="display: flex; gap: 10px;">
              <el-button @click="handleSearch">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
              <el-button @click="resetSearch">
                <el-icon><RefreshLeft /></el-icon>
                重置
              </el-button>
              <el-button @click="refreshProjectList">
                <el-icon><Refresh /></el-icon>
                刷新列表
              </el-button>
              <el-button @click="openAddProjectDialog">
                <el-icon><Plus /></el-icon>
                新建项目
              </el-button>
            </div>
          </div>
        </el-collapse-item>
        
        <el-collapse-item title="高级搜索" name="advanced">
          <el-row :gutter="20" style="margin-bottom: 15px;">
            <!-- 日期范围搜索 -->
            <el-col :span="8">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                style="width: 100%;"
                @change="handleSearch"
              />
            </el-col>
            
            <!-- 预算范围搜索 -->
            <el-col :span="8">
              <el-input
                v-model="budgetRange"
                placeholder="预算范围，如：100000-200000"
                style="width: 100%;"
                @keyup.enter="handleSearch"
              >
                <template #prepend>
                  <el-icon><Money /></el-icon>
                </template>
              </el-input>
            </el-col>
            
            <!-- 进度范围搜索 -->
            <el-col :span="8">
              <el-input
                v-model="progressRange"
                placeholder="进度范围，如：30-70"
                style="width: 100%;"
                @keyup.enter="handleSearch"
              >
                <template #prepend>
                  <el-icon><DocumentCopy /></el-icon>
                </template>
              </el-input>
            </el-col>
          </el-row>
        </el-collapse-item>
      </el-collapse>
    </el-card>
    
    <!-- 项目统计 -->
    <el-card shadow="hover" style="margin-bottom: 20px;">
      <el-row :gutter="20" style="margin-bottom: 15px;">
        <!-- 第一行：总合同额、预算成本合计、实际成本合计、成本偏差 -->
        <el-col :span="6">
          <el-statistic 
            title="总合同额" 
            :value="projectStatistics.total_contract_amount" 
            prefix="¥" 
            :precision="2" 
            class="statistic-orange"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic 
            title="预算成本合计" 
            :value="projectStatistics.total_budget_cost" 
            prefix="¥" 
            :precision="2" 
            class="statistic-orange"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic 
            title="实际成本合计" 
            :value="projectStatistics.total_actual_cost" 
            prefix="¥" 
            :precision="2" 
            class="statistic-orange"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic 
            title="成本偏差" 
            :value="projectStatistics.cost_variance" 
            prefix="¥" 
            :precision="2" 
            :class="projectStatistics.cost_variance > 0 ? 'statistic-red' : (projectStatistics.cost_variance < 0 ? 'statistic-green' : '')"
          />
        </el-col>
      </el-row>
      
      <!-- 分割线 -->
      <el-divider style="margin: 15px 0;"></el-divider>
      
      <el-row :gutter="20" style="margin-bottom: 15px;">
        <!-- 第二行：总项目数、已完成、已延期、已暂停 -->
        <el-col :span="6">
          <el-statistic 
            title="总项目数" 
            :value="projectStatistics.total_projects" 
            class="statistic-blue"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic 
            title="已完成" 
            :value="projectStatistics.status_counts['已完成'] || 0" 
            class="statistic-green"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic 
            title="已延期" 
            :value="projectStatistics.status_counts['已延期'] || 0" 
            class="statistic-red"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic 
            title="已暂停" 
            :value="projectStatistics.status_counts['已暂停'] || 0" 
          />
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <!-- 第三行：进行中、提前完成、延期完成、已取消 -->
        <el-col :span="6">
          <el-statistic 
            title="进行中" 
            :value="projectStatistics.status_counts['进行中'] || 0" 
            class="statistic-blue"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic 
            title="提前完成" 
            :value="projectStatistics.status_counts['提前完成'] || 0" 
            class="statistic-green"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic 
            title="延期完成" 
            :value="projectStatistics.status_counts['延期完成'] || 0" 
            class="statistic-red"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic 
            title="已取消" 
            :value="projectStatistics.status_counts['已取消'] || 0" 
          />
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 项目列表 -->
    <el-card shadow="hover">
      <el-table 
        :data="filteredProjects" 
        style="width: 100%"
        @row-dblclick="viewProjectDetails"
        v-loading="loading"
        element-loading-text="加载中..."
        element-loading-spinner="el-icon-loading"
        element-loading-background="rgba(255, 255, 255, 0.8)"
      >
        <el-table-column prop="name" label="项目名称" sortable>
          <template #default="scope">
            <div class="project-name" @click="viewProjectDetails(scope.row)">
              {{ scope.row.name }}
            </div>
          </template>
        </el-table-column>
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
              :percentage="scope.row.status === '进行中' ? scope.row.progress : 100" 
              :status="getProgressStatus(scope.row.status, scope.row.progress)" 
              :stroke-width="10"
            ></el-progress>
          </template>
        </el-table-column>
        <el-table-column prop="contract_amount" label="合同金额" sortable>
          <template #default="scope">
            ¥ {{ formatCurrency(scope.row.contract_amount || 0) }}
          </template>
        </el-table-column>
        <el-table-column prop="budget_total_cost" label="预算成本" sortable>
          <template #default="scope">
            ¥ {{ formatCurrency(scope.row.budget_total_cost || 0) }}
          </template>
        </el-table-column>
        <el-table-column prop="actual_total_cost" label="实际成本" sortable>
          <template #default="scope">
            ¥ {{ formatCurrency(scope.row.actual_total_cost || 0) }}
          </template>
        </el-table-column>
        <el-table-column prop="leader" label="项目经理" sortable />
        <el-table-column prop="start_date" label="开始日期" sortable>
          <template #default="scope">
            {{ formatDate(scope.row.start_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="计划结束日期" label="计划结束日期" sortable>
          <template #default="scope">
            {{ formatDate(scope.row.计划结束日期) }}
          </template>
        </el-table-column>
        <el-table-column prop="实际结束日期" label="实际结束日期" sortable>
          <template #default="scope">
            {{ scope.row.实际结束日期 ? formatDate(scope.row.实际结束日期) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="viewProjectDetails(scope.row)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button type="warning" size="small" @click="editProject(scope.row)">
              <el-icon><EditPen /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="deleteProjectHandler(scope.row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div style="margin-top: 10px; text-align: right;">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalProjects"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Plus,
  Refresh,
  View,
  EditPen,
  Delete,
  Download,
  User,
  Money,
  DocumentCopy,
  Search,
  RefreshLeft,
  Document
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getProjects,
  createProject,
  updateProject,
  deleteProject,
  getProjectOverviewStatistics,
  type Project,
  type ProjectCreate,
  type ProjectUpdate
} from '../../api/project'
import {
  getPersonnel,
  type Personnel
} from '../../api/resource'

const router = useRouter()

// 项目数据
const projects = ref<Project[]>([])

// 加载状态
const loading = ref(false)

// 总项目数
const totalProjects = ref(0)

// 人员列表数据
const personnelList = ref<Personnel[]>([])

// 搜索查询
const searchQuery = ref('')

// 状态筛选
const statusFilter = ref('')

// 活跃的搜索面板
const activeSearchPanel = ref<string[]>(['basic'])

// 项目经理筛选
const managerFilter = ref('')

// 日期范围筛选
const dateRange = ref<[Date, Date] | null>(null)

// 预算范围筛选
const budgetRange = ref('')

// 进度范围筛选
const progressRange = ref('')

// 分页数据
const currentPage = ref<number>(1)
const pageSize = ref<number>(50)

// 获取项目列表
const fetchProjects = async () => {
  try {
    loading.value = true
    const response = await getProjects({
      page: currentPage.value,
      size: pageSize.value,
      status: statusFilter.value || undefined,
      name: searchQuery.value || undefined
    })
    
    // 检查响应格式，使用items和total字段
    if (response && typeof response === 'object' && 'items' in response && 'total' in response) {
      projects.value = response.items
      totalProjects.value = response.total
    } else if (Array.isArray(response)) {
      // 兼容旧格式
      projects.value = response
      totalProjects.value = response.length
    }
    loading.value = false
  } catch (error) {
    console.error('获取项目列表失败:', error)
    loading.value = false
  }
}

// 获取人员列表
const fetchPersonnel = async () => {
  try {
    const response = await getPersonnel({
      limit: 1000 // 获取所有人员
    })
    personnelList.value = response
  } catch (error) {
    console.error('获取人员列表失败:', error)
    ElMessage.error('获取人员列表失败')
  }
}

// 过滤后的项目列表
const filteredProjects = computed(() => {
  return projects.value.filter(project => {
    // 状态筛选
    if (statusFilter.value && project.status !== statusFilter.value) {
      return false
    }
    
    // 搜索筛选
    if (searchQuery.value) {
      const searchLower = searchQuery.value.toLowerCase()
      if (!project.name.toLowerCase().includes(searchLower)) {
        return false
      }
    }
    
    // 项目经理筛选
    if (managerFilter.value) {
      const managerLower = managerFilter.value.toLowerCase()
      if (!project.leader.toLowerCase().includes(managerLower)) {
        return false
      }
    }
    
    // 日期范围筛选
    if (dateRange.value) {
      const projectStartDate = new Date(project.start_date)
      const projectEndDate = new Date(project["计划结束日期"])
      const [startDate, endDate] = dateRange.value
      
      // 检查项目日期范围是否与筛选范围有重叠
      if (projectEndDate < startDate || projectStartDate > endDate) {
        return false
      }
    }
    
    // 预算范围筛选
    if (budgetRange.value) {
      const budgetMatch = budgetRange.value.match(/^(\d+)-(\d+)$/)
      if (budgetMatch) {
        const [, minBudget, maxBudget] = budgetMatch
        if (project.budget_total_cost < parseFloat(minBudget) || project.budget_total_cost > parseFloat(maxBudget)) {
          return false
        }
      }
    }
    
    // 进度范围筛选
    if (progressRange.value) {
      const progressMatch = progressRange.value.match(/^(\d+)-(\d+)$/)
      if (progressMatch) {
        const [, minProgress, maxProgress] = progressMatch
        if (project.progress < parseFloat(minProgress) || project.progress > parseFloat(maxProgress)) {
          return false
        }
      }
    }
    
    return true
  })
})



// 打开添加项目页面（多步骤）
const openAddProjectDialog = () => {
  console.log('DEBUG: [新建项目] 点击新建按钮，准备跳转到 ProjectCreateStep1')
  // 跳转到多步骤新建项目的第一步，统一使用query参数传递mode
  router.push({ 
    name: 'ProjectCreateStep1',
    query: { mode: 'create' }
  })
  console.log('DEBUG: [新建项目] 已执行跳转，跳转参数: { name: "ProjectCreateStep1", query: { mode: "create" } }')
}

// 编辑项目
const editProject = (row: Project) => {
  // 跳转到多步骤编辑项目页面，使用正确的命名路由
  router.push({ name: 'ProjectEditStep1', params: { projectId: row.id } })
}

// 查看项目详情
const viewProjectDetails = (row: Project) => {
  // 跳转到项目详情页面
  router.push(`/projects/${row.id}`)
}

// 删除项目
const deleteProjectHandler = async (row: Project) => {
  ElMessageBox.confirm('确定要删除这个项目吗？', '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      loading.value = true
      await deleteProject(row.id)
      await fetchProjects()
      ElMessage.success('项目已删除')
    } catch (error) {
      console.error('删除项目失败:', error)
    } finally {
      loading.value = false
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}



// 刷新项目列表
const refreshProjectList = async () => {
  try {
    loading.value = true
    await fetchProjects()
    ElMessage.success('项目列表已刷新')
  } catch (error) {
    console.error('刷新项目列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 分页处理
const handleSizeChange = async (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  await fetchProjects()
}

const handleCurrentChange = async (val: number) => {
  currentPage.value = val
  await fetchProjects()
}

// 处理搜索
const handleSearch = async () => {
  currentPage.value = 1
  await fetchProjects()
}

// 重置搜索条件
const resetSearch = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  managerFilter.value = ''
  dateRange.value = null
  budgetRange.value = ''
  progressRange.value = ''
  currentPage.value = 1
  fetchProjects()
}

// 处理表格行双击事件
const handleRowDoubleClick = (row: Project) => {
  viewProjectDetails(row)
}

// 格式化日期
const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}

// 格式化金额为金融风格
const formatCurrency = (amount: number) => {
  return amount.toLocaleString('zh-CN', { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  })
}

// 根据状态获取标签类型
const getStatusType = (status: string) => {
  const statusMap: any = {
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

// 根据状态和进度获取进度条状态
const getProgressStatus = (status: string, progress: number) => {
  if (status === '进行中') {
    if (progress === 100) return 'success'
    if (progress < 30) return 'exception'
    return ''
  } else if (status === '提前完成' || status === '已完成') {
    return 'success'
  } else if (status === '延期完成') {
    return 'warning'
  }
  return ''
}

// 全局统计数据
const projectStatistics = ref({
  total_projects: 0,
  status_counts: {},
  total_contract_amount: 0,
  total_budget_cost: 0,
  total_actual_cost: 0,
  cost_variance: 0,
  avg_progress: 0
})

// 获取全局统计数据
const fetchProjectStatistics = async () => {
  try {
    // 使用现有的统计端点获取全局统计数据
    const response = await getProjectOverviewStatistics()
    if (response && typeof response === 'object') {
      projectStatistics.value = response
    }
  } catch (error) {
    console.error('获取项目统计数据失败:', error)
  }
}

// 初始加载数据
onMounted(async () => {
  await Promise.all([
    fetchProjects(),
    fetchProjectStatistics(),
    fetchPersonnel()
  ])
})
</script>

<style scoped>
.projects-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100%;
}

h1 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #303133;
}



/* 统计数字颜色样式 */
:deep(.statistic-orange .el-statistic__content) {
  color: #ff7d00;
  font-weight: bold;
}

:deep(.statistic-blue .el-statistic__content) {
  color: #1890ff;
  font-weight: bold;
}

:deep(.statistic-green .el-statistic__content) {
  color: #52c41a;
  font-weight: bold;
}

:deep(.statistic-red .el-statistic__content) {
  color: #ff4d4f;
  font-weight: bold;
}
</style>