<template>
  <div class="daily-report-container">
    <!-- 日报内容 -->
    <div class="daily-report-content">
      <div class="report-content">
        <!-- 标题 -->
        <div class="report-header">
          <div class="report-title-section">
            <h1 class="report-title">日报详情页</h1>
            <div class="header-buttons">
              <el-button @click="goBack" type="primary" size="default" class="header-back-btn">
                <el-icon><ArrowLeft /></el-icon>
                返回
              </el-button>
            </div>
          </div>
        </div>

        <!-- 日报时间 -->
        <div class="report-header-section">
          <div class="date-section">
            <div class="date-item">
              <label class="date-label">日报时间：</label>
              <span class="date-value">{{ formatDate(report.report_date) }}</span>
            </div>
            <div class="date-item">
              <label class="date-label">状态：</label>
              <el-tag :type="getStatusTagType(report.status)" size="small">
                {{ report.status }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 日报内容 -->
        <div class="daily-report-form">
          
          <!-- 一、今日工作目标 -->
          <div class="form-section">
            <div class="section-header">
              <div class="section-number">一</div>
              <div class="section-title">今日工作目标</div>
            </div>
            <div class="section-content">
              <div class="content-display">
                {{ report.work_target || '未填写' }}
              </div>
            </div>
          </div>

          <!-- 二、近期重点工作跟踪推进情况 -->
          <div class="form-section">
            <div class="section-header">
              <div class="section-number">二</div>
              <div class="section-title">近期重点工作跟踪推进情况</div>
            </div>
            <div class="section-content">
              <div class="content-display">
                {{ report.key_work_tracking || '未填写' }}
              </div>
            </div>
          </div>

          <!-- 三、主要工作事项 -->
          <div class="form-section">
            <div class="section-header">
              <div class="section-number">三</div>
              <div class="section-title">主要工作事项</div>
            </div>
            <div class="section-content">
              <!-- 任务统计信息 -->
              <div class="task-stats-display" v-if="workItems && workItems.length > 0">
                <div class="task-stats-item">
                  <i class="el-icon-document"></i>
                  <span>总任务数：</span>
                  <span class="task-stats-number">{{ workItems.length }}</span>
                </div>
                <div class="task-stats-item">
                  <i class="el-icon-time"></i>
                  <span>总工时：</span>
                  <span class="task-stats-number">{{ totalWorkHours }} 小时</span>
                </div>
              </div>

              <!-- 工作项目列表 -->
              <div class="work-items-display" v-if="workItems && workItems.length > 0">
                <div 
                  v-for="(item, index) in workItems" 
                  :key="index" 
                  class="work-item-card-display"
                >
                  <!-- 卡片头部 -->
                  <div class="card-header">
                    <div class="card-number">
                      <span class="number">{{ index + 1 }}</span>
                      <span class="text">工作事项</span>
                    </div>
                  </div>

                  <!-- 卡片内容 -->
                  <div class="card-content">
                    <!-- 主要工作事项 -->
                    <div class="form-row">
                      <label class="form-label">
                        <i class="el-icon-edit-outline"></i>
                        {{ (index + 1) }}.1 主要工作事项
                      </label>
                      <div class="form-field">
                        <div class="content-display">
                          {{ item.content || '未填写' }}
                        </div>
                      </div>
                    </div>

                    <!-- 关联任务 -->
                    <div class="form-row">
                      <label class="form-label">
                        <i class="el-icon-link"></i>
                        {{ (index + 1) }}.2 关联任务
                      </label>
                      <div class="form-field">
                        <div class="content-display">
                          {{ item.relatedTask || '无关联任务' }}
                        </div>
                      </div>
                    </div>

                    <!-- 工作时间 -->
                    <div class="form-row">
                      <label class="form-label">
                        <i class="el-icon-time"></i>
                        {{ (index + 1) }}.3 工作时间
                      </label>
                      <div class="form-field">
                        <div class="content-display">
                          {{ item.startTime || '未设置' }} 至 {{ item.endTime || '未设置' }}
                        </div>
                      </div>
                    </div>

                    <!-- 完成情况结果 -->
                    <div class="form-row">
                      <label class="form-label">
                        <i class="el-icon-check-circle"></i>
                        {{ (index + 1) }}.4 完成情况结果
                      </label>
                      <div class="form-field">
                        <div class="content-display">
                          {{ item.result || '未填写' }}
                        </div>
                      </div>
                    </div>

                    <!-- 追溯差距根源制定正确措施 -->
                    <div class="form-row">
                      <label class="form-label">
                        <i class="el-icon-setting"></i>
                        {{ (index + 1) }}.5 追溯差距根源制定正确措施
                      </label>
                      <div class="form-field">
                        <div class="content-display">
                          {{ item.measures || '未填写' }}
                        </div>
                      </div>
                    </div>

                    <!-- 自我评价 -->
                    <div class="form-row">
                      <label class="form-label">
                        <i class="el-icon-star-on"></i>
                        {{ (index + 1) }}.6 自我评价
                      </label>
                      <div class="form-field">
                        <div class="content-display">
                          <div class="evaluation-display">
                            <el-tag 
                              :type="getWorkEvaluationType(item.evaluation)"
                              size="default"
                              class="prominent-self-evaluation"
                            >
                              <span class="grade-letter">{{ item.evaluation || '未评价' }}</span>
                            </el-tag>
                            <span class="evaluation-description prominent-desc">
                              {{ getWorkEvaluationText(item.evaluation) }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-work-items">
                <i class="el-icon-document"></i>
                <p>暂无工作事项</p>
              </div>

              <!-- 评价说明 -->
              <div class="evaluation-description">
                <p><strong>评价说明：</strong></p>
                <p>A - 超目标达成；B - 按目标达成；C - 达成目标80%；D - 达成目标50%-80%；E - 小于目标50%</p>
              </div>
            </div>
          </div>

          <!-- 四、明日计划 -->
          <div class="form-section">
            <div class="section-header">
              <div class="section-number">四</div>
              <div class="section-title">明日计划</div>
            </div>
            <div class="section-content">
              <div class="content-display">
                {{ report.tomorrow_plan || '未填写' }}
              </div>
            </div>
          </div>

          <!-- 五、附件列表 -->
          <div class="form-section attachments-section">
            <div class="section-header">
              <div class="section-number">五</div>
              <div class="section-title">附件列表</div>
            </div>
            <div class="section-content">
              <div v-if="attachments && attachments.length > 0" class="attachments-page-list">
                <div 
                  v-for="(attachment, index) in attachments" 
                  :key="index" 
                  class="attachment-item"
                >
                  <div class="attachment-info">
                    <div class="attachment-name">
                      <el-icon><Document /></el-icon>
                      {{ attachment.file_name || attachment.filename }}
                    </div>
                    <div class="attachment-details">
                      <span class="attachment-size">
                        {{ attachment.file_size ? (attachment.file_size / 1024 / 1024).toFixed(2) + ' MB' : '未知大小' }}
                      </span>
                      <span class="attachment-date">
                        {{ attachment.uploaded_at ? new Date(attachment.uploaded_at).toLocaleString('zh-CN') : '未知时间' }}
                      </span>
                    </div>
                  </div>
                  <div class="attachment-actions">
                    <el-button 
                      v-if="isImagePreview(attachment)"
                      type="primary" 
                      size="small"
                      @click="previewAttachment(attachment)"
                    >
                      <el-icon><View /></el-icon>
                      预览
                    </el-button>
                    <el-button 
                      type="primary" 
                      size="small"
                      @click="downloadAttachment(attachment)"
                    >
                      <el-icon><Download /></el-icon>
                      下载
                    </el-button>
                  </div>
                </div>
              </div>
              <div v-else class="no-attachments">
                <el-icon color="#909399" size="48"><Document /></el-icon>
                <p>暂无附件</p>
              </div>
            </div>
          </div>

          <!-- 六、上级评价 -->
          <div class="form-section">
            <div class="section-header">
              <div class="section-number">六</div>
              <div class="section-title">上级评价</div>
            </div>
            <div class="section-content">
              <div class="content-display" v-if="report.supervisor_score && report.supervisor_score !== 0 && report.supervisor_name">
                <div class="supervisor-evaluation">
                  <div class="evaluation-header">
                    <div class="evaluator-info">
                      <span class="evaluator-name">
                        <el-icon><UserFilled /></el-icon>
                        {{ report.supervisor_name }}
                      </span>
                      <el-tag type="primary" size="small" class="supervisor-badge">
                        直属领导
                      </el-tag>
                    </div>
                  </div>
                  <!-- 评价等级卡片 -->
                  <div class="evaluation-card">
                    <div class="card-header">
                      <label class="card-label">评价等级</label>
                    </div>
                    <div class="card-content">
                      <el-tag 
                        :type="getScoreType(convertScoreToGrade(report.supervisor_score))"
                        size="large"
                        class="prominent-grade-tag"
                      >
                        <span class="grade-letter">{{ convertScoreToGrade(report.supervisor_score) }}</span>
                      </el-tag>
                      <span class="score-description prominent-desc">{{ getScoreDescription(convertScoreToGrade(report.supervisor_score)) }}</span>
                    </div>
                  </div>
                  
                  <!-- 评价等级说明 -->
                  <div class="evaluation-grades-info">
                    <label class="grades-title">评价标准：</label>
                    <div class="grades-list">
                      <div class="grade-item" :class="{ 'current-grade': convertScoreToGrade(report.supervisor_score) === 'A' }">
                        <span class="grade-tag grade-a">A</span>
                        <span class="grade-desc">超目标达成</span>
                      </div>
                      <div class="grade-item" :class="{ 'current-grade': convertScoreToGrade(report.supervisor_score) === 'B' }">
                        <span class="grade-tag grade-b">B</span>
                        <span class="grade-desc">按目标达成</span>
                      </div>
                      <div class="grade-item" :class="{ 'current-grade': convertScoreToGrade(report.supervisor_score) === 'C' }">
                        <span class="grade-tag grade-c">C</span>
                        <span class="grade-desc">达成目标80%</span>
                      </div>
                      <div class="grade-item" :class="{ 'current-grade': convertScoreToGrade(report.supervisor_score) === 'D' }">
                        <span class="grade-tag grade-d">D</span>
                        <span class="grade-desc">达成目标50%-80%</span>
                      </div>
                      <div class="grade-item" :class="{ 'current-grade': convertScoreToGrade(report.supervisor_score) === 'E' }">
                        <span class="grade-tag grade-e">E</span>
                        <span class="grade-desc">小于目标50%</span>
                      </div>
                    </div>
                  </div>
                  <!-- 评价说明卡片 -->
                  <div class="evaluation-card" v-if="report.supervisor_comment">
                    <div class="card-header">
                      <label class="card-label">评价说明</label>
                    </div>
                    <div class="card-content">
                      <div class="comment-text">{{ report.supervisor_comment }}</div>
                    </div>
                  </div>
                  
                  <!-- 评价时间卡片 -->
                  <div class="evaluation-card">
                    <div class="card-header">
                      <label class="card-label">评价时间</label>
                    </div>
                    <div class="card-content">
                      <span class="time-text">{{ formatDateTime(report.evaluated_at) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="content-display">
                <div class="empty-evaluation">
                  <i class="el-icon-document"></i>
                  <p>暂无上级评价</p>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>

    <!-- 提交确认对话框 -->
    <el-dialog
      v-model="submitDialogVisible"
      title="提交确认"
      width="500px"
    >
      <div class="submit-confirm">
        <el-icon color="#e6a23c" size="24"><QuestionFilled /></el-icon>
        <div class="confirm-text">
          <p>确定要提交这份日报吗？</p>
          <p class="warning-text">提交后将无法修改，只能查看。</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="submitDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="confirmSubmit"
          :loading="submitLoading"
        >
          确定提交
        </el-button>
      </template>
    </el-dialog>

    <!-- 评价对话框 -->
    <el-dialog
      v-model="evaluationDialogVisible"
      title="评价日报"
      width="600px"
      @close="resetEvaluationForm"
    >
      <el-form 
        ref="evaluationForm" 
        :model="evaluationFormData" 
        label-width="100px"
      >
        <el-form-item label="日报日期">
          <span class="evaluation-info">{{ formatDate(report.report_date) }} - {{ report.employee_name }}</span>
        </el-form-item>
        
        <el-form-item label="工作表现" required>
          <div class="score-section">
            <label>评价等级：</label>
            <el-radio-group v-model="evaluationFormData.supervisor_score">
              <el-radio-button label="A" class="grade-a">优秀</el-radio-button>
              <el-radio-button label="B" class="grade-b">良好</el-radio-button>
              <el-radio-button label="C" class="grade-c">一般</el-radio-button>
              <el-radio-button label="D" class="grade-d">较差</el-radio-button>
              <el-radio-button label="E" class="grade-e">很差</el-radio-button>
            </el-radio-group>
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
          <el-button @click="evaluationDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="submitEvaluation"
            :loading="submitLoading"
            :disabled="!evaluationFormData.supervisor_score"
          >
            提交评价
          </el-button>
        </div>
      </template>
    </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  ArrowLeft, Edit, Upload, InfoFilled, Document, Star, Clock, 
  QuestionFilled, UserFilled, Download, View 
} from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import {
  getDailyReport,
  submitDailyReport,
  getDailyReportAttachments,
  downloadDailyReportAttachment,
  type DailyReport
} from '../../api/dailyReport'

// 导入评价相关API
import { 
  evaluateDailyReport
} from '../../api/dailyReportEvaluation'

const router = useRouter()
const route = useRoute()

// 状态管理
const report = ref<DailyReport>({} as DailyReport)
const workItems = ref<any[]>([])
const loading = ref(false)
const submitDialogVisible = ref(false)
const submitLoading = ref(false)
const reportId = ref<number>(0)

// 附件相关状态
const attachments = ref<any[]>([])

// 评价相关状态
const evaluationDialogVisible = ref(false)
const evaluationForm = ref()
const evaluationFormData = ref({
  supervisor_score: '',
  supervisor_comment: ''
})

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return dateStr
}

const formatDateTime = (dateTime: string) => {
  if (!dateTime) return '-'
  return new Date(dateTime).toLocaleString('zh-CN')
}

// 获取标签类型
const getStatusTagType = (status: string) => {
  const typeMap: Record<string, any> = {
    '待提交': 'info',
    '已提交': 'warning',
    '待评价': 'primary',
    '已评价': 'success'
  }
  return typeMap[status] || 'default'
}



// 数字评分转换为字母评分
const convertScoreToGrade = (score: number | string): string => {
  // 如果已经是字母，直接返回
  if (typeof score === 'string') {
    return score
  }
  
  // 数字转换为字母
  const intToGrade = {
    5: 'A',  // 优秀
    4: 'B',  // 良好
    3: 'C',  // 一般
    2: 'D',  // 较差
    1: 'E'   // 很差
  }
  
  return intToGrade[score] || 'E' // 默认为E
}

// 获取评分类型
const getScoreType = (score: string | number) => {
  const grade = convertScoreToGrade(score)
  switch (grade) {
    case 'A': return 'success'
    case 'B': return 'primary'
    case 'C': return 'warning'
    case 'D': return 'danger'
    case 'E': return 'info'
    default: return 'default'
  }
}

// 获取评分描述
const getScoreDescription = (score: string | number) => {
  const grade = convertScoreToGrade(score)
  switch (grade) {
    case 'A': return 'A - 超目标达成'
    case 'B': return 'B - 按目标达成'
    case 'C': return 'C - 达成目标80%'
    case 'D': return 'D - 达成目标50%-80%'
    case 'E': return 'E - 小于目标50%'
    default: return ''
  }
}

// 获取工作评价类型
const getWorkEvaluationType = (evaluation: string) => {
  switch (evaluation) {
    case 'A': return 'success'
    case 'B': return 'warning' 
    case 'C': return 'danger'
    default: return 'info'
  }
}

// 获取工作评价文本
const getWorkEvaluationText = (evaluation: string) => {
  switch (evaluation) {
    case 'A': return 'A - 超目标达成'
    case 'B': return 'B - 按目标达成'
    case 'C': return 'C - 达成目标80%'
    case 'D': return 'D - 达成目标50%-80%'
    case 'E': return 'E - 小于目标50%'
    default: return '未评价'
  }
}

// 计算总工时
const totalWorkHours = computed(() => {
  if (!workItems.value || workItems.value.length === 0) return 0
  
  let total = 0
  for (const item of workItems.value) {
    if (item.startTime && item.endTime) {
      try {
        const start = new Date(`2000-01-01 ${item.startTime}`)
        const end = new Date(`2000-01-01 ${item.endTime}`)
        const hours = (end.getTime() - start.getTime()) / (1000 * 60 * 60)
        if (hours > 0) {
          total += hours
        }
      } catch (error) {
        console.warn('时间解析错误:', item.startTime, item.endTime)
      }
    }
  }
  return Math.round(total * 100) / 100 // 保留两位小数
})

const getProgressTagType = (status: string) => {
  const typeMap: Record<string, any> = {
    '正常': 'success',
    '延期': 'warning',
    '超前': 'primary',
    '暂停': 'info'
  }
  return typeMap[status] || 'default'
}

// 加载日报详情
const loadReport = async () => {
  if (!reportId.value) return
  
  loading.value = true
  try {
    const response = await getDailyReport(reportId.value)
    report.value = response
    
    // 处理工作项目数据
    if (response.work_items && Array.isArray(response.work_items)) {
      workItems.value = response.work_items.map(item => ({
        content: item.work_content || '',
        relatedTask: item.task_name ? `${item.project_name} - ${item.task_name}` : '',
        startTime: item.start_time || '',
        endTime: item.end_time || '',
        result: item.result || '',
        measures: item.measures || '',
        evaluation: item.evaluation || ''
      }))
    } else {
      workItems.value = []
    }
    
    // 加载附件数据
    try {
      const attachmentResponse = await getDailyReportAttachments(reportId.value)
      attachments.value = attachmentResponse.data || attachmentResponse || []
    } catch (attachmentError) {
      console.warn('获取附件失败:', attachmentError)
      attachments.value = []
    }
  } catch (error) {
    console.error('获取日报详情失败:', error)
    ElMessage.error('获取日报详情失败')
  } finally {
    loading.value = false
  }
}

// 事件处理
const goBack = () => {
  console.log('🔄 开始返回到日报列表...')
  
  // 使用window.location.href强制页面刷新，这是最可靠的方法
  const timestamp = Date.now()
  const targetPath = `/daily-report?t=${timestamp}`
  
  console.log('🔄 强制页面刷新到:', targetPath)
  
  // 延迟一下确保日志输出
  setTimeout(() => {
    window.location.href = targetPath
  }, 100)
}

const handleEdit = () => {
  router.push(`/daily-report/${reportId.value}/edit`)
}

const handleSubmit = () => {
  submitDialogVisible.value = true
}

// 判断附件是否支持图片预览
const isImagePreview = (attachment: any) => {
  if (!attachment || !attachment.file_type) return false
  const fileType = attachment.file_type.toLowerCase()
  return fileType.includes('image') && 
         (fileType.includes('jpeg') || fileType.includes('jpg') || 
          fileType.includes('png') || fileType.includes('gif') || 
          fileType.includes('webp') || fileType.includes('bmp'))
}

// 预览附件
const previewAttachment = (attachment: any) => {
  if (isImagePreview(attachment)) {
    // 跳转到附件预览页面，使用正确的路由路径
    router.push(`/daily-report/attachment/preview/${attachment.id}`)
  } else {
    ElMessage.warning('该文件格式不支持预览')
  }
}

// 下载附件
const downloadAttachment = async (attachment: any) => {
  try {
    const response = await downloadDailyReportAttachment(attachment.id)
    
    // 创建下载链接
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = attachment.file_name || attachment.filename || 'attachment'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('下载开始')
  } catch (error) {
    console.error('下载附件失败:', error)
    ElMessage.error('下载附件失败')
  }
}



const resetEvaluationForm = () => {
  evaluationFormData.value = {
    supervisor_score: '',
    supervisor_comment: ''
  }
}

const submitEvaluation = async () => {
  if (!evaluationFormData.value.supervisor_score) {
    ElMessage.error('请选择评价等级')
    return
  }
  
  submitLoading.value = true
  try {
    await evaluateDailyReport({
      report_id: reportId.value,
      supervisor_score: evaluationFormData.value.supervisor_score,
      supervisor_comment: evaluationFormData.value.supervisor_comment
    })
    
    ElMessage.success('评价提交成功')
    evaluationDialogVisible.value = false
    loadReport() // 重新加载数据
  } catch (error) {
    console.error('提交评价失败:', error)
    ElMessage.error('提交评价失败')
  } finally {
    submitLoading.value = false
  }
}

const confirmSubmit = async () => {
  submitLoading.value = true
  try {
    await submitDailyReport(reportId.value)
    ElMessage.success('提交成功')
    submitDialogVisible.value = false
    loadReport()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败')
  } finally {
    submitLoading.value = false
  }
}

// 初始化
onMounted(() => {
  reportId.value = parseInt(route.params.id as string)
  loadReport()
})
</script>

<style scoped>
.daily-report-container {
  padding: 20px;
  background: white;
  min-height: 100vh;
  width: 100%;
  overflow-x: auto;
}

.page-header {
  margin-bottom: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-actions {
  display: flex;
  justify-content: flex-start;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.report-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-header {
  background: #f8f9fa;
  padding: 16px 20px;
  border-bottom: 1px solid #e9ecef;
}

.section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #000000;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-content {
  padding: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  font-size: 14px;
  color: #000000;
  font-weight: 500;
}

.info-value {
  font-size: 16px;
  color: #303133;
}

.content-section {
  margin-bottom: 24px;
}

.content-section:last-child {
  margin-bottom: 0;
}

.content-title {
  font-size: 14px;
  font-weight: 600;
  color: #000000;
  margin-bottom: 8px;
}

.content-text {
  font-size: 16px;
  color: #000000;
  line-height: 1.6;
  background: #f8f9fa;
  padding: 16px;
  border-radius: 6px;
  min-height: 60px;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-number {
  font-size: 16px;
  font-weight: 600;
  color: #409EFF;
}

.timeline {
  position: relative;
  padding-left: 40px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 15px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e9ecef;
}

.timeline-item {
  position: relative;
  margin-bottom: 24px;
}

.timeline-item:last-child {
  margin-bottom: 0;
}

.timeline-dot {
  position: absolute;
  left: -31px;
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #c0c4cc;
  border: 2px solid white;
  box-shadow: 0 0 0 1px #c0c4cc;
}

.timeline-dot.active {
  background: #409EFF;
  box-shadow: 0 0 0 1px #409EFF;
}

.timeline-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.timeline-title {
  font-size: 16px;
  font-weight: 600;
  color: #000000;
}

.timeline-time {
  font-size: 14px;
  color: #000000;
}

.submit-confirm {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.confirm-text {
  flex: 1;
}

.warning-text {
  color: #e6a23c;
  font-weight: 500;
  margin: 8px 0 0 0;
}

.score-description {
  margin-left: 8px;
  color: #909399;
  font-size: 12px;
}

.task-stats-display {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.task-stats-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #000000;
  font-size: 14px;
}

.task-stats-item i {
  color: #409eff;
}

.task-stats-number {
  font-weight: 600;
  color: #000000;
}

.evaluation-display {
  display: flex;
  align-items: center;
  gap: 10px;
}

.evaluation-description {
  color: #909399;
  font-size: 12px;
  margin-left: 8px;
}

.evaluation-description {
  margin-top: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.evaluation-description p {
  margin: 5px 0;
  color: #000000;
  font-size: 13px;
  line-height: 1.5;
}

.supervisor-evaluation {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 上级主管评价样式 */
.evaluation-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.evaluator-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: nowrap;
  min-width: fit-content;
}

.evaluator-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: #303133;
  font-size: 15px;
  white-space: nowrap;
}

.evaluator-name .el-icon {
  font-size: 14px;
  color: #409EFF;
}

.supervisor-badge {
  display: inline-flex;
  align-items: center;
  background-color: #409EFF;
  color: white;
  border: none;
  font-size: 11px;
  font-weight: 500;
  padding: 4px 8px;
  height: 20px;
  line-height: 1;
  border-radius: 4px;
  white-space: nowrap;
}

.grade-display {
  display: flex;
  align-items: center;
  gap: 12px;
}

.prominent-grade-tag {
  transform: scale(1.3);
  font-size: 18px !important;
  font-weight: bold;
  padding: 8px 16px !important;
  border-radius: 8px !important;
}

.grade-letter {
  font-weight: bold;
}

.prominent-desc {
  font-size: 16px !important;
  font-weight: 600 !important;
  color: #303133 !important;
}

/* 第三部分自我评价样式 */
.prominent-self-evaluation {
  transform: scale(1.2);
  font-size: 16px !important;
  font-weight: bold;
  padding: 6px 12px !important;
  border-radius: 6px !important;
}

.evaluation-grade,
.evaluation-comment,
.evaluation-time {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.evaluation-label {
  font-weight: 500;
  color: #000000;
  min-width: 80px;
  margin-top: 2px;
}

.comment-text {
  color: #000000;
  line-height: 1.6;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
  flex: 1;
}

.time-text {
  color: #000000;
  font-weight: 500;
}

/* 评价等级说明样式 */
.evaluation-grades-info {
  margin: 16px 0;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

/* 上级评价卡片样式 */
.evaluation-card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 0;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
}

.evaluation-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
  padding: 12px 16px;
  border-radius: 8px 8px 0 0;
}

.card-label {
  font-weight: 600;
  color: #606266;
  font-size: 14px;
  margin: 0;
}

.card-content {
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.card-content .comment-text {
  color: #303133;
  line-height: 1.6;
  font-size: 14px;
  margin: 0;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 0;
  flex: 1;
}

.card-content .time-text {
  color: #409eff;
  font-weight: 500;
  font-size: 14px;
}

.grades-title {
  display: block;
  font-weight: 600;
  color: #606266;
  margin-bottom: 12px;
  font-size: 14px;
}

.grades-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.grade-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #ffffff;
  border-radius: 6px;
  border: 1px solid #dcdfe6;
  transition: all 0.3s ease;
}

.grade-item.current-grade {
  background: #f0f9ff;
  border-color: #409eff;
  box-shadow: 0 0 0 1px #409eff;
}

.grade-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.grade-a { background: #67c23a; }
.grade-b { background: #409eff; }
.grade-c { background: #e6a23c; }
.grade-d { background: #f56c6c; }
.grade-e { background: #909399; }

.grade-desc {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.grade-item.current-grade .grade-desc {
  color: #409eff;
  font-weight: 600;
}

.evaluation-info {
  font-weight: 500;
  color: #409eff;
}

.score-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-section label {
  font-weight: 500;
  color: #000000;
  min-width: 80px;
}

.grade-a {
  background-color: #f0f9ff;
  border-color: #c6e2ff;
  color: #409eff;
}

.grade-b {
  background-color: #f0f9ff;
  border-color: #b3d8ff;
  color: #337ecc;
}

.grade-c {
  background-color: #fdf6ec;
  border-color: #f5dab1;
  color: #e6a23c;
}

.grade-d {
  background-color: #fef0f0;
  border-color: #fbc4c4;
  color: #f56c6c;
}

.grade-e {
  background-color: #f4f4f5;
  border-color: #c0c4cc;
  color: #909399;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 新的详情页面样式 */
.daily-report-content {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.report-content {
  padding: 0;
}

.report-header {
  padding: 30px 40px 20px;
  background: white;
  color: #000000;
  text-align: center;
}

.report-title-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.report-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.header-back-btn {
  flex-shrink: 0;
}

.header-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-attachments-btn {
  flex-shrink: 0;
}

.report-header-section {
  padding: 20px 40px;
  background: #fafbfc;
  border-bottom: 1px solid #e8eaed;
}

.date-section {
  display: flex;
  gap: 30px;
  align-items: center;
}

.date-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.date-value {
  color: #000000;
  font-weight: 500;
}

.daily-report-form {
  padding: 30px 40px;
}

.form-section {
  margin-bottom: 30px;
  background: white;
  border: 1px solid #e8eaed;
  border-radius: 8px;
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  padding: 20px 25px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #e8eaed;
}

.section-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
  margin-right: 15px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.section-content {
  padding: 25px;
}

.content-display {
  padding: 15px;
  background: #fafbfc;
  border: 1px solid #e8eaed;
  border-radius: 6px;
  color: #000000;
  line-height: 1.6;
  min-height: 60px;
  white-space: pre-wrap;
  word-break: break-word;
}

.work-items-display {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.work-item-card-display {
  background: white;
  border: 1px solid #e8eaed;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.card-header {
  padding: 15px 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #e8eaed;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-number {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-number .number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #667eea;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.card-number .text {
  font-weight: 500;
  color: #606266;
}

.card-content {
  padding: 20px;
}

.form-row {
  margin-bottom: 15px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
  font-size: 14px;
}

.form-field {
  padding-left: 24px;
}

.empty-work-items {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.empty-work-items i {
  font-size: 48px;
  margin-bottom: 16px;
  color: #dcdfe6;
}

.empty-evaluation {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.empty-evaluation i {
  font-size: 48px;
  margin-bottom: 16px;
  color: #dcdfe6;
}

.empty-evaluation p {
  font-size: 16px;
  color: #909399;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  font-weight: 500;
  color: #606266;
  font-size: 14px;
}

.info-value {
  color: #000000;
  line-height: 1.5;
}

.score-description {
  margin-left: 8px;
  color: #909399;
  font-size: 12px;
}

/* 附件页面内显示样式 */
.attachments-page-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.attachment-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border: 1px solid #e8eaed;
  border-radius: 8px;
  background: white;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.attachment-item:hover {
  background: #f8f9fa;
  border-color: #409EFF;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.1);
}

.attachment-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-name {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
  color: #303133;
  font-size: 15px;
}

.attachment-name .el-icon {
  color: #409EFF;
  font-size: 18px;
}

.attachment-details {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
  color: #909399;
}

.attachment-size {
  background: #f0f9ff;
  color: #409EFF;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 500;
  font-size: 12px;
}

.attachment-date {
  color: #909399;
}

.attachment-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 页面内无附件样式 */
.attachments-section .no-attachments {
  text-align: center;
  padding: 60px 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 2px dashed #e8eaed;
  color: #909399;
}

.attachments-section .no-attachments i {
  margin-bottom: 16px;
  opacity: 0.6;
  font-size: 48px;
}

.attachments-section .no-attachments p {
  font-size: 16px;
  margin: 0;
  color: #c0c4cc;
  font-weight: 500;
}
</style>