<template>
  <div class="daily-report-evaluation">
    <!-- 页面标题和统计信息 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">日报评价</h1>
        <div class="header-actions">
          <div class="statistics">
            <el-statistic title="待评价日报" :value="statistics.pending" value-style="color: #e6a23c;">
            </el-statistic>
            <el-statistic title="已评价日报" :value="statistics.evaluated" value-style="color: #67c23a;">
            </el-statistic>
            <el-statistic title="评价进度" :value="statistics.progress" suffix="%" value-style="color: #409eff;">
            </el-statistic>
          </div>

        </div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-form :model="filterForm" inline>
        <el-form-item label="员工姓名">
          <el-input
            v-model="filterForm.employee_name"
            placeholder="输入员工姓名"
            style="width: 200px;"
            clearable
            @change="handleFilterChange"
          />
        </el-form-item>
        
        <el-form-item label="部门">
          <el-select 
            v-model="filterForm.department" 
            placeholder="选择部门"
            style="width: 150px;"
            clearable
            @change="handleFilterChange"
          >
            <el-option
              v-for="dept in departments"
              :key="dept"
              :label="dept"
              :value="dept"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="评价状态">
          <el-select 
            v-model="filterForm.evaluation_status" 
            placeholder="选择状态"
            style="width: 150px;"
            clearable
            @change="handleFilterChange"
          >
            <el-option label="待评价" value="pending" />
            <el-option label="已评价" value="evaluated" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 280px;"
            @change="handleFilterChange"
          />
        </el-form-item>
        
        <!-- 查询和重置按钮 -->
        <el-form-item>
          <el-button 
            type="primary" 
            size="default" 
            @click="refreshData"
            :loading="loading"
            style="margin-left: 20px;"
          >
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button 
            size="default" 
            @click="resetFilters"
            style="margin-left: 10px;"
          >
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 日报列表 -->
    <div class="report-list">
      <el-table 
          v-loading="loading"
          :data="filteredReports"
          element-loading-text="加载中..."
          style="width: 100%; margin-top: 20px; min-width: 1300px;"
          :row-class-name="getRowClassName"
        >
          
          <el-table-column prop="report_date" label="日期" width="100" sortable />
          <el-table-column prop="employee_name" label="员工姓名" width="100" />
          <el-table-column prop="department" label="部门" width="150" />
          <el-table-column prop="position" label="职位" width="150" />
          <el-table-column prop="work_target" label="工作目标" min-width="400" show-overflow-tooltip />
          <el-table-column label="评价状态" width="100">
            <template #default="scope">
              <el-tag 
                :type="scope.row.evaluation ? 'success' : 'warning'"
                size="small"
              >
                {{ scope.row.evaluation ? '已评价' : '待评价' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="评分" width="100">
            <template #default="scope">
              <div v-if="scope.row.evaluation">
                <el-tag 
                  :type="getScoreType(convertScoreToGrade(scope.row.evaluation.supervisor_score))"
                  size="small"
                >
                  {{ convertScoreToGrade(scope.row.evaluation.supervisor_score) }}
                </el-tag>
              </div>
              <span v-else class="no-score">未评价</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="scope">
              <el-button 
                :type="scope.row.evaluation ? 'info' : 'primary'"
                size="small" 
                @click="scope.row.evaluation ? viewEvaluation(scope.row) : evaluateReport(scope.row)"
              >
                <el-icon><Edit v-if="!scope.row.evaluation" /><View v-else /></el-icon>
                {{ scope.row.evaluation ? '查看' : '评价' }}
              </el-button>
            </template>
          </el-table-column>
      </el-table>
    </div>

    <!-- 评价对话框 -->
    <el-dialog
      v-model="evaluationDialogVisible"
      :title="evaluationDialogTitle"
      width="600px"
      @close="resetEvaluationForm"
    >
      <el-form 
        ref="evaluationForm" 
        :model="evaluationFormData" 
        label-width="100px"
      >
        <el-form-item label="日报日期">
          <span class="evaluation-info">{{ currentReport?.report_date }} - {{ currentReport?.employee_name }}</span>
        </el-form-item>
        
        <el-form-item label="工作表现" :required="dialogMode === 'evaluate'">
          <div class="score-section">
            <label>评价等级：</label>
            <!-- 评价模式：显示可编辑的单选按钮 -->
            <div v-if="dialogMode === 'evaluate'">
              <el-radio-group v-model="evaluationFormData.supervisor_score">
                <el-radio-button label="A" class="grade-a">优秀</el-radio-button>
                <el-radio-button label="B" class="grade-b">良好</el-radio-button>
                <el-radio-button label="C" class="grade-c">一般</el-radio-button>
                <el-radio-button label="D" class="grade-d">较差</el-radio-button>
                <el-radio-button label="E" class="grade-e">很差</el-radio-button>
              </el-radio-group>
            </div>
            <!-- 查看模式：显示只读的标签 -->
            <div v-else>
              <el-tag 
                v-if="evaluationFormData.supervisor_score"
                :type="getScoreType(evaluationFormData.supervisor_score)"
                size="large"
              >
                {{ evaluationFormData.supervisor_score }}
              </el-tag>
              <span v-else class="no-score">未评价</span>
            </div>
          </div>
        </el-form-item>
        
        <el-form-item label="评价内容">
          <el-input 
            v-model="evaluationFormData.supervisor_comment" 
            type="textarea" 
            :rows="4"
            placeholder="请输入对员工工作的评价和建议"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="evaluationDialogVisible = false">
            {{ dialogMode === 'view' ? '关闭' : '取消' }}
          </el-button>
          <!-- 只在评价模式下显示提交按钮 -->
          <el-button 
            v-if="dialogMode === 'evaluate'"
            type="primary" 
            @click="submitEvaluation"
            :loading="submitting"
            :disabled="!evaluationFormData.supervisor_score"
          >
            提交评价
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Refresh, 
  Edit, 
  View, 
  Document,
  Star,
  Search
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
// 导入评价相关API
import { 
  getSubordinateReports,
  evaluateDailyReport,
  getEvaluationStats
} from '../../api/dailyReportEvaluation'

// 接口定义
interface ReportItem {
  work_content: string
  start_time: string
  end_time: string
  result: string
  evaluation: string
}

interface ReportEvaluation {
  supervisor_score: string
  supervisor_comment: string
  supervisor_id: string
  supervisor_name: string
  evaluated_at: string
}

interface DailyReport {
  id: number
  report_date: string
  employee_id: string
  employee_name: string
  department: string
  position: string
  tomorrow_plan: string
  planned_hours: number
  work_items: ReportItem[]
  evaluation: ReportEvaluation | null
}

interface EvaluationStats {
  pending: number
  evaluated: number
  progress: number
}

// 响应式数据
const loading = ref(false)
const submitting = ref(false)
const reports = ref<DailyReport[]>([])
const departments = ref<string[]>([])

// 统计数据
const statistics = ref<EvaluationStats>({
  pending: 0,
  evaluated: 0,
  progress: 0
})

// 获取默认日期范围（当月1号到最后一天）
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

// 筛选表单
const filterForm = ref({
  employee_name: '',
  department: '',
  evaluation_status: '',
  dateRange: getDefaultDateRange()
})

// 重置日期范围到默认值
const resetDateRange = () => {
  filterForm.value.dateRange = getDefaultDateRange()
}

// 重置所有筛选条件
const resetFilters = () => {
  filterForm.value.employee_name = ''
  filterForm.value.department = ''
  filterForm.value.evaluation_status = ''
  filterForm.value.dateRange = getDefaultDateRange()
  refreshData()
}

// 评价对话框
const evaluationDialogVisible = ref(false)
const evaluationDialogTitle = ref('评价日报')
const dialogMode = ref<'evaluate' | 'view'>('evaluate')  // 对话框模式：评价或查看
const currentReport = ref<DailyReport | null>(null)
const evaluationForm = ref()
const evaluationFormData = ref({
  supervisor_score: '',
  supervisor_comment: ''
})

// 计算属性
const filteredReports = computed(() => {
  let result = reports.value
  
  if (filterForm.value.employee_name) {
    result = result.filter(report => 
      report.employee_name.toLowerCase().includes(filterForm.value.employee_name.toLowerCase())
    )
  }
  
  if (filterForm.value.department) {
    result = result.filter(report => report.department === filterForm.value.department)
  }
  
  if (filterForm.value.evaluation_status) {
    result = result.filter(report => {
      if (filterForm.value.evaluation_status === 'pending') {
        return !report.evaluation
      } else if (filterForm.value.evaluation_status === 'evaluated') {
        return !!report.evaluation
      }
      return true
    })
  }
  
  if (filterForm.value.dateRange && filterForm.value.dateRange.length === 2) {
    const [startDate, endDate] = filterForm.value.dateRange
    result = result.filter(report => 
      report.report_date >= startDate && report.report_date <= endDate
    )
  }
  
  return result
})

// 重新登录函数
const reLoginIfNeeded = async () => {
  console.log('尝试重新登录...')
  
  // 获取存储的用户名
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
  const username = currentUser.username || currentUser.employee_id || 'admin'
  const password = '123456'  // 默认密码
  
  try {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    
    const loginResponse = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData
    })
    
    if (loginResponse.ok) {
      const loginData = await loginResponse.json()
      
      if (loginData.code === 200 && loginData.data?.access_token) {
        const newToken = loginData.data.access_token
        console.log('重新登录成功:', loginData)
        
        // 保存新token
        localStorage.setItem('token', newToken)
        
        // 保存用户信息
        const userInfo = {
          id: '1',
          employee_id: username,
          employee_name: currentUser.employee_name || currentUser.name || username,
          name: currentUser.employee_name || currentUser.name || username,
          username: username
        }
        localStorage.setItem('currentUser', JSON.stringify(userInfo))
        
        console.log('✅ 重新登录成功，token已更新')
        return newToken
      } else {
        console.log('❌ 重新登录响应格式错误:', loginData)
        return null
      }
    } else {
      console.log('❌ 重新登录失败:', loginResponse.status, await loginResponse.text())
      return null
    }
  } catch (error) {
    console.error('❌ 重新登录异常:', error)
    return null
  }
}

