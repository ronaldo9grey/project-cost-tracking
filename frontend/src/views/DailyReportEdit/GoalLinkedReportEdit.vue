<template>
  <div class="goal-linked-report-container">
    <!-- 日报内容 -->
    <div class="report-content">
      <div class="report-header">
        <h1 class="report-title">
          {{ isEdit ? (isReportSubmitted ? '查看日清表' : '编辑日清表') : '新建日清表' }}
          <el-tag type="success" class="mode-tag">关联目标模式</el-tag>
        </h1>
        <div class="report-actions">
          <el-button type="default" size="large" @click="handleGoBack" :disabled="saving">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <el-button type="info" size="large" @click="handleAttachments" :disabled="saving">
            附件
          </el-button>
          <template v-if="!isReportSubmitted">
            <el-button type="success" size="large" @click="handleSave" :loading="saving">
              保存
            </el-button>
            <el-button 
              type="primary" 
              size="large" 
              @click="handleSubmit" 
              :loading="saving"
              :disabled="!canSubmit"
            >
              提交
            </el-button>
          </template>
        </div>
      </div>

      <!-- 日期选择 -->
      <div class="report-header-section">
        <div class="date-task-section">
          <div class="date-item">
            <label class="date-label">日报时间：</label>
            <el-date-picker
              v-model="selectedDate"
              type="date"
              placeholder="选择日报日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="handleDateChange"
              size="small"
              :disabled="isEdit"
            />
          </div>
        </div>
      </div>

      <!-- 周目标展示 -->
      <WeekGoalDisplay
        v-if="weeklyGoals.length > 0"
        :weekly-goals="weeklyGoals"
        :current-week-number="currentWeekNumber"
        :month="currentMonth"
        :month-title="currentMonthTitle"
      />

      <!-- 日报表单 -->
      <div class="daily-report-form">
        
        <!-- 一、今日工作事项（对应周目标分解） -->
        <div class="form-section">
          <div class="section-header">
            <div class="section-number">一</div>
            <div class="section-title">今日工作事项</div>
            <span class="section-subtitle">根据周目标分解填写，可添加多个事项</span>
          </div>
          
          <div class="section-content">
            <!-- 工作事项统计 -->
            <div class="task-stats" v-if="workItems.length > 0">
              <div class="task-stats-item">
                <el-icon><Document /></el-icon>
                <span>总事项数：</span>
                <span class="task-stats-number">{{ workItems.length }}</span>
              </div>
            </div>

            <!-- 工作事项卡片组 -->
            <div class="work-items-group">
              <div 
                v-for="(item, index) in workItems" 
                :key="item.key" 
                class="work-item-card"
              >
                <!-- 卡片头部 -->
                <div class="card-header">
                  <div class="card-number">
                    <span class="number">{{ index + 1 }}</span>
                    <span class="text">工作事项</span>
                  </div>
                  <div class="card-actions">
                    <el-button
                      type="text"
                      size="small"
                      @click="duplicateWorkItem(index)"
                      title="复制这一组"
                    >
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                  </div>
                </div>
              
                <!-- 卡片内容 -->
                <div class="card-content">
                  <!-- 关联项目任务 -->
                  <div class="form-row">
                    <label class="form-label required">
                      <el-icon><Link /></el-icon>
                      关联项目任务
                    </label>
                    <div class="form-field">
                      <el-select
                        v-model="item.relatedTask"
                        placeholder="选择关联的项目任务"
                        filterable
                        allow-create
                        default-first-option
                        size="small"
                        class="related-task-selector"
                        @change="(val) => handleRelatedTaskChange(val, item)"
                        :disabled="isReportSubmitted"
                      >
                        <el-option
                          v-for="task in myTasks"
                          :key="task.task_id"
                          :value="`${task.project_name} - ${task.task_name}`"
                          :label="`${task.project_name} - ${task.task_name}`"
                        >
                          <span style="font-size: 14px; color: #666; display: block;">{{ task.project_name }}</span>
                          <span style="font-size: 14px; font-weight: bold; color: #333; display: block;">{{ task.task_name }}</span>
                        </el-option>
                        
                        <template #empty>
                          <div class="empty-task">
                            <el-icon><Document /></el-icon>
                            暂无可用任务，请手动输入
                          </div>
                        </template>
                      </el-select>
                    </div>
                  </div>

                  <!-- 工作时间 -->
                  <div class="form-row">
                    <label class="form-label">
                      <el-icon><Clock /></el-icon>
                      工作时间
                    </label>
                    <div class="form-field">
                      <div class="time-picker-group">
                        <el-time-picker
                          v-model="item.startTime"
                          placeholder="开始时间"
                          format="HH:mm"
                          value-format="HH:mm"
                          size="small"
                          style="width: 120px"
                          @change="calculateHours(item)"
                          :disabled="isReportSubmitted"
                        />
                        <span class="time-separator">至</span>
                        <el-time-picker
                          v-model="item.endTime"
                          placeholder="结束时间"
                          format="HH:mm"
                          value-format="HH:mm"
                          size="small"
                          style="width: 120px"
                          @change="calculateHours(item)"
                          :disabled="isReportSubmitted"
                        />
                        <div class="hours-display">
                          <span class="hours-label">工时：</span>
                          <span class="hours-value">{{ item.hours_spent || 0 }}h</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 完成情况结果 -->
                  <div class="form-row">
                    <label class="form-label">
                      <el-icon><CircleCheck /></el-icon>
                      完成情况结果
                    </label>
                    <div class="form-field">
                      <el-input
                        v-model="item.result"
                        type="textarea"
                        :rows="2"
                        placeholder="请描述今日完成情况..."
                        maxlength="300"
                        show-word-limit
                        :disabled="isReportSubmitted"
                      />
                    </div>
                  </div>

                  <!-- 自我评价 -->
                  <div class="form-row">
                    <label class="form-label">
                      <el-icon><Star /></el-icon>
                      自我评价
                    </label>
                    <div class="form-field">
                      <div class="evaluation-group">
                        <div 
                          v-for="option in ['A', 'B', 'C', 'D', 'E']"
                          :key="option"
                          :class="['evaluation-box', { active: item.evaluation === option }]"
                          @click="!isReportSubmitted && (item.evaluation = option)"
                        >
                          <span class="letter">{{ option }}</span>
                          <span class="description">{{ getEvaluationDescription(option) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 添加工作事项按钮 -->
              <el-button 
                v-if="!isReportSubmitted"
                type="dashed" 
                class="add-item-btn"
                @click="addWorkItem"
              >
                <el-icon><Plus /></el-icon>
                添加工作事项
              </el-button>
            </div>
          </div>
        </div>

        <!-- 二、明日计划 -->
        <div class="form-section">
          <div class="section-header">
            <div class="section-number">二</div>
            <div class="section-title">明日计划</div>
          </div>
          <div class="section-content">
            <el-input
              v-model="reportForm.tomorrow_plan"
              type="textarea"
              :rows="3"
              placeholder="明日工作计划..."
              maxlength="500"
              show-word-limit
              :disabled="isReportSubmitted"
            />
          </div>
        </div>

        <!-- 提交时显示验证提示 -->
        <div v-if="!isReportSubmitted && validationErrors.length > 0" class="validation-errors">
          <el-alert
            type="error"
            :title="`请完善以下 ${validationErrors.length} 项内容：`"
            :description="validationErrors.join('； ')"
            show-icon
            :closable="false"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, Document, CopyDocument, Delete, EditPen,
  Link, Clock, CircleCheck, Star, Plus
} from '@element-plus/icons-vue'
import WeekGoalDisplay from './components/WeekGoalDisplay.vue'
import {
  getCurrentWeekGoal,
  createGoalLinkedReport,
  getMyTasks,
  getDailyReportDetail,
  updateDailyReport,
  submitDailyReport
} from '@/api/dailyReport'
import { getWeeklyGoals } from '@/api/goal'

const route = useRoute()
const router = useRouter()

// 状态
const loading = ref(false)
const saving = ref(false)
const isEdit = ref(false)
const reportId = ref<number | null>(null)
const isReportSubmitted = ref(false)

// 日期
const selectedDate = ref('')

// 周目标信息
const weekGoal = ref<any>(null)
const weeklyGoals = ref<any[]>([])
const currentWeekNumber = ref(1)
const currentMonth = ref('')
const currentMonthTitle = ref('')

// 我的任务列表
const myTasks = ref<any[]>([])

// 报告表单
const reportForm = reactive({
  tomorrow_plan: '继续推进本周目标',
  planned_hours: 0
})

// 工作事项列表
interface WorkItem {
  key: string
  relatedTask: string
  project_id: string
  project_name: string
  task_id: string
  task_name: string
  startTime: string
  endTime: string
  hours_spent: number
  result: string
  evaluation: string
}

const workItems = ref<WorkItem[]>([])

// 计算属性
const canSubmit = computed(() => {
  if (workItems.value.length === 0) return false
  return workItems.value.every(item => 
    item.relatedTask &&
    item.evaluation
  )
})

const validationErrors = computed(() => {
  const errors: string[] = []
  
  workItems.value.forEach((item, index) => {
    if (!item.relatedTask) {
      errors.push(`工作事项${index + 1}：关联项目任务未选择`)
    }
    if (!item.evaluation) {
      errors.push(`工作事项${index + 1}：自我评价未选择`)
    }
  })
  
  return errors
})

// 初始化
onMounted(async () => {
  console.log('【调试】页面挂载，开始初始化')
  const id = route.query.id as string
  if (id) {
    console.log('【调试】编辑模式，日报ID:', id)
    isEdit.value = true
    reportId.value = parseInt(id)
    await loadReportDetail()
  } else {
    console.log('【调试】新建模式')
    selectedDate.value = new Date().toISOString().split('T')[0]
    console.log('【调试】当前日期:', selectedDate.value)
    await initNewReport()
  }
  await loadMyTasks()
  console.log('【调试】初始化完成，weekGoal:', weekGoal.value)
})

// 加载日报详情
const loadReportDetail = async () => {
  if (!reportId.value) return

  try {
    loading.value = true
    const res = await getDailyReportDetail(reportId.value)

    if (res.data) {
      const data = res.data
      selectedDate.value = data.report_date
      reportForm.tomorrow_plan = data.tomorrow_plan || '继续推进本周目标'
      reportForm.planned_hours = data.planned_hours || 0
      isReportSubmitted.value = data.status === '已提交' || data.status === '已评价'

      // 加载周目标信息和所有周目标（用于显示四周目标）
      if (data.linked_weekly_goal_id) {
        await loadWeekGoalInfo(data.linked_weekly_goal_id)
        // 同时加载该月度目标下的所有周目标
        if (data.linked_monthly_goal_id) {
          try {
            const weeklyRes = await getWeeklyGoals(data.linked_monthly_goal_id)
            if (weeklyRes.data && weeklyRes.data.length > 0) {
              weeklyGoals.value = weeklyRes.data
              console.log('【调试】编辑模式 - 所有周目标已加载:', weeklyGoals.value)
            }
          } catch (e) {
            console.error('【调试】编辑模式 - 获取周目标列表失败:', e)
          }
        }
      }

      // 加载工作事项
      if (data.work_items && data.work_items.length > 0) {
        workItems.value = data.work_items.map((item: any) => ({
          key: `item_${item.id}_${Date.now()}`,
          relatedTask: item.project_id ? `${item.project_name} - ${item.task_name}` : '',
          project_id: item.project_id || '',
          project_name: item.project_name || '',
          task_id: item.task_id || '',
          task_name: item.task_name || '',
          startTime: item.start_time || '08:15',
          endTime: item.end_time || '18:00',
          hours_spent: item.hours_spent || 0,
          result: item.result || '',
          evaluation: item.evaluation || ''
        }))
      }
    }
  } catch (error) {
    ElMessage.error('加载日报详情失败')
  } finally {
    loading.value = false
  }
}

// 加载周目标信息
const loadWeekGoalInfo = async (weeklyGoalId: number) => {
  try {
    const res = await getCurrentWeekGoal(selectedDate.value)
    if (res.data && res.data.weekly_goal_id === weeklyGoalId) {
      weekGoal.value = res.data
    }
  } catch (error) {
    console.error('加载周目标信息失败', error)
  }
}

// 初始化新日报
const initNewReport = async () => {
  console.log('【调试】initNewReport 开始执行，日期:', selectedDate.value)
  try {
    loading.value = true
    const res = await getCurrentWeekGoal(selectedDate.value)
    console.log('【调试】getCurrentWeekGoal 返回:', res)

    // API可能直接返回数据或包装在data中
    const weekGoalData = res.data || res
    console.log('【调试】处理后的周目标数据:', weekGoalData)

    if (weekGoalData && weekGoalData.weekly_goal_id) {
      weekGoal.value = weekGoalData
      currentWeekNumber.value = weekGoalData.week_number || 1
      currentMonth.value = weekGoalData.month || ''
      currentMonthTitle.value = weekGoalData.month_title || ''
      console.log('【调试】weekGoal 已设置:', weekGoal.value)

      // 获取该月度目标下的所有周目标
      if (weekGoalData.monthly_goal_id) {
        try {
          const weeklyRes = await getWeeklyGoals(weekGoalData.monthly_goal_id)
          if (weeklyRes.data) {
            weeklyGoals.value = weeklyRes.data
            console.log('【调试】所有周目标已获取:', weeklyGoals.value)
          }
        } catch (e) {
          console.error('【调试】获取周目标列表失败:', e)
          // 如果获取失败，至少显示当前周
          weeklyGoals.value = [{
            week_number: weekGoalData.week_number,
            title: weekGoalData.weekly_goal_title,
            content: weekGoalData.weekly_goal_content
          }]
        }
      } else {
        // 如果没有 monthly_goal_id，只显示当前周
        weeklyGoals.value = [{
          week_number: weekGoalData.week_number,
          title: weekGoalData.weekly_goal_title,
          content: weekGoalData.weekly_goal_content
        }]
      }

      // 自动创建第一个工作事项
      const newItem: WorkItem = {
        key: `item_${Date.now()}`,
        relatedTask: '',
        project_id: '',
        project_name: '',
        task_id: '',
        task_name: '',
        startTime: '08:15',
        endTime: '18:00',
        hours_spent: 9.75, // 默认工时 08:15-18:00 = 9.75小时
        result: '',
        evaluation: ''
      }
      workItems.value = [newItem]
      console.log('【调试】工作事项已创建:', workItems.value)

      // 更新总工时
      reportForm.planned_hours = 9.75
      console.log('【调试】总工时已设置:', reportForm.planned_hours)
    }
  } catch (error: any) {
    console.error('【调试】获取本周目标失败:', error)
    ElMessage.error(error.message || '获取本周目标失败')
    // 创建空的工作事项
    workItems.value = [{
      key: `item_${Date.now()}`,
      relatedTask: '',
      project_id: '',
      project_name: '',
      task_id: '',
      task_name: '',
      startTime: '08:15',
      endTime: '18:00',
      hours_spent: 9.75,
      result: '',
      evaluation: ''
    }]
  } finally {
    loading.value = false
  }
}

// 加载我的任务
const loadMyTasks = async () => {
  try {
    const res = await getMyTasks()
    if (res.data) {
      myTasks.value = res.data
    }
  } catch (error) {
    console.error('加载任务列表失败', error)
  }
}

// 日期变更
const handleDateChange = async () => {
  console.log('【调试】日期变更:', selectedDate.value)
  if (!isEdit.value) {
    // 清空当前数据
    weekGoal.value = null
    weeklyGoals.value = []
    currentWeekNumber.value = 1
    currentMonth.value = ''
    currentMonthTitle.value = ''
    workItems.value = []
    await initNewReport()
  }
}

// 关联任务变更
const handleRelatedTaskChange = (val: string, item: WorkItem) => {
  if (!val) {
    item.project_id = ''
    item.project_name = ''
    item.task_id = ''
    item.task_name = ''
    return
  }
  
  const task = myTasks.value.find(t => `${t.project_name} - ${t.task_name}` === val)
  if (task) {
    item.project_id = task.project_id
    item.project_name = task.project_name
    item.task_id = task.task_id
    item.task_name = task.task_name
  } else {
    // 手动输入的情况
    const parts = val.split(' - ')
    if (parts.length >= 2) {
      item.project_name = parts[0]
      item.task_name = parts[1]
    }
  }
}

// 计算工时
const calculateHours = (item: WorkItem) => {
  if (item.startTime && item.endTime) {
    const start = new Date(`2000-01-01T${item.startTime}`)
    const end = new Date(`2000-01-01T${item.endTime}`)
    let hours = (end.getTime() - start.getTime()) / (1000 * 60 * 60)
    if (hours < 0) hours += 24 // 跨天情况
    item.hours_spent = Math.round(hours * 10) / 10
    
    // 更新总计划工时
    updateTotalHours()
  }
}

// 更新总工时
const updateTotalHours = () => {
  reportForm.planned_hours = workItems.value.reduce((sum, item) => {
    return sum + (item.hours_spent || 0)
  }, 0)
}

// 添加工作事项
const addWorkItem = () => {
  workItems.value.push({
    key: `item_${Date.now()}`,
    relatedTask: '',
    project_id: '',
    project_name: '',
    task_id: '',
    task_name: '',
    startTime: '08:15',
    endTime: '18:00',
    hours_spent: 9.75,
    result: '',
    evaluation: ''
  })
}

// 复制工作事项
const duplicateWorkItem = (index: number) => {
  const item = workItems.value[index]
  workItems.value.splice(index + 1, 0, {
    ...item,
    key: `item_${Date.now()}`,
    result: '',
    evaluation: ''
  })
  updateTotalHours()
}

// 删除工作事项
const confirmDeleteWorkItem = (index: number) => {
  if (workItems.value.length <= 1) {
    ElMessage.warning('至少保留一个工作事项')
    return
  }

  ElMessageBox.confirm('确定删除这个工作事项吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    workItems.value.splice(index, 1)
    updateTotalHours()
    ElMessage.success('删除成功')
  }).catch(() => {})
}

