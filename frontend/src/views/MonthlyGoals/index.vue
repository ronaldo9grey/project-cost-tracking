<template>
  <div class="monthly-goals-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">{{ currentYear }}年 目标管理</h1>
      <div class="header-actions">
        <el-button type="success" @click="handleGenerateFromTasks" :loading="generating">
          <el-icon><MagicStick /></el-icon>
          从任务生成
        </el-button>
        <el-button-group>
          <el-button @click="changeYear(-1)">
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <el-button disabled>{{ currentYear }}年</el-button>
          <el-button @click="changeYear(1)">
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </el-button-group>
      </div>
    </div>

    <!-- 12个月卡片网格 -->
    <div class="months-grid" v-loading="loading">
      <div
        v-for="month in 12"
        :key="month"
        :class="['month-card', { 'has-goal': hasGoal(month), 'active': selectedMonth === month }]"
        @click="handleMonthClick(month)"
      >
        <div class="month-header">
          <span class="month-number">{{ month }}月</span>
          <el-tag
            v-if="hasGoal(month)"
            :type="getGoalStatusType(month)"
            size="small"
            class="status-tag"
          >
            {{ getGoalStatusText(month) }}
          </el-tag>
          <el-tag v-else type="info" size="small" class="status-tag">未创建</el-tag>
        </div>

        <div class="month-content">
          <template v-if="hasGoal(month)">
            <div class="goal-title" :title="getGoal(month)?.title">{{ getGoal(month)?.title }}</div>
            <div class="goal-progress">
              <el-progress
                :percentage="Number(getGoal(month)?.progress_rate || getGoal(month)?.progress || 0)"
                :stroke-width="6"
                :show-text="false"
              />
              <span class="progress-text">{{ Number(getGoal(month)?.progress_rate || getGoal(month)?.progress || 0) }}%</span>
            </div>
            <div class="weeks-indicator">
              <div class="weeks-dots">
                <span
                  v-for="week in 4"
                  :key="week"
                  :class="['week-dot', { 'completed': hasWeekGoal(month, week) }]"
                />
              </div>
            </div>
          </template>
          <template v-else>
            <div class="empty-tip">
              <el-icon class="add-icon"><Plus /></el-icon>
              <span>点击创建</span>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 编辑区域 - 默认显示提示 -->
    <div class="edit-section">
      <!-- 有选中月份时显示编辑表单 -->
      <template v-if="selectedMonth > 0">
        <div class="edit-header">
          <div class="edit-title-wrapper">
            <el-icon class="title-icon"><Calendar /></el-icon>
            <span class="edit-title">{{ currentYear }}年{{ selectedMonth }}月 {{ isEdit ? '编辑目标' : '创建目标' }}</span>
          </div>
          <el-button type="info" text @click="selectedMonth = 0">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
        
        <div class="edit-content">
          <!-- 月度目标 - 左侧大区域 -->
          <div class="monthly-goal-section">
            <div class="section-header">
              <span class="section-tag">月度</span>
              <span class="section-title">结果目标</span>
            </div>
            
            <el-form
              ref="formRef"
              :model="form"
              :rules="formRules"
              label-position="top"
            >
              <el-form-item prop="title" class="large-form-item">
                <template #label>
                  <span class="field-label">结果目标</span>
                </template>
                <el-input
                  v-model="form.title"
                  placeholder="请输入本月要达成的结果目标"
                  maxlength="100"
                  show-word-limit
                  size="large"
                />
              </el-form-item>

              <el-form-item class="large-form-item">
                <template #label>
                  <span class="field-label">具体内容</span>
                </template>
                <el-input
                  v-model="form.description"
                  type="textarea"
                  :rows="8"
                  placeholder="描述具体的工作内容、交付物和验收标准"
                  maxlength="500"
                  show-word-limit
                />
              </el-form-item>
            </el-form>
          </div>

          <!-- 四周目标 - 右侧大区域 -->
          <div class="weekly-goals-section">
            <div class="section-header">
              <span class="section-tag weekly">周目标</span>
              <span class="section-title">四周拆解</span>
            </div>
            
            <div class="weeks-list">
              <div
                v-for="(week, index) in weeklyGoals"
              :key="index"
              class="week-row"
            >
              <div class="week-info">
                <div class="week-badge">第{{ index + 1 }}周</div>
                <div class="week-date-range">{{ getWeekDateRange(index) }}</div>
              </div>
              
              <div class="week-inputs">
                <el-input
                  v-model="week.title"
                  placeholder="本周结果目标"
                  maxlength="100"
                  show-word-limit
                  class="week-title-input"
                >
                  <template #prefix>
                    <el-icon><Flag /></el-icon>
                  </template>
                </el-input>
                <el-input
                  v-model="week.description"
                  type="textarea"
                  :rows="4"
                  placeholder="具体内容"
                  maxlength="300"
                  show-word-limit
                  class="week-desc-input"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="edit-footer">
        <el-button size="large" @click="selectedMonth = 0">取消</el-button>
        <el-button
          v-if="isEdit"
          type="danger"
          size="large"
          @click="handleDelete"
          :loading="deleting"
        >
          删除
        </el-button>
        <el-button
          type="primary"
          size="large"
          @click="handleSave"
          :loading="saving"
        >
          {{ isEdit ? '更新目标' : '创建目标' }}
        </el-button>
        <el-button
          v-if="isEdit && form.status === 'draft'"
          type="success"
          size="large"
          @click="handlePublish"
          :loading="publishing"
        >
          发布目标
        </el-button>
      </div>
      </template>
      
      <!-- 未选中月份时显示提示 -->
      <template v-else>
        <div class="edit-placeholder">
          <div class="placeholder-icon">
            <el-icon><Calendar /></el-icon>
          </div>
          <div class="placeholder-text">
            <h3>请选择月度卡片</h3>
            <p>点击上方任意月份卡片，创建或编辑该月的目标</p>
          </div>
          <div class="placeholder-tips">
            <div class="tip-item">
              <el-icon><CircleCheck /></el-icon>
              <span>制定月度结果目标</span>
            </div>
            <div class="tip-item">
              <el-icon><CircleCheck /></el-icon>
              <span>拆解为四周周目标</span>
            </div>
            <div class="tip-item">
              <el-icon><CircleCheck /></el-icon>
              <span>跟踪进度直至完成</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { ArrowLeft, ArrowRight, Plus, Calendar, MagicStick, Close, CircleCheck, Flag } from '@element-plus/icons-vue'