// 方法定义
const loadData = async () => {
  loading.value = true
  try {
    console.log('开始加载日报评价数据...')
    
    // 获取当前用户信息
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
    const userId = currentUser.id || currentUser.employee_id || currentUser.username
    console.log('当前用户信息:', currentUser)
    console.log('用户ID:', userId)
    
    // 加载管辖员工的日报（后端自动使用当前用户ID过滤）
    let reportsResponse
    try {
      // 检查日期范围是否为空，如果为空则使用默认范围
      const dateRange = filterForm.value.dateRange
      const startDate = dateRange && dateRange.length > 0 ? dateRange[0] : getDefaultDateRange()[0]
      const endDate = dateRange && dateRange.length > 0 ? dateRange[1] : getDefaultDateRange()[1]
      
      reportsResponse = await getSubordinateReports({
        start_date: startDate,
        end_date: endDate
      })
      console.log('日报响应数据:', reportsResponse)
    } catch (error) {
      console.log('获取日报数据失败，尝试重新登录:', error)
      const newToken = await reLoginIfNeeded()
      if (newToken) {
        console.log('重新登录成功，重试获取日报数据...')
        // 重新检查日期范围
        const dateRange = filterForm.value.dateRange
        const startDate = dateRange && dateRange.length > 0 ? dateRange[0] : getDefaultDateRange()[0]
        const endDate = dateRange && dateRange.length > 0 ? dateRange[1] : getDefaultDateRange()[1]
        
        reportsResponse = await getSubordinateReports({
          start_date: startDate,
          end_date: endDate
        })
        console.log('重试后日报响应数据:', reportsResponse)
      } else {
        throw error
      }
    }
    
    // 处理响应数据 - 适配后端返回格式
    const reportsData = reportsResponse.data || reportsResponse.value || reportsResponse || []
    
    // 加载统计数据（后端自动使用当前用户ID过滤）
    let statsResponse
    try {
      // 检查日期范围是否为空，如果为空则使用默认范围
      const dateRange = filterForm.value.dateRange
      const startDate = dateRange && dateRange.length > 0 ? dateRange[0] : getDefaultDateRange()[0]
      const endDate = dateRange && dateRange.length > 0 ? dateRange[1] : getDefaultDateRange()[1]
      
      statsResponse = await getEvaluationStats({
        start_date: startDate,
        end_date: endDate
      })
      console.log('统计响应数据:', statsResponse)
    } catch (error) {
      console.log('获取统计数据失败，尝试重新登录:', error)
      const newToken = await reLoginIfNeeded()
      if (newToken) {
        console.log('重新登录成功，重试获取统计数据...')
        // 重新检查日期范围
        const dateRange = filterForm.value.dateRange
        const startDate = dateRange && dateRange.length > 0 ? dateRange[0] : getDefaultDateRange()[0]
        const endDate = dateRange && dateRange.length > 0 ? dateRange[1] : getDefaultDateRange()[1]
        
        statsResponse = await getEvaluationStats({
          start_date: startDate,
          end_date: endDate
        })
        console.log('重试后统计响应数据:', statsResponse)
      } else {
        throw error
      }
    }
    
    // 处理统计数据
    const statsData = statsResponse.data || statsResponse.value || {
      pending_count: 0,
      evaluated_count: 0,
      total_count: 0,
      progress: 0
    }
    
    reports.value = Array.isArray(reportsData) ? reportsData : []
    
    // 映射后端字段名到前端字段名
    statistics.value = {
      pending: statsData.pending_count || 0,
      evaluated: statsData.evaluated_count || 0,
      progress: statsData.progress || 0
    }
    
    // 提取部门列表
    const deptSet = new Set<string>()
    reports.value.forEach(report => {
      if (report.department && report.department !== '未设置') {
        deptSet.add(report.department)
      }
    })
    departments.value = Array.from(deptSet).sort()
    
    console.log('处理后的数据:', {
      reportsCount: reports.value.length,
      statistics: statistics.value,
      departments: departments.value
    })
    
    ElMessage.success('数据加载成功')
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadData()
}

const handleFilterChange = () => {
  // 筛选变化时重新计算
}

const getRowClassName = ({ row }: { row: DailyReport }) => {
  return row.evaluation ? '' : 'pending-row'
}

const getWorkEvaluationType = (evaluation: string) => {
  switch (evaluation) {
    case 'A': return 'success'
    case 'B': return 'warning' 
    case 'C': return 'danger'
    default: return 'info'
  }
}

const getWorkEvaluationText = (evaluation: string) => {
  switch (evaluation) {
    case 'A': return '优秀'
    case 'B': return '良好'
    case 'C': return '需改进'
    default: return '未评价'
  }
}

const getScoreType = (score: string) => {
  switch (score) {
    case 'A': return 'success'
    case 'B': return 'primary'
    case 'C': return 'warning'
    case 'D': return 'danger'
    case 'E': return 'info'
    default: return 'default'
  }
}

// 整数到ABCDE转换函数
const convertScoreToGrade = (score: number | string): string => {
  // 如果已经是字符串，直接返回
  if (typeof score === 'string') {
    return score
  }
  
  // 整数转换为ABCDE
  const intToGrade = {
    5: 'A',  // 超目标达成
    4: 'B',  // 按目标达成
    3: 'C',  // 达成目标80%
    2: 'D',  // 达成目标50%-80%
    1: 'E'   // 小于目标50%
  }
  return intToGrade[score as keyof typeof intToGrade] || 'E'
}

const formatDateTime = (datetime: string) => {
  return new Date(datetime).toLocaleString('zh-CN')
}

const router = useRouter()

const evaluateReport = (report: DailyReport) => {
  // 跳转到日报详情页面进行评价
  router.push(`/daily-report/${report.id}/evaluate`)
}

const viewReport = (report: DailyReport) => {
  // 查看日报详情，不跳转页面
  currentReport.value = report
  evaluationDialogTitle.value = `查看日报 - ${report.employee_name} (${report.report_date})`
  
  // 如果已有评价，显示评价信息
  if (report.evaluation) {
    evaluationFormData.value = {
      supervisor_score: report.evaluation.supervisor_score,
      supervisor_comment: report.evaluation.supervisor_comment
    }
  } else {
    evaluationFormData.value = {
      supervisor_score: '',
      supervisor_comment: ''
    }
  }
  evaluationDialogVisible.value = true
}

const viewEvaluation = (report: DailyReport) => {
  // 跳转到评价详情页面查看模式
  router.push(`/daily-report/${report.id}/evaluate?view=true`)
}

const resetEvaluationForm = () => {
  evaluationFormData.value = {
    supervisor_score: '',
    supervisor_comment: ''
  }
}

const submitEvaluation = async () => {
  if (!currentReport.value || !evaluationFormData.value.supervisor_score) {
    ElMessage.error('请选择评价等级')
    return
  }
  
  submitting.value = true
  try {
    await evaluateDailyReport({
      report_id: currentReport.value.id,
      supervisor_score: evaluationFormData.value.supervisor_score,
      supervisor_comment: evaluationFormData.value.supervisor_comment
    })
    
    ElMessage.success('评价提交成功')
    evaluationDialogVisible.value = false
    loadData() // 重新加载数据
  } catch (error) {
    console.error('提交评价失败:', error)
    ElMessage.error('提交评价失败')
  } finally {
    submitting.value = false
  }
}

// 初始化
onMounted(() => {
  // 确保日期范围正确设置为当月1日到月末最后一天
  filterForm.value.dateRange = getDefaultDateRange()
  console.log('页面加载，设置的默认日期范围:', filterForm.value.dateRange)
  loadData()
})
</script>

<style scoped>
.daily-report-evaluation {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100%;
  width: 100%;
  overflow-x: auto;
}

.page-header {
  margin-bottom: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 24px;
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 30px;
}

.statistics {
  display: flex;
  gap: 30px;
}

.statistics .el-statistic {
  text-align: center;
}

.filter-bar {
  margin-bottom: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.report-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.report-detail {
  padding: 20px;
  background-color: #fafafa;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h4 {
  margin-bottom: 10px;
  color: #303133;
  font-weight: 600;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 5px;
}

.detail-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.detail-item {
  display: flex;
  align-items: center;
}

.detail-item label {
  font-weight: 500;
  color: #606266;
  margin-right: 8px;
  min-width: 80px;
}

.detail-item span {
  color: #303133;
}

.work-items-section {
  margin-top: 20px;
}

.work-items-section h4 {
  margin-bottom: 10px;
  color: #303133;
  font-weight: 600;
}

.score-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.evaluation-info {
  font-weight: 500;
  color: #409eff;
}

.score-text {
  margin-left: 8px;
  color: #909399;
  font-size: 12px;
}

.no-score {
  color: #c0c4cc;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 表格行样式 */
:deep(.pending-row) {
  background-color: #fef0f0;
}

:deep(.pending-row:hover) {
  background-color: #fde2e2 !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: space-between;
  }
  
  .statistics {
    justify-content: space-around;
  }
  
  .detail-content {
    grid-template-columns: 1fr;
  }
}
</style>