// 获取评价描述
const getEvaluationDescription = (option: string) => {
  const descriptions: Record<string, string> = {
    'A': '超目标达成',
    'B': '按目标达成',
    'C': '达成目标80%',
    'D': '达成目标50%-80%',
    'E': '小于目标50%'
  }
  return descriptions[option] || ''
}

// 保存日报
const handleSave = async () => {
  if (workItems.value.length === 0) {
    ElMessage.warning('请至少添加一个工作事项')
    return
  }
  
  try {
    saving.value = true
    
    const workItemsData = workItems.value.map(item => ({
      project_id: item.project_id,
      project_name: item.project_name,
      task_id: item.task_id,
      task_name: item.task_name,
      start_time: item.startTime,
      end_time: item.endTime,
      hours_spent: item.hours_spent,
      result: item.result,
      evaluation: item.evaluation
    }))
    
    if (isEdit.value && reportId.value) {
      // 更新现有日报
      await updateDailyReport(reportId.value, {
        tomorrow_plan: reportForm.tomorrow_plan,
        planned_hours: reportForm.planned_hours,
        work_items: workItemsData
      })
      ElMessage.success('保存成功')
    } else {
      // 创建新日报
      // 如果有周目标信息，则使用关联目标模式；否则使用自由填报模式
      const hasGoal = weekGoal.value && weekGoal.value.weekly_goal_id
      const res = await createGoalLinkedReport({
        report_date: selectedDate.value,
        tomorrow_plan: reportForm.tomorrow_plan,
        planned_hours: reportForm.planned_hours,
        linked_monthly_goal_id: hasGoal ? (weekGoal.value?.monthly_goal_id || 0) : 0,
        linked_weekly_goal_id: hasGoal ? (weekGoal.value?.weekly_goal_id || 0) : 0,
        work_items: workItemsData
      })
      
      if (res.data) {
        reportId.value = res.data.id
        isEdit.value = true
        ElMessage.success('创建成功')
      }
    }
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 提交日报
const handleSubmit = async () => {
  if (!canSubmit.value) {
    ElMessage.warning('请完善所有必填项')
    return
  }
  
  try {
    await ElMessageBox.confirm('确定提交日报吗？提交后将不可修改', '确认提交', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    saving.value = true
    
    // 先保存
    await handleSave()
    
    // 再提交
    if (reportId.value) {
      await submitDailyReport(reportId.value)
      isReportSubmitted.value = true
      ElMessage.success('提交成功')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '提交失败')
    }
  } finally {
    saving.value = false
  }
}

// 返回
const handleGoBack = () => {
  router.push('/daily-reports')
}

// 附件管理
const handleAttachments = () => {
  if (!reportId.value) {
    ElMessage.warning('请先保存日报')
    return
  }
  // 打开附件管理弹窗或跳转
  ElMessage.info('附件功能开发中')
}
</script>

<style scoped lang="scss">
.goal-linked-report-container {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.report-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  padding: 30px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;

  .report-title {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
    color: #303133;
    display: flex;
    align-items: center;
    gap: 12px;

    .mode-tag {
      font-size: 13px;
    }
  }

  .report-actions {
    display: flex;
    gap: 12px;
  }
}

.report-header-section {
  margin-bottom: 20px;

  .date-task-section {
    display: flex;
    gap: 20px;
  }

  .date-item {
    display: flex;
    align-items: center;
    gap: 8px;

    .date-label {
      font-weight: 500;
      color: #606266;
    }
  }
}

.daily-report-form {
  .form-section {
    margin-bottom: 30px;
  }

  .section-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #409eff;

    .section-number {
      background: #409eff;
      color: white;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      font-weight: bold;
      margin-right: 15px;
    }

    .section-title {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }

    .section-subtitle {
      font-size: 13px;
      color: #909399;
      margin-left: auto;
    }
  }

  .section-content {
    padding-left: 0;
  }
}

.task-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
  padding: 12px 16px;
  background-color: #f5f7fa;
  border-radius: 4px;

  .task-stats-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 14px;
    color: #606266;

    .task-stats-number {
      color: #409eff;
      font-weight: 600;
      font-size: 16px;
    }
  }
}