import {
  getMonthlyGoals,
  createMonthlyGoal,
  updateMonthlyGoal,
  deleteMonthlyGoal,
  publishMonthlyGoal,
  getWeeklyGoals,
  createWeeklyGoal,
  updateWeeklyGoal,
  deleteWeeklyGoal,
  generateGoalsFromTasks,
  type MonthlyGoal,
  type WeeklyGoal
} from '@/api/goal'

const currentYear = ref(new Date().getFullYear())
const loading = ref(false)
const monthlyGoals = ref<MonthlyGoal[]>([])
const weeklyGoalsMap = ref<Map<number, WeeklyGoal[]>>(new Map())
const selectedMonth = ref<number>(0)
const isEdit = ref(false)
const editingGoalId = ref<number | null>(null)
const saving = ref(false)
const deleting = ref(false)
const publishing = ref(false)
const generating = ref(false)

const formRef = ref<FormInstance>()
const form = reactive({
  title: '',
  description: '',
  status: 'draft'
})

const weeklyGoals = reactive([
  { title: '', description: '' },
  { title: '', description: '' },
  { title: '', description: '' },
  { title: '', description: '' }
])

const formRules: FormRules = {
  title: [
    { required: true, message: '请输入结果目标', trigger: 'blur' },
    { min: 2, max: 100, message: '长度2-100字符', trigger: 'blur' }
  ]
}

const hasGoal = (month: number) => {
  const monthStr = `${currentYear.value}-${String(month).padStart(2, '0')}`
  return monthlyGoals.value.some(g => g.month === monthStr)
}

const getGoal = (month: number): MonthlyGoal | undefined => {
  const monthStr = `${currentYear.value}-${String(month).padStart(2, '0')}`
  return monthlyGoals.value.find(g => g.month === monthStr)
}

