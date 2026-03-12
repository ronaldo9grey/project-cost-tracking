<template>
  <div class="daily-report-list">
    <!-- 页面标题和操作栏 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">我的日报</h1>
        <div class="header-actions">
           <el-button 
             type="primary" 
             size="large" 
             @click="handleCreate"
             :loading="loading"
           >
             <el-icon><Plus /></el-icon>
             新建日报
           </el-button>
         </div>
      </div>
    </div>

    <!-- 模式选择弹窗 -->
    <ModeSelector
      v-model="modeSelectorVisible"
      :has-weekly-goal="hasWeeklyGoal"
      @select="handleModeSelect"
      @cancel="modeSelectorVisible = false"
      @create-goal="handleCreateGoal"
    />

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-form :model="filterForm" inline>
        <el-form-item label="日期">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleFilterChange"
          />
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select 
            v-model="filterForm.status" 
            placeholder="选择状态"
            @change="handleFilterChange"
            style="width: 120px;"
          >
            <el-option label="全部" value="" />
            <el-option label="待提交" value="待提交" />
            <el-option label="已提交" value="已提交" />
            <el-option label="待评价" value="待评价" />
            <el-option label="已评价" value="已评价" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button @click="handleResetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 日报列表 -->
    <div class="report-list">
      <el-table 
        :data="reports" 
        v-loading="loading"
        stripe
        :default-sort="{ prop: 'report_date', order: 'descending' }"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="report_date" label="日期" width="120" sortable="custom">
          <template #default="{ row }">
            <span class="date-cell">{{ formatDate(row.report_date) }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="report_mode" label="模式" width="100">
          <template #default="{ row }">
            <el-tag 
              :type="row.report_mode === 'goal' ? 'success' : 'info'"
              size="small"
            >
              {{ row.report_mode === 'goal' ? '关联目标' : '自由填报' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="employee_name" label="员工" min-width="120" show-overflow-tooltip />
        
        <el-table-column prop="tomorrow_plan" label="明日计划" min-width="300" show-overflow-tooltip>
          <template #default="{ row }">
            <el-tooltip 
              :content="row.tomorrow_plan || '-'" 
              placement="top"
              :disabled="!row.tomorrow_plan || row.tomorrow_plan.length <= 20"
            >
              <span class="tomorrow-plan">{{ (row.tomorrow_plan || '-').substring(0, 20) }}{{ (row.tomorrow_plan || '-').length > 20 ? '...' : '' }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        
        <el-table-column prop="work_target" label="工作目标" min-width="300" show-overflow-tooltip>
          <template #default="{ row }">
            <el-tooltip 
              :content="row.work_target || '-'" 
              placement="top"
              :disabled="!row.work_target || row.work_target.length <= 20"
            >
              <span class="work-target">{{ (row.work_target || '-').substring(0, 20) }}{{ (row.work_target || '-').length > 20 ? '...' : '' }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        
        <el-table-column prop="actual_hours" label="工时(小时)" width="120">
          <template #default="{ row }">
            <span class="hours-cell">{{ row.actual_hours || 0 }}小时</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag 
              :type="getStatusTagType(row.status)"
              size="small"
            >
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button 
              size="small" 
              @click="handleView(row)"
              link
            >
              <el-icon><View /></el-icon>
              查看
            </el-button>
            
            <el-button 
              v-if="row.status === '待提交'"
              size="small" 
              @click="handleEdit(row)"
              link
              type="primary"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            
            <el-button 
              v-if="row.status === '待提交'"
              size="small" 
              @click="handleSubmit(row)"
              link
              type="success"
            >
              <el-icon><Upload /></el-icon>
              提交
            </el-button>
            
            <el-button 
              v-if="row.status === '待提交'"
              size="small" 
              @click="handleDelete(row)"
              link
              type="danger"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="删除确认"
      width="400px"
    >
      <div class="delete-confirm">
        <el-icon color="#f56c6c" size="24"><WarningFilled /></el-icon>
        <div class="confirm-text">
          <p>确定要删除这个日报吗？</p>
          <p class="report-info">
            日期：{{ formatDate(deleteTarget?.report_date) }}<br>
            员工：{{ deleteTarget?.employee_name }}
          </p>
          <p class="warning-text">删除后无法恢复，请谨慎操作！</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button 
          type="danger" 
          @click="confirmDelete"
          :loading="deleteLoading"
        >
          确定删除
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, View, Edit, Delete, Upload, WarningFilled } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import {
  getMyReports,
  deleteDailyReport,
  submitDailyReport,
  getCurrentWeekGoal,
  type DailyReport,
  type DailyReportListResponse
} from '../../api/dailyReport'
import ModeSelector from '../DailyReportEdit/components/ModeSelector.vue'

const router = useRouter()

// 数据状态
const reports = ref<DailyReport[]>([])
const loading = ref(false)
const deleteLoading = ref(false)
const deleteDialogVisible = ref(false)
const deleteTarget = ref<DailyReport | null>(null)

// 模式选择相关
const modeSelectorVisible = ref(false)
const hasWeeklyGoal = ref(false)

// 检查是否有本周目标
const checkWeeklyGoal = async () => {
  try {
    const today = new Date().toISOString().split('T')[0]
    await getCurrentWeekGoal(today)
    hasWeeklyGoal.value = true
  } catch (error) {
    hasWeeklyGoal.value = false
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

// 筛选表单
const filterForm = reactive({
  dateRange: getDefaultDateRange(),
  status: ''
})

// 分页数据
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 排序
const sortConfig = reactive({
  prop: 'report_date',
  order: 'descending'
})

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return dateStr
}

// 获取状态标签类型
const getStatusTagType = (status: string) => {
  const typeMap: Record<string, any> = {
    '待提交': 'info',
    '已提交': 'warning',
    '已评价': 'success'
  }
  return typeMap[status] || 'default'
}

// 加载日报列表
const loadReports = async () => {
  console.log('开始加载日报列表数据...')
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...(filterForm.dateRange.length === 2 && {
        start_date: filterForm.dateRange[0],
        end_date: filterForm.dateRange[1]
      }),
      ...(filterForm.status && { status: filterForm.status })
    }

    console.log('请求参数:', params)
    const response = await getMyReports(params)
    console.log('API响应:', response)
    
    if (response.items) {
      console.log('设置数据:', response.items.length, '条记录')
      reports.value = response.items
      pagination.total = response.total
      console.log('数据设置完成，reports长度:', reports.value.length)
    } else {
      console.log('响应中没有items字段:', response)
      reports.value = []
      pagination.total = 0
    }
  } catch (error) {
    console.error('获取日报列表失败:', error)
    ElMessage.error('获取日报列表失败')
  } finally {
    loading.value = false
    console.log('加载完成，设置loading为false')
  }
}

// 事件处理函数
const handleCreate = async () => {
  // 检查今天是否已有日报
  const today = new Date().toISOString().split('T')[0]
  const todayReport = reports.value.find(r => r.report_date === today)
  
  if (todayReport) {
    ElMessage.warning('今天已经创建过日报了，请编辑现有日报')
    // 跳转到编辑页面
    if (todayReport.report_mode === 'goal') {
      router.push(`/daily-report-goal/${todayReport.id}/edit`)
    } else {
      router.push(`/daily-report/${todayReport.id}/edit`)
    }
    return
  }
  
  // 检查是否有本周目标
  await checkWeeklyGoal()
  
  // 显示模式选择弹窗
  modeSelectorVisible.value = true
}

// 处理模式选择
const handleModeSelect = (mode: 'free' | 'goal') => {
  if (mode === 'free') {
    router.push('/daily-report/create')
  } else {
    router.push('/daily-report-goal/create')
  }
}

// 处理跳转到目标制定
const handleCreateGoal = () => {
  router.push('/monthly-goals')
}

const handleView = (row: DailyReport) => {
  // 两种模式查看使用同一个详情页
  router.push(`/daily-report/${row.id}/view`)
}

const handleEdit = (row: DailyReport) => {
  // 根据日报模式跳转到对应编辑页面
  if (row.report_mode === 'goal') {
    router.push(`/daily-report-goal/${row.id}/edit`)
  } else {
    router.push(`/daily-report/${row.id}/edit`)
  }
}

const handleSubmit = async (row: DailyReport) => {
  try {
    await ElMessageBox.confirm(
      `确定要提交这份日报吗？\n日期：${formatDate(row.report_date)}\n员工：${row.employee_name}`,
      '提交确认',
      {
        confirmButtonText: '确定提交',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await submitDailyReport(row.id)
    ElMessage.success('提交成功')
    loadReports()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('提交失败:', error)
      ElMessage.error('提交失败')
    }
  }
}

const handleDelete = (row: DailyReport) => {
  deleteTarget.value = row
  deleteDialogVisible.value = true
}

const confirmDelete = async () => {
  if (!deleteTarget.value) return
  
  deleteLoading.value = true
  try {
    await deleteDailyReport(deleteTarget.value.id)
    ElMessage.success('删除成功')
    deleteDialogVisible.value = false
    deleteTarget.value = null
    loadReports()
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败')
  } finally {
    deleteLoading.value = false
  }
}

const handleFilterChange = () => {
  pagination.page = 1
  loadReports()
}

const handleResetFilter = () => {
  filterForm.dateRange = getDefaultDateRange()
  filterForm.status = ''
  pagination.page = 1
  loadReports()
}

const handleSortChange = ({ prop, order }: any) => {
  sortConfig.prop = prop
  sortConfig.order = order
  pagination.page = 1
  loadReports()
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadReports()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadReports()
}

// 生命周期
onMounted(() => {
  console.log('🚀 日报列表组件已挂载，开始加载数据')
  // 确保日期范围正确设置为当月1日到月末最后一天
  filterForm.dateRange = getDefaultDateRange()
  console.log('页面加载，设置的默认日期范围:', filterForm.dateRange)
  loadReports()
})

// 添加组件卸载时的日志
onUnmounted(() => {
  console.log('🚨 日报列表组件即将卸载')
})
</script>

<style scoped>
.daily-report-list {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.filter-bar {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.report-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.date-cell {
  font-weight: 500;
  color: #409EFF;
}

.work-target {
  color: #606266;
}

.evaluation-status {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.score-info {
  font-size: 12px;
  color: #909399;
}

.pagination-wrapper {
  background: white;
  padding: 20px;
  margin-top: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.delete-confirm {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.confirm-text {
  flex: 1;
}

.report-info {
  background: #f8f9fa;
  padding: 8px 12px;
  border-radius: 4px;
  margin: 8px 0;
  font-size: 14px;
  color: #606266;
}

.warning-text {
  color: #f56c6c;
  font-weight: 500;
  margin: 8px 0 0 0;
}
</style>