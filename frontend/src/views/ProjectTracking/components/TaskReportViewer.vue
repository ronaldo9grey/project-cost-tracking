<template>
  <el-dialog
    :model-value="modelValue"
    :title="`任务: ${taskInfo?.task_name || '任务'} - 关联日报`"
    width="80%"
    top="5vh"
    @update:model-value="$emit('update:modelValue', $event)"
    @close="$emit('close')"
  >
    <div class="task-report-viewer">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="6" animated />
      </div>

      <!-- 任务基本信息 -->
      <div v-else-if="taskInfo" class="task-info">
        <el-card shadow="never" class="task-basic-card">
          <template #header>
            <div class="card-header">
              <h3 class="section-title">
                <el-icon><List /></el-icon>
                任务基本信息
              </h3>
            </div>
          </template>
          
          <el-descriptions :column="3" border class="task-descriptions">
            <el-descriptions-item label="任务名称">
              {{ taskInfo.task_name }}
            </el-descriptions-item>
            <el-descriptions-item label="负责人">
              {{ taskInfo.assignee || '未分配' }}
            </el-descriptions-item>
            <el-descriptions-item label="计划进度">
              {{ taskInfo.planned_progress || 0 }}%
            </el-descriptions-item>
            <el-descriptions-item label="实际进度">
              <div class="progress-info">
                <el-progress
                  :percentage="taskInfo.current_progress || 0"
                  :status="getProgressStatus(taskInfo.current_progress || 0)"
                  :stroke-width="8"
                  style="width: 150px"
                />
                <span class="progress-text">{{ taskInfo.current_progress || 0 }}%</span>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="开始日期">
              {{ formatDate(taskInfo.planned_start) }}
            </el-descriptions-item>
            <el-descriptions-item label="结束日期">
              {{ formatDate(taskInfo.planned_end) }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusTagType(taskInfo.status)" size="small">
                {{ taskInfo.status }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="延迟天数">
              <span v-if="taskInfo.delay_days > 0" class="delay-text">
                {{ taskInfo.delay_days }}天
              </span>
              <span v-else class="normal-text">正常</span>
            </el-descriptions-item>
            <el-descriptions-item label="关联日报数">
              <el-badge :value="relatedReports.length" class="reports-badge">
                <el-icon><Document /></el-icon>
              </el-badge>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </div>

      <!-- 关联日报列表 -->
      <div class="reports-section">
        <el-card shadow="never" class="reports-card">
          <template #header>
            <div class="card-header">
              <h3 class="section-title">
                <el-icon><Document /></el-icon>
                关联日报 ({{ relatedReports.length }}条)
              </h3>
              <div class="reports-filter">
                <el-select
                  v-model="reportFilter"
                  placeholder="筛选类型"
                  size="small"
                  style="width: 150px"
                >
                  <el-option label="全部" value="" />
                  <el-option label="有CDE评价" value="cde" />
                  <el-option label="无CDE评价" value="no_cde" />
                </el-select>
              </div>
            </div>
          </template>
          
          <div v-if="filteredReports.length === 0" class="no-reports">
            <el-empty description="暂无关联日报" />
          </div>
          
          <div v-else class="reports-timeline">
            <el-timeline>
              <el-timeline-item
                v-for="report in filteredReports"
                :key="report.id"
                :timestamp="formatDate(report.report_date)"
                :type="getReportType(report)"
                :size="getReportSize(report)"
              >
                <el-card class="report-card" shadow="hover">
                  <div class="report-header">
                    <div class="reporter-info">
                      <el-icon><User /></el-icon>
                      <span class="reporter-name">{{ report.employee_name }}</span>
                      <el-tag size="small" type="info">{{ report.employee_id }}</el-tag>
                    </div>
                    <div class="report-meta">
                      <el-tag size="small" type="success">{{ report.hours_spent }}小时</el-tag>
                      <el-tag
                        v-if="report.has_cde_evaluation"
                        size="small"
                        type="warning"
                        class="cde-tag"
                      >
                        <el-icon><Star /></el-icon>
                        CDE评价
                      </el-tag>
                    </div>
                  </div>

                  <div class="report-content">
                    <div class="work-content">
                      <h4 class="content-title">工作内容</h4>
                      <p class="content-text">{{ report.work_content }}</p>
                    </div>

                    <!-- CDE评价内容 -->
                    <div v-if="report.has_cde_evaluation" class="cde-evaluation">
                      <el-divider content-position="left">
                        <el-icon><Star /></el-icon>
                        CDE自我评价
                      </el-divider>
                      <div class="evaluation-content">
                        <div v-if="report.cde_evaluation_score" class="evaluation-score">
                          <span class="score-label">评分:</span>
                          <el-rate
                            v-model="report.cde_evaluation_score"
                            disabled
                            show-score
                            text-color="#ff9900"
                            score-template="{value}/5"
                          />
                        </div>
                        <div v-if="report.cde_evaluation_content" class="evaluation-text">
                          <h5 class="evaluation-title">评价内容:</h5>
                          <p class="evaluation-desc">{{ report.cde_evaluation_content }}</p>
                        </div>
                      </div>
                    </div>

                    <!-- 进度贡献 -->
                    <div class="progress-contribution">
                      <h4 class="contribution-title">对任务进度贡献</h4>
                      <div class="contribution-info">
                        <el-progress
                          :percentage="report.progress_contribution"
                          :text-inside="true"
                          :stroke-width="18"
                          :status="getContributionStatus(report.progress_contribution)"
                          style="width: 200px"
                        />
                        <span class="contribution-text">
                          {{ report.progress_contribution }}%
                        </span>
                      </div>
                    </div>
                  </div>

                  <div class="report-footer">
                    <div class="report-actions">
                      <el-button
                        size="small"
                        type="primary"
                        @click="viewReportDetail(report)"
                      >
                        查看详情
                      </el-button>
                      <el-button
                        v-if="report.has_cde_evaluation"
                        size="small"
                        type="warning"
                        @click="viewEvaluation(report)"
                      >
                        查看评价
                      </el-button>
                    </div>
                    <div class="report-time">
                      <el-icon><Clock /></el-icon>
                      {{ formatDate(report.create_time) }}
                    </div>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>
        </el-card>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <div class="footer-info">
          <span class="total-info">
            总计 {{ relatedReports.length }} 条关联日报
            <span v-if="cdeCount > 0">，其中 {{ cdeCount }} 条有CDE评价</span>
          </span>
        </div>
        <div class="footer-actions">
          <el-button @click="$emit('close')">关闭</el-button>
          <el-button type="primary" @click="exportReports">
            <el-icon><Download /></el-icon>
            导出日报
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  List,
  Document,
  User,
  Star,
  Clock,
  Download
} from '@element-plus/icons-vue'
import { projectTrackingApi, type TaskReportLink, type TaskTracking } from '@/api/projectTracking'

// Props
interface Props {
  modelValue: boolean
  taskId?: string
  taskInfo?: TaskTracking
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'close': []
}>()

// 响应式数据
const loading = ref(false)
const relatedReports = ref<TaskReportLink[]>([])
const reportFilter = ref('')

// 计算属性
const filteredReports = computed(() => {
  if (!reportFilter.value) return relatedReports.value
  
  if (reportFilter.value === 'cde') {
    return relatedReports.value.filter(report => report.has_cde_evaluation)
  } else if (reportFilter.value === 'no_cde') {
    return relatedReports.value.filter(report => !report.has_cde_evaluation)
  }
  
  return relatedReports.value
})

const cdeCount = computed(() => 
  relatedReports.value.filter(report => report.has_cde_evaluation).length
)

// 获取任务关联的日报
const fetchRelatedReports = async () => {
  if (!props.taskId) return
  
  loading.value = true
  try {
    const response = await projectTrackingApi.getTaskRelatedReports(props.taskId)
    
    if (response.data.success) {
      if (response.data.data && response.data.data.related_reports) {
        relatedReports.value = response.data.data.related_reports
      } else {
        relatedReports.value = []
      }
    } else {
      ElMessage.error(response.data.message || '获取关联日报失败')
      relatedReports.value = []
    }
  } catch (error) {
    console.error('获取任务关联日报失败:', error)
    ElMessage.error('获取关联日报失败')
    relatedReports.value = []
  } finally {
    loading.value = false
  }
}

// 查看报告详情
const viewReportDetail = (report: TaskReportLink) => {
  // 这里可以跳转到日报详情页或打开详情对话框
  ElMessage.info(`查看日报详情: ${report.id}`)
}

// 查看评价详情
const viewEvaluation = (report: TaskReportLink) => {
  // 这里可以打开评价详情对话框
  ElMessage.info(`查看评价详情: ${report.id}`)
}

// 导出日报
const exportReports = () => {
  ElMessage.info('导出日报功能开发中...')
}

// 格式化日期
const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取状态标签类型
const getStatusTagType = (status: string) => {
  switch (status) {
    case '已完成':
      return 'success'
    case '进行中':
      return 'primary'
    case '已暂停':
      return 'warning'
    case '未开始':
      return 'info'
    default:
      return ''
  }
}

// 获取进度状态
const getProgressStatus = (progress: number) => {
  if (progress >= 100) return 'success'
  if (progress >= 80) return ''
  if (progress >= 50) return 'warning'
  return 'exception'
}

// 获取贡献状态
const getContributionStatus = (contribution: number) => {
  if (contribution >= 50) return 'success'
  if (contribution >= 20) return ''
  if (contribution >= 10) return 'warning'
  return 'exception'
}

// 获取报告类型
const getReportType = (report: TaskReportLink) => {
  if (report.has_cde_evaluation) return 'warning'
  if (report.progress_contribution >= 50) return 'success'
  return 'primary'
}

// 获取报告大小
const getReportSize = (report: TaskReportLink) => {
  if (report.has_cde_evaluation) return 'large'
  return 'normal'
}

// 监听对话框状态
watch(() => props.modelValue, (newVal) => {
  if (newVal && props.taskId) {
    fetchRelatedReports()
  }
})

// 监听任务ID变化
watch(() => props.taskId, (newVal) => {
  if (newVal && props.modelValue) {
    fetchRelatedReports()
  }
})
</script>

<style scoped>
.task-report-viewer {
  min-height: 500px;
}

/* 加载状态 */
.loading-container {
  padding: 20px;
}

/* 任务信息 */
.task-info {
  margin-bottom: 24px;
}

.task-basic-card {
  border: none;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.task-descriptions {
  margin: 0;
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  min-width: 35px;
}

.delay-text {
  color: #f59e0b;
  font-weight: 600;
}

.normal-text {
  color: #6b7280;
}

.reports-badge {
  color: #3b82f6;
}

/* 报告部分 */
.reports-section {
  margin-top: 24px;
}

.reports-card {
  border: none;
  border-radius: 8px;
}

.reports-filter {
  display: flex;
  gap: 12px;
}

.no-reports {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.reports-timeline {
  margin-top: 20px;
}

.report-card {
  border: none;
  border-radius: 8px;
  margin-bottom: 16px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.reporter-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.reporter-name {
  font-weight: 600;
  color: #374151;
}

.report-meta {
  display: flex;
  gap: 8px;
  align-items: center;
}

.cde-tag {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 报告内容 */
.report-content {
  margin-bottom: 16px;
}

.work-content {
  margin-bottom: 16px;
}

.content-title {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.content-text {
  margin: 0;
  color: #6b7280;
  line-height: 1.6;
}

/* CDE评价 */
.cde-evaluation {
  margin: 16px 0;
  padding: 16px;
  background: #fef3cd;
  border-radius: 8px;
  border: 1px solid #fcd34d;
}

.evaluation-content {
  margin-top: 12px;
}

.evaluation-score {
  margin-bottom: 12px;
}

.score-label {
  display: inline-block;
  margin-right: 8px;
  font-weight: 600;
  color: #92400e;
}

.evaluation-text {
  margin-top: 12px;
}

.evaluation-title {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #92400e;
}

.evaluation-desc {
  margin: 0;
  color: #78350f;
  line-height: 1.6;
  font-style: italic;
}

/* 进度贡献 */
.progress-contribution {
  margin-top: 16px;
}

.contribution-title {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.contribution-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.contribution-text {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  min-width: 40px;
}

/* 报告底部 */
.report-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f3f4f6;
}

.report-actions {
  display: flex;
  gap: 8px;
}

.report-time {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #9ca3af;
}

/* 对话框底部 */
.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-info {
  color: #6b7280;
  font-size: 14px;
}

.total-info {
  font-weight: 600;
}

.footer-actions {
  display: flex;
  gap: 12px;
}

/* 响应式 */
@media (max-width: 768px) {
  .task-report-viewer {
    padding: 0;
  }
  
  .report-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .report-meta {
    flex-wrap: wrap;
  }
  
  .report-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .dialog-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .progress-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .contribution-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