const getGoalStatusType = (month: number) => {
  const goal = getGoal(month)
  if (!goal) return 'info'
  const map: Record<string, string> = {
    'draft': 'info',
    'published': 'success',
    'completed': 'success'
  }
  return map[goal.status] || 'info'
}

const getGoalStatusText = (month: number) => {
  const goal = getGoal(month)
  if (!goal) return '未创建'
  const map: Record<string, string> = {
    'draft': '草稿',
    'published': '已发布',
    'completed': '已完成'
  }
  return map[goal.status] || goal.status
}

const hasWeekGoal = (month: number, week: number) => {
  const goal = getGoal(month)
  if (!goal) return false
  const weeks = weeklyGoalsMap.value.get(goal.id)
  if (!weeks) return false
  return weeks.some(w => w.week_number === week)
}

const getWeekDateRange = (weekIndex: number) => {
  const month = selectedMonth.value
  const year = currentYear.value
  const firstDayOfMonth = new Date(year, month - 1, 1)
  const firstMonday = new Date(firstDayOfMonth)
  const dayOfWeek = firstDayOfMonth.getDay()
  const daysUntilMonday = dayOfWeek === 0 ? 1 : (dayOfWeek === 1 ? 0 : 8 - dayOfWeek)
  firstMonday.setDate(firstDayOfMonth.getDate() + daysUntilMonday)
  const weekStart = new Date(firstMonday)
  weekStart.setDate(firstMonday.getDate() + weekIndex * 7)
  const weekEnd = new Date(weekStart)
  weekEnd.setDate(weekStart.getDate() + 6)
  return `${month}月${weekStart.getDate()}日-${weekEnd.getDate()}日`
}

const changeYear = (delta: number) => {
  currentYear.value += delta
  selectedMonth.value = 0
  loadData()
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getMonthlyGoals({
      month: `${currentYear.value}-`,
      page: 1,
      size: 100
    })
    if (res && 'items' in res) {
      monthlyGoals.value = res.items || []
      for (const goal of monthlyGoals.value) {
        try {
          const weeksRes = await getWeeklyGoals(goal.id)
          if (weeksRes && 'items' in weeksRes) {
            weeklyGoalsMap.value.set(goal.id, weeksRes.items)
          }
        } catch (e) {
          console.error('加载周目标失败:', e)
        }
      }
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleMonthClick = (month: number) => {
  selectedMonth.value = month
  const existingGoal = getGoal(month)
  if (existingGoal) {
    isEdit.value = true
    editingGoalId.value = existingGoal.id
    form.title = existingGoal.title
    form.description = existingGoal.description || ''
    form.status = existingGoal.status
    const weeks = weeklyGoalsMap.value.get(existingGoal.id) || []
    for (let i = 0; i < 4; i++) {
      const week = weeks.find(w => w.week_number === i + 1)
      if (week) {
        weeklyGoals[i].title = week.title
        weeklyGoals[i].description = week.description || week.content || ''
      } else {
        weeklyGoals[i].title = ''
        weeklyGoals[i].description = ''
      }
    }
  } else {
    isEdit.value = false
    editingGoalId.value = null
    form.title = ''
    form.description = ''
    form.status = 'draft'
    for (let i = 0; i < 4; i++) {
      weeklyGoals[i].title = ''
      weeklyGoals[i].description = ''
    }
  }
}

const handleSave = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    saving.value = true
    const monthStr = `${currentYear.value}-${String(selectedMonth.value).padStart(2, '0')}`
    if (isEdit.value && editingGoalId.value) {
      await updateMonthlyGoal(editingGoalId.value, {
        title: form.title,
        description: form.description
      })
      const existingWeeks = weeklyGoalsMap.value.get(editingGoalId.value) || []
      for (let i = 0; i < 4; i++) {
        const existingWeek = existingWeeks.find(w => w.week_number === i + 1)
        if (weeklyGoals[i].title) {
          if (existingWeek) {
            await updateWeeklyGoal(existingWeek.id, {
              title: weeklyGoals[i].title,
              description: weeklyGoals[i].description
            })
          } else {
            await createWeeklyGoal(editingGoalId.value, {
              week_number: i + 1,
              title: weeklyGoals[i].title,
              description: weeklyGoals[i].description
            })
          }
        } else if (existingWeek) {
          await deleteWeeklyGoal(existingWeek.id)
        }
      }
      ElMessage.success('更新成功')
    } else {
      const newGoal = await createMonthlyGoal({
        month: monthStr,
        title: form.title,
        description: form.description,
        planned_hours: 0
      })
      if (newGoal && newGoal.id) {
        for (let i = 0; i < 4; i++) {
          if (weeklyGoals[i].title) {
            await createWeeklyGoal(newGoal.id, {
              week_number: i + 1,
              title: weeklyGoals[i].title,
              description: weeklyGoals[i].description
            })
          }
        }
      }
      ElMessage.success('创建成功')
    }
    selectedMonth.value = 0
    loadData()
  } catch (error: any) {
    ElMessage.error(error.message || (isEdit.value ? '更新失败' : '创建失败'))
  } finally {
    saving.value = false
  }
}

