<template>
  <div class="daily-report-container">
    <!-- 日报内容 -->
    <div class="daily-report-content">
      <div class="report-content">
        <!-- 标题 -->
        <div class="report-header">
          <div class="report-title-section">
            <h1 class="report-title">{{ isViewMode ? '日报查看详情' : '日报评价详情' }}</h1>
            <el-button @click="goBack" type="primary" size="default" class="header-back-btn">
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
          </div>
        </div>

        <!-- 日报时间 -->
        <div class="report-header-section">
          <div class="date-section">
            <div class="date-item">
              <label class="date-label">日报日期：</label>
              <span class="date-value">{{ reportData.report_date }}</span>
            </div>
            <div class="date-item">
              <label class="date-label">员工姓名：</label>
              <span class="date-value">{{ reportData.employee_name }}</span>
            </div>
            <div class="date-item">
              <label class="date-label">部门：</label>
              <span class="date-value">{{ reportData.department }}</span>
            </div>
            <div class="date-item">
              <label class="date-label">职位：</label>
              <span class="date-value">{{ reportData.position }}</span>
            </div>
            <div class="date-item">
              <label class="date-label">状态：</label>
              <el-tag 
                :type="getStatusTagType(reportData.status)" 
                size="small"
                effect="plain"
              >
                {{ reportData.status }}
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
                {{ reportData.work_target || '未填写' }}
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
                {{ reportData.key_work_tracking || '未填写' }}
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
              <div class="task-stats-display" v-if="reportData.work_items && reportData.work_items.length > 0">
                <div class="task-stats-item">
                  <i class="el-icon-document"></i>
                  <span>总任务数：</span>
                  <span class="task-stats-number">{{ reportData.work_items.length }}</span>
                </div>
                <div class="task-stats-item">
                  <i class="el-icon-time"></i>
                  <span>总工时：</span>
                  <span class="task-stats-number">{{ totalWorkHours }} 小时</span>
                </div>
              </div>

              <!-- 工作项目列表 -->
              <div class="work-items-display" v-if="reportData.work_items && reportData.work_items.length > 0">
                <div 
                  v-for="(item, index) in reportData.work_items" 
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
                        主要工作事项
                      </label>
                      <div class="form-field">
                        <div class="content-display">
                          {{ item.work_content || '未填写' }}
                        </div>
                      </div>
                    </div>

                    <!-- 工作时间 -->
                    <div class="form-row">
                      <label class="form-label">
                        <i class="el-icon-time"></i>
                        工作时间
                      </label>
                      <div class="form-field">
                        <div class="content-display">
                          {{ item.start_time || '未设置' }} 至 {{ item.end_time || '未设置' }}
                        </div>
                      </div>
                    </div>

                    <!-- 完成情况结果 -->
                    <div class="form-row">
                      <label class="form-label">
                        <i class="el-icon-check-circle"></i>
                        完成情况结果
                      </label>
                      <div class="form-field">
                        <div class="content-display">
                          {{ item.result || '未填写' }}
                        </div>
                      </div>
                    </div>

                    <!-- 工作评价 -->
                    <div class="form-row">
                      <label class="form-label">
                        <i class="el-icon-star-on"></i>
                        工作评价
                      </label>
                      <div class="form-field">
                        <div class="content-display">
                          <div class="work-evaluation-display">
                            <el-tag 
                              :type="getWorkEvaluationType(getDisplayScore(item.evaluation))"
                              size="large"
                              class="evaluation-grade-tag"
                            >
                              {{ getDisplayScore(item.evaluation) }}
                            </el-tag>
                            <span class="evaluation-grade-text">
                              {{ getEvaluationDescription(getDisplayScore(item.evaluation)) }}
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
            </div>
          </div>
 
          <!-- 四、明日目标及计划 -->
          <div class="form-section">
            <div class="section-header">
              <div class="section-number">四</div>
              <div class="section-title">明日目标及计划</div>
            </div>
            <div class="section-content">
              <div class="content-display">
                {{ reportData.tomorrow_plan || '未填写' }}
              </div>
            </div>
          </div>
 


          <!-- 五、附件列表 -->
          <div class="form-section">
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
              
              <div v-if="hasEvaluation" class="evaluation-display">
                <div class="evaluation-content">
                  <div class="evaluator-info">
                    <label>评价人：</label>
                    <span class="evaluator-name">{{ currentEvaluation.supervisor_name }}</span>
                    <el-tag size="small" type="primary" effect="plain">直属领导</el-tag>
                  </div>
                  <!-- 评价等级卡片 -->
                  <div class="evaluation-card">
                    <div class="card-header">
                      <label class="card-label">评价等级</label>
                    </div>
                    <div class="card-content">
                      <el-tag 
                        :type="getScoreType(getDisplayScore(currentEvaluation.supervisor_score))"
                        size="large"
                        class="score-tag"
                      >
                        {{ getDisplayScore(currentEvaluation.supervisor_score) }}
                      </el-tag>
                      <span class="score-description">{{ getScoreDescription(getDisplayScore(currentEvaluation.supervisor_score)) }}</span>
                    </div>
                  </div>
                  
                  <!-- 评价等级说明 -->
                  <div class="evaluation-grades-info">
                    <label class="grades-title">评价标准：</label>
                    <div class="grades-list">
                      <div class="grade-item" :class="{ 'current-grade': currentEvaluation.supervisor_score === 'A' }">
                        <span class="grade-tag grade-a">A</span>
                        <span class="grade-desc">超目标达成</span>
                      </div>
                      <div class="grade-item" :class="{ 'current-grade': currentEvaluation.supervisor_score === 'B' }">
                        <span class="grade-tag grade-b">B</span>
                        <span class="grade-desc">按目标达成</span>
                      </div>
                      <div class="grade-item" :class="{ 'current-grade': currentEvaluation.supervisor_score === 'C' }">
                        <span class="grade-tag grade-c">C</span>
                        <span class="grade-desc">达成目标80%</span>
                      </div>
                      <div class="grade-item" :class="{ 'current-grade': currentEvaluation.supervisor_score === 'D' }">
                        <span class="grade-tag grade-d">D</span>
                        <span class="grade-desc">达成目标50%-80%</span>
                      </div>
                      <div class="grade-item" :class="{ 'current-grade': currentEvaluation.supervisor_score === 'E' }">
                        <span class="grade-tag grade-e">E</span>
                        <span class="grade-desc">小于目标50%</span>
                      </div>
                    </div>
                  </div>
                  <!-- 评价说明卡片 -->
                  <div class="evaluation-card" v-if="currentEvaluation.supervisor_comment">
                    <div class="card-header">
                      <label class="card-label">评价说明</label>
                    </div>
                    <div class="card-content">
                      <div class="comment-content">{{ currentEvaluation.supervisor_comment }}</div>
                    </div>
                  </div>
                  
                  <!-- 评价时间卡片 -->
                  <div class="evaluation-card">
                    <div class="card-header">
                      <label class="card-label">评价时间</label>
                    </div>
                    <div class="card-content">
                      <span class="evaluation-time-text">{{ formatDateTime(currentEvaluation.evaluated_at) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 查看模式下：未评价时也显示查看状态 -->
              <div v-else-if="isViewMode" class="evaluation-view-mode">
                <div class="view-mode-content">
                  <el-empty description="暂无评价信息" :image-size="60">
                    <template #description>
                      <p>该日报暂无评价信息</p>
                    </template>
                  </el-empty>
                </div>
              </div>
              
              <!-- 评价模式下：显示评价表单 -->
              <div v-else class="evaluation-form">
                <div class="form-row">
                  <label class="form-label">
                    <i class="el-icon-star-on"></i>
                    评价等级
                  </label>
                  <div class="form-field">
                    <div class="modern-evaluation-group">
                      <div 
                        v-for="option in ['A', 'B', 'C', 'D', 'E']"
                        :key="option"
                        :class="['modern-evaluation-box', { active: evaluationFormData.supervisor_score === option }]"
                        @click="evaluationFormData.supervisor_score = option"
                      >
                        <span class="modern-letter">{{ option }}</span>
                        <span class="modern-description">{{ getEvaluationDescription(option) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="form-row">
                  <label class="form-label">
                    <i class="el-icon-document"></i>
                    评价说明
                  </label>
                  <div class="form-field">
                    <el-input 
                      v-model="evaluationFormData.supervisor_comment" 
                      type="textarea" 
                      :rows="4"
                      placeholder="请输入对员工工作的评价和建议"
                      maxlength="500"
                      show-word-limit
                    />
                  </div>
                </div>
                
                <div class="form-actions">
                  <el-button @click="resetForm">重置</el-button>
                  <el-button 
                    type="primary" 
                    @click="submitEvaluation"
                    :loading="submitting"
                    :disabled="!evaluationFormData.supervisor_score"
                  >
                    提交评价
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Document, View, Download } from '@element-plus/icons-vue'

// 导入API
import { 
  getReportDetail,
  evaluateDailyReport
} from '../../api/dailyReportEvaluation'
import { getDailyReportAttachments, downloadDailyReportAttachment } from '../../api/dailyReport'

interface WorkItem {
  work_content: string
  start_time: string
  end_time: string
  result: string
  evaluation: string
}

interface Evaluation {
  supervisor_score: string
  supervisor_comment: string
  supervisor_id: string
  supervisor_name: string
  evaluated_at: string
}

interface ReportData {
  id: number
  report_date: string
  employee_name: string
  department: string
  position: string
  work_target: string
  work_items: WorkItem[]
  evaluation: Evaluation | null
  status: string
}

const router = useRouter()
const route = useRoute()

// 状态管理
const loading = ref(false)
const submitting = ref(false)
const reportId = ref<number>(0)
const isViewMode = ref(false) // 查看模式标志

const reportData = ref<ReportData>({
  id: 0,
  report_date: '',
  employee_name: '',
  department: '',
  position: '',
  work_target: '',
  work_items: [],
  evaluation: null
})

const evaluationFormData = ref({
  supervisor_score: '',
  supervisor_comment: ''
})

const attachments = ref<any[]>([])

// 计算属性
const hasEvaluation = computed(() => {
  return reportData.value.evaluation && 
         reportData.value.evaluation.supervisor_score !== null && 
         reportData.value.evaluation.supervisor_score !== undefined &&
         reportData.value.evaluation.supervisor_score !== ''
})

const currentEvaluation = computed(() => {
  return reportData.value.evaluation
})

// 获取状态标签类型
const getStatusTagType = (status: string) => {
  const typeMap: Record<string, any> = {
    '待提交': 'info',
    '已提交': 'warning',
    '待评价': 'primary',
    '已评价': 'success'
  }
  return typeMap[status] || 'default'
}

// 方法定义
const loadReportData = async () => {
  loading.value = true
  try {
    console.log('加载日报评价数据...', reportId.value)
    
    // 获取日报评价数据
    const response = await getReportDetail(reportId.value)
    console.log('日报评价数据响应:', response)
    
    const data = response.data || response.value || response
    reportData.value = data
    
    // 如果已有评价，填充表单（用于查看）
    if (hasEvaluation.value) {
      evaluationFormData.value = {
        supervisor_score: currentEvaluation.value.supervisor_score,
        supervisor_comment: currentEvaluation.value.supervisor_comment
      }
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

const submitEvaluation = async () => {
  if (!evaluationFormData.value.supervisor_score) {
    ElMessage.warning('请选择评价等级')
    return
  }
  
  submitting.value = true
  try {
    await evaluateDailyReport({
      report_id: reportId.value,
      supervisor_score: evaluationFormData.value.supervisor_score,
      supervisor_comment: evaluationFormData.value.supervisor_comment
    })
    
    ElMessage.success('评价提交成功')
    
    // 重新加载数据以显示最新评价
    await loadReportData()
    
  } catch (error) {
    console.error('提交评价失败:', error)
    ElMessage.error('提交评价失败')
  } finally {
    submitting.value = false
  }
}


const resetForm = () => {
  evaluationFormData.value = {
    supervisor_score: '',
    supervisor_comment: ''
  }
}

const goBack = () => {
  router.go(-1)
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
    // 跳转到附件预览页面
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

const formatDateTime = (dateTime: string) => {
  if (!dateTime) return '-'
  return new Date(dateTime).toLocaleString('zh-CN')
}

const getScoreType = (score: string) => {
  switch (score) {
    case 'A': return 'success'
    case 'B': return 'primary'
    case 'C': return 'warning'
    case 'D': return 'danger'
    case 'E': return 'danger'
    default: return 'default'
  }
}

const getScoreDescription = (score: string) => {
  switch (score) {
    case 'A': return 'A - 超目标达成'
    case 'B': return 'B - 按目标达成'
    case 'C': return 'C - 达成目标80%'
    case 'D': return 'D - 达成目标50%-80%'
    case 'E': return 'E - 小于目标50%'
    default: return ''
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

// 获取评价显示值（支持多种格式）
const getDisplayScore = (score: any): string => {
  // 如果是null或undefined
  if (score === null || score === undefined) {
    return '未评价'
  }
  
  // 如果是字符串（工作项目评价）
  if (typeof score === 'string') {
    return score || '未评价'
  }
  
  // 如果是数字（日报评价）
  if (typeof score === 'number') {
    return convertScoreToGrade(score)
  }
  
  return '未评价'
}

const getEvaluationDescription = (option: string) => {
  switch (option) {
    case 'A': return '超目标达成'
    case 'B': return '按目标达成'
    case 'C': return '达成目标80%'
    case 'D': return '达成目标50%-80%'
    case 'E': return '小于目标50%'
    default: return ''
  }
}

const getWorkEvaluationType = (evaluation: string) => {
  switch (evaluation) {
    case 'A': return 'success'
    case 'B': return 'primary'
    case 'C': return 'warning'
    case 'D': return 'danger'
    case 'E': return 'danger'
    default: return 'default'
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

// 计算总工时
const totalWorkHours = computed(() => {
  if (!reportData.value.work_items || reportData.value.work_items.length === 0) {
    return 0
  }
  
  let totalHours = 0
  reportData.value.work_items.forEach(item => {
    // 这里可以添加工时计算逻辑，如果需要的话
    // 目前暂时返回固定值或基于数据的计算
    if (item.start_time && item.end_time) {
      // 简单的时间计算（小时）
      try {
        const startTime = new Date(`1970-01-01T${item.start_time}:00`)
        const endTime = new Date(`1970-01-01T${item.end_time}:00`)
        const diffHours = (endTime.getTime() - startTime.getTime()) / (1000 * 60 * 60)
        totalHours += Math.max(0, diffHours)
      } catch (error) {
        // 忽略时间解析错误
      }
    }
  })
  return totalHours.toFixed(1)
})

// 初始化
onMounted(() => {
  reportId.value = Number(route.params.id)
  
  // 检测查看模式
  isViewMode.value = route.query.view === 'true'
  console.log('页面模式:', isViewMode.value ? '查看模式' : '评价模式')
  
  if (reportId.value) {
    loadReportData().then(() => {
      // 根据日报状态自动判断显示模式
      // 如果日报状态是"已评价"，则显示查看模式
      // 如果日报状态是"已提交"，则显示评价模式
      if (reportData.value.status === '已评价') {
        isViewMode.value = true
        console.log('根据日报状态自动切换到查看模式')
      }
    })
  } else {
    ElMessage.error('无效的日报ID')
    goBack()
  }
})
</script>

<style scoped>
.daily-report-evaluation-detail {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
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
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.info-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 12px;
}

.card-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-item label {
  font-weight: 600;
  color: #606266;
  min-width: 80px;
  white-space: nowrap;
}

.info-item span {
  color: #303133;
  flex: 1;
}

.work-items-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.work-item {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 16px;
  background-color: #fafafa;
}

.work-item-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.work-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #409eff;
  color: white;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.work-content {
  color: #303133;
  font-weight: 500;
  flex: 1;
}

.work-item-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-left: 36px;
}

.work-time, .work-result {
  color: #606266;
  font-size: 14px;
}

.evaluation-display {
  padding: 16px 0;
}

.evaluation-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.score-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.score-section label {
  font-weight: 600;
  color: #606266;
  min-width: 80px;
}

.score-tag {
  font-size: 16px;
  padding: 8px 16px;
}

.score-description {
  color: #606266;
  font-size: 14px;
}

.comment-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comment-section label {
  font-weight: 600;
  color: #606266;
}

.comment-content {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  color: #303133;
  line-height: 1.5;
}

.evaluator-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.evaluator-info label {
  font-weight: 600;
  color: #606266;
  margin: 0;
}

.evaluator-name {
  font-weight: 500;
  color: #303133;
}

.evaluation-grades-info {
  margin: 16px 0;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
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

.card-content .comment-content {
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

.card-content .evaluation-time-text {
  color: #409eff;
  font-weight: 500;
  font-size: 14px;
}

.evaluation-time {
  color: #606266;
  font-size: 14px;
}

.evaluation-time label {
  font-weight: 600;
  margin-right: 8px;
}

.evaluation-form {
  padding: 16px 0;
}

/* 查看模式样式 */
.evaluation-view-mode {
  padding: 20px 0;
}

.view-mode-content {
  text-align: center;
}

.view-mode-content .el-empty {
  padding: 20px 0;
}

.view-mode-content p {
  color: #909399;
  font-size: 14px;
  margin-top: 8px;
}

.score-section .el-radio-group {
  display: flex;
  gap: 8px;
}

.grade-a .el-radio-button__inner {
  background-color: #f0f9ff;
  border-color: #409eff;
  color: #409eff;
}

.grade-b .el-radio-button__inner {
  background-color: #f0f9ff;
  border-color: #67c23a;
  color: #67c23a;
}

.grade-c .el-radio-button__inner {
  background-color: #fffbf0;
  border-color: #e6a23c;
  color: #e6a23c;
}

.grade-d .el-radio-button__inner {
  background-color: #fef0f0;
  border-color: #f56c6c;
  color: #f56c6c;
}

.grade-e .el-radio-button__inner {
  background-color: #fef0f0;
  border-color: #c45656;
  color: #c45656;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

/* 与日报填报页面保持一致的样式 */

/* 主容器 */
.daily-report-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.daily-report-content {
  max-width: 1200px;
  margin: 0 auto;
}

.report-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 标题区域 */
.report-header {
  padding: 24px 32px;
  border-bottom: 1px solid #ebeef5;
  background: white;
}

.report-title-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-title {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.header-back-btn {
  padding: 10px 20px;
}

/* 日期信息区域 */
.report-header-section {
  padding: 24px 32px;
  background: #fafbfc;
  border-bottom: 1px solid #ebeef5;
}

.date-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.date-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-label {
  font-weight: 600;
  color: #606266;
  font-size: 14px;
}

.date-value {
  color: #303133;
  font-weight: 500;
}

/* 表单区域 */
.daily-report-form {
  padding: 32px;
}

/* 表单区域 */
.form-section {
  margin-bottom: 32px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #409eff;
}

.section-number {
  width: 32px;
  height: 32px;
  background: #409eff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
}

.section-title {
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.section-content {
  padding-left: 44px;
}

/* 内容显示 */
.content-display {
  color: #303133;
  line-height: 1.6;
  font-size: 14px;
}

/* 工作项目统计 */
.task-stats-display {
  display: flex;
  gap: 32px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.task-stats-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.task-stats-item i {
  color: #409eff;
  font-size: 16px;
}

.task-stats-number {
  font-weight: 600;
  color: #409eff;
  font-size: 16px;
}

/* 工作项目显示 */
.work-items-display {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.work-item-card-display {
  border: 1px solid #e9ecef;
  border-radius: 12px;
  background: white;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.work-item-card-display:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 卡片头部 */
.card-header {
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-number {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-number .number {
  width: 24px;
  height: 24px;
  background: #409eff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

.card-number .text {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

/* 卡片内容 */
.card-content {
  padding: 20px;
}

/* 表单行 */
.form-row {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 24px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-label {
  min-width: 125px;
  font-weight: 500;
  color: #303133;
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding-top: 8px;
  line-height: 1.5;
  text-align: right;
  font-size: 14px;
}

.form-label i {
  color: #409eff;
  margin-top: 2px;
}

.form-field {
  flex: 1;
}

/* 评价组 */
.evaluation-group {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.evaluation-box {
  min-width: 160px;
  height: 160px;
  padding: 36px 40px;
  border: 1px solid #dcdfe6;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.evaluation-box:hover {
  border-color: #409eff;
  background: #f0f9ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.evaluation-box.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.evaluation-box .letter {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 3px;
}

.evaluation-box .description {
  font-size: 11px;
  text-align: center;
  line-height: 1.2;
  padding: 0 8px;
  white-space: nowrap;
}

/* 现代型评价组 */
.modern-evaluation-group {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.modern-evaluation-box {
  min-width: 120px;
  height: 100px;
  padding: 20px 24px;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  overflow: hidden;
}

.modern-evaluation-box::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent 0%, rgba(64, 158, 255, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.modern-evaluation-box:hover {
  border-color: #409eff;
  background: #f8fbff;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(64, 158, 255, 0.15);
}

.modern-evaluation-box:hover::before {
  opacity: 1;
}

.modern-evaluation-box.active {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border-color: #409eff;
  color: white;
  box-shadow: 0 8px 25px rgba(64, 158, 255, 0.4);
  transform: translateY(-2px);
}

.modern-evaluation-box.active::before {
  background: rgba(255, 255, 255, 0.1);
  opacity: 1;
}

.modern-letter {
  font-size: 32px;
  font-weight: 800;
  line-height: 1;
  position: relative;
  z-index: 1;
}

.modern-description {
  font-size: 12px;
  text-align: center;
  line-height: 1.2;
  padding: 0 8px;
  white-space: nowrap;
  position: relative;
  z-index: 1;
  font-weight: 500;
}

/* 评价显示 */
.evaluation-display {
  padding: 16px 0;
}

/* 工作评价醒目显示 */
.work-evaluation-display {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.evaluation-grade-tag {
  font-size: 14px;
  font-weight: 600;
  padding: 6px 12px;
  min-width: 32px;
  text-align: center;
}

.evaluation-grade-text {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.evaluation-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.score-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.score-section label {
  font-weight: 600;
  color: #606266;
  min-width: 80px;
}

.score-tag {
  font-size: 16px;
  padding: 8px 16px;
}

.score-description {
  color: #606266;
  font-size: 14px;
}

.comment-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comment-section label {
  font-weight: 600;
  color: #606266;
}

.comment-content {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  color: #303133;
  line-height: 1.5;
}

.evaluation-time {
  color: #606266;
  font-size: 14px;
}

.evaluation-time label {
  font-weight: 600;
  margin-right: 8px;
}

/* 评价说明 */
.evaluation-description {
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.evaluation-description p {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.evaluation-description p:first-child {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

/* 评价表单 */
.evaluation-form {
  padding: 16px 0;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

/* 空状态 */
.empty-work-items {
  text-align: center;
  color: #909399;
  padding: 40px;
  font-style: italic;
}

.empty-work-items i {
  font-size: 48px;
  margin-bottom: 16px;
  color: #c0c4cc;
}

.empty-work-items p {
  margin: 0;
  font-size: 16px;
}

/* 响应式 */
@media (max-width: 768px) {
  .daily-report-form {
    padding: 20px;
  }
  
  .section-content {
    padding-left: 0;
  }
  
  .date-section {
    grid-template-columns: 1fr;
  }
  
  .task-stats-display {
    flex-direction: column;
    gap: 16px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 12px;
  }
  
  .form-label {
    min-width: auto;
    text-align: left;
    padding-top: 0;
  }
  
  .evaluation-group {
    gap: 12px;
  }
  
  .evaluation-box {
    min-width: 120px;
    height: 120px;
    padding: 24px 20px;
    gap: 12px;
  }
  
  .evaluation-box .letter {
    font-size: 18px;
  }
  
  .evaluation-box .description {
    font-size: 10px;
  }
  
  .modern-evaluation-group {
    gap: 12px;
  }
  
  .modern-evaluation-box {
    min-width: 100px;
    height: 80px;
    padding: 16px 20px;
    gap: 6px;
  }
  
  .modern-letter {
    font-size: 24px;
  }
  
  .modern-description {
    font-size: 10px;
  }
  
  .work-evaluation-display {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    padding: 12px;
  }
}

/* 附件列表样式 */
.attachments-page-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attachment-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: #fafafa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.attachment-item:hover {
  background: #f5f7fa;
  border-color: #c0c4cc;
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
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.attachment-details {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.attachment-size,
.attachment-date {
  display: flex;
  align-items: center;
  gap: 4px;
}

.attachment-actions {
  display: flex;
  gap: 8px;
  margin-left: 16px;
}

.no-attachments {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
  color: #909399;
}

.no-attachments p {
  margin: 12px 0 0 0;
  font-size: 14px;
}
</style>