.work-items-group {
  .work-item-card {
    border: 1px solid #dcdfe6;
    border-radius: 8px;
    margin-bottom: 16px;
    overflow: hidden;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      background-color: #f5f7fa;
      border-bottom: 1px solid #e4e7ed;

      .card-number {
        display: flex;
        align-items: center;
        gap: 8px;

        .number {
          width: 24px;
          height: 24px;
          background-color: #409eff;
          color: white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
        }

        .text {
          font-weight: 500;
          color: #606266;
        }
      }

      .card-actions {
        .delete-btn {
          color: #f56c6c;
        }
      }
    }

    .card-content {
      padding: 16px;
    }
  }

  .add-item-btn {
    width: 100%;
    border-style: dashed;
    margin-top: 8px;
  }
}

.form-row {
  display: flex;
  margin-bottom: 16px;
  align-items: flex-start;

  &:last-child {
    margin-bottom: 0;
  }

  .form-label {
    width: 110px;
    flex-shrink: 0;
    font-weight: 500;
    color: #606266;
    display: flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 32px;

    &.required::before {
      content: '*';
      color: #f56c6c;
      margin-right: 4px;
    }
  }

  .form-field {
    flex: 1;
    min-width: 0;

    .time-picker-group {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;

      .time-separator {
        color: #909399;
      }

      .hours-display {
        margin-left: 16px;
        padding: 4px 12px;
        background-color: #f0f9ff;
        border-radius: 4px;

        .hours-label {
          color: #606266;
        }

        .hours-value {
          color: #1890ff;
          font-weight: 600;
        }
      }
    }

    .related-task-selector {
      width: 100%;

      :deep(.el-input__wrapper) {
        max-width: 100%;
      }

      :deep(.el-input__inner) {
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
      }
    }
  }
}

.validation-errors {
  margin-top: 20px;
}

.empty-task {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 20px;
  color: #909399;
}

// 自我评价样式
.evaluation-group {
  display: flex;
  gap: 12px;

  .evaluation-box {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 12px 8px;
    border: 2px solid #dcdfe6;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      border-color: #409eff;
    }

    &.active {
      border-color: #409eff;
      background-color: #ecf5ff;
    }

    .letter {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 4px;
    }

    .description {
      font-size: 12px;
      color: #606266;
      text-align: center;
    }
  }
}
</style>