const handlePublish = async () => {
  if (!editingGoalId.value) return
  try {
    await ElMessageBox.confirm('确定要发布这个目标吗？发布后将对团队可见。', '确认发布', 
      { confirmButtonText: '确认', cancelButtonText: '取消', type: 'warning' })
    publishing.value = true
    await publishMonthlyGoal(editingGoalId.value)
    ElMessage.success('发布成功')
    selectedMonth.value = 0
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '发布失败')
    }
  } finally {
    publishing.value = false
  }
}

const handleDelete = async () => {
  if (!editingGoalId.value) return
  try {
    await ElMessageBox.confirm('确定要删除这个目标吗？删除后将无法恢复。', '确认删除',
      { confirmButtonText: '确认', cancelButtonText: '取消', type: 'danger' })
    deleting.value = true
    await deleteMonthlyGoal(editingGoalId.value)
    ElMessage.success('删除成功')
    selectedMonth.value = 0
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  } finally {
    deleting.value = false
  }
}

const handleGenerateFromTasks = async () => {
  try {
    await ElMessageBox.confirm(
      `将根据您负责的项目任务自动生成 ${currentYear.value} 年的目标数据。`,
      '自动生成目标',
      { confirmButtonText: '确定生成', cancelButtonText: '取消', type: 'info' })
    
    // 显示AI分析中提示
    const loadingInstance = ElLoading.service({
      lock: true,
      text: 'AI正在智能拆解目标...',
      spinner: 'Loading',
      background: 'rgba(0, 0, 0, 0.7)',
      customClass: 'ai-loading'
    })
    
    generating.value = true
    const res = await generateGoalsFromTasks(currentYear.value)
    loadingInstance.close()
    
    if (res && res.data) {
      const { generated_months, total_tasks } = res.data
      const created = generated_months.filter((m: any) => m.status === 'created')
      const aiGenerated = created.filter((m: any) => m.ai_generated)
      const fallbackGenerated = created.filter((m: any) => !m.ai_generated)
      const errors = generated_months.filter((m: any) => m.ai_error)
      
      // 构建提示信息
      let message = `<div style="text-align: left;">`
      message += `<p style="font-size: 16px; font-weight: bold; margin-bottom: 10px;">✅ 目标生成完成</p>`
      message += `<p>共分析到 <strong>${total_tasks}</strong> 个任务，成功生成 <strong>${created.length}</strong> 个月的目标</p>`
      
      if (aiGenerated.length > 0) {
        message += `<div style="margin-top: 10px; padding: 10px; background: #f0f9ff; border-radius: 6px; border-left: 3px solid #1890ff;">`
        message += `<p style="color: #1890ff; font-weight: bold; margin: 0;">🤖 AI智能生成: ${aiGenerated.length} 个月</p>`
        message += `<p style="font-size: 12px; color: #666; margin: 5px 0 0 0;">基于SMART原则 · OKR方法论 · 敏捷开发实践</p>`
        message += `</div>`
      }
      
      if (fallbackGenerated.length > 0) {
        message += `<div style="margin-top: 8px; padding: 8px; background: #fff7e6; border-radius: 6px; border-left: 3px solid #fa8c16;">`
        message += `<p style="color: #fa8c16; font-size: 13px; margin: 0;">⚠️ 模板生成: ${fallbackGenerated.length} 个月（AI服务异常）</p>`
        message += `</div>`
      }
      
      if (errors.length > 0) {
        message += `<div style="margin-top: 8px; padding: 8px; background: #fff1f0; border-radius: 6px; border-left: 3px solid #f5222d;">`
        message += `<p style="color: #f5222d; font-size: 13px; margin: 0;">❌ 生成失败: ${errors.length} 个月</p>`
        errors.forEach((err: any) => {
          if (err.ai_error) {
            message += `<p style="font-size: 11px; color: #999; margin: 4px 0 0 0;">${err.month}: ${err.ai_error}</p>`
          }
        })
        message += `</div>`
      }
      
      // 拆解规则说明
      message += `<div style="margin-top: 12px; padding: 12px; background: #f6ffed; border-radius: 6px; border: 1px solid #b7eb8f;">`
      message += `<p style="font-weight: bold; color: #52c41a; margin: 0 0 8px 0;">📋 AI拆解规则</p>`
      message += `<ul style="margin: 0; padding-left: 16px; font-size: 12px; color: #666;">`
      message += `<li><strong>SMART原则</strong>：具体、可衡量、可达成、相关、有时限</li>`
      message += `<li><strong>OKR方法论</strong>：目标与关键结果对齐，聚焦核心成果</li>`
      message += `<li><strong>敏捷开发</strong>：迭代推进，每周有明确交付物</li>`
      message += `<li><strong>成果导向</strong>：强调结果价值，而非任务罗列</li>`
      message += `</ul>`
      message += `</div>`
      
      message += `</div>`
      
      ElMessageBox.alert(message, '生成结果', {
        dangerouslyUseHTMLString: true,
        confirmButtonText: '确定',
        customClass: 'ai-result-dialog'
      })
      
      loadData()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '生成失败')
    }
  } finally {
    generating.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.monthly-goals-page {
  padding: 20px;
  min-height: calc(100vh - 60px);
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-shrink: 0;
  
  .page-title {
    font-size: 20px;
    font-weight: 600;
    color: #1f2f3d;
    margin: 0;
  }
  
  .header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

// 月度卡片 - 保持原样
.months-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  margin-bottom: 16px;
  flex-shrink: 0;
  
  @media (max-width: 1200px) {
    grid-template-columns: repeat(4, 1fr);
  }
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(3, 1fr);
  }
  
  @media (max-width: 480px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.month-card {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e0e0e0;
  
  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border-color: #1890ff;
  }
  
  &.has-goal {
    border-left: 3px solid #1890ff;
  }
  
  &.active {
    border-color: #1890ff;
    box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.15);
  }
}

.month-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  
  .month-number {
    font-size: 15px;
    font-weight: 600;
    color: #1f2f3d;
  }
  
  .status-tag {
    font-size: 11px;
  }
}

.month-content {
  .goal-title {
    font-size: 13px;
    color: #333;
    margin-bottom: 8px;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    height: 36px;
  }
  
  .goal-progress {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    
    .el-progress {
      flex: 1;
    }
    
    .progress-text {
      font-size: 12px;
      font-weight: 500;
      color: #1890ff;
      min-width: 32px;
    }
  }
  
  .weeks-indicator {
    .weeks-dots {
      display: flex;
      gap: 4px;
      
      .week-dot {
        width: 8px;
        height: 8px;
        border-radius: 2px;
        background: #e0e0e0;
        
        &.completed {
          background: #52c41a;
        }
      }
    }
  }
  
  .empty-tip {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 60px;
    color: #999;
    
    .add-icon {
      font-size: 24px;
      margin-bottom: 4px;
      color: #ccc;
    }
    
    span {
      font-size: 12px;
    }
  }
}

// 编辑区域 - 充满剩余空间
.edit-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 400px;
  
  .edit-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 2px solid #f0f0f0;
    flex-shrink: 0;
    
    .edit-title-wrapper {
      display: flex;
      align-items: center;
      gap: 10px;
      
      .title-icon {
        color: #1890ff;
        font-size: 22px;
      }
      
      .edit-title {
        font-size: 18px;
        font-weight: 600;
        color: #1f2f3d;
      }
    }
  }
  
  .edit-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32px;
    flex: 1;
    overflow: hidden;
    
    @media (max-width: 992px) {
      grid-template-columns: 1fr;
      gap: 20px;
      overflow-y: auto;
    }
  }
  
  // 区域标题样式
  .section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
    
    .section-tag {
      background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
      color: #fff;
      font-size: 12px;
      font-weight: 600;
      padding: 4px 12px;
      border-radius: 20px;
      
      &.weekly {
        background: linear-gradient(135deg, #52c41a 0%, #95de64 100%);
      }
    }
    
    .section-title {
      font-size: 16px;
      font-weight: 600;
      color: #1f2f3d;
    }
  }
  
  // 月度目标区域
  .monthly-goal-section {
    display: flex;
    flex-direction: column;
    
    .large-form-item {
      margin-bottom: 20px;
      
      :deep(.el-form-item__label) {
        padding-bottom: 8px;
      }
      
      .field-label {
        font-size: 14px;
        font-weight: 500;
        color: #333;
      }
      
      :deep(.el-input__inner) {
        height: 44px;
        font-size: 15px;
      }
      
      :deep(.el-textarea__inner) {
        font-size: 14px;
        padding: 12px;
        line-height: 1.6;
      }
    }
  }
  
  // 周目标区域
  .weekly-goals-section {
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    
    .weeks-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    
    .week-row {
      display: flex;
      gap: 16px;
      padding: 16px;
      background: #f8f9fa;
      border-radius: 10px;
      border: 1px solid #e8e8e8;
      transition: all 0.2s;
      
      &:hover {
        border-color: #1890ff;
        box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
      }
      
      .week-info {
        display: flex;
        flex-direction: column;
        gap: 4px;
        min-width: 100px;
        
        .week-badge {
          background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
          color: #fff;
          font-size: 13px;
          font-weight: 600;
          padding: 6px 14px;
          border-radius: 20px;
          text-align: center;
        }
        
        .week-date-range {
          font-size: 12px;
          color: #666;
          text-align: center;
        }
      }
      
      .week-inputs {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 10px;
        
        .week-title-input {
          :deep(.el-input__inner) {
            height: 40px;
            font-size: 14px;
          }
          
          :deep(.el-input__prefix) {
            color: #1890ff;
          }
        }
        
        .week-desc-input {
          :deep(.el-textarea__inner) {
            font-size: 13px;
            padding: 10px;
            line-height: 1.5;
            resize: none;
          }
        }
      }
    }
  }
  
  .edit-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding-top: 20px;
    margin-top: 20px;
    border-top: 2px solid #f0f0f0;
    flex-shrink: 0;
  }
  
  // 占位提示样式
  .edit-placeholder {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 40px;
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
    border-radius: 12px;
    border: 2px dashed #c0c4cc;
    
    .placeholder-icon {
      width: 80px;
      height: 80px;
      background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 24px;
      box-shadow: 0 4px 20px rgba(24, 144, 255, 0.3);
      
      .el-icon {
        font-size: 40px;
        color: #fff;
      }
    }
    
    .placeholder-text {
      text-align: center;
      margin-bottom: 32px;
      
      h3 {
        font-size: 20px;
        font-weight: 600;
        color: #1f2f3d;
        margin: 0 0 8px 0;
      }
      
      p {
        font-size: 14px;
        color: #666;
        margin: 0;
      }
    }
    
    .placeholder-tips {
      display: flex;
      gap: 32px;
      
      @media (max-width: 768px) {
        flex-direction: column;
        gap: 12px;
      }
      
      .tip-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 20px;
        background: #fff;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        
        .el-icon {
          color: #52c41a;
          font-size: 18px;
        }
        
        span {
          font-size: 14px;
          color: #333;
        }
      }
    }
  }
}
</style>
