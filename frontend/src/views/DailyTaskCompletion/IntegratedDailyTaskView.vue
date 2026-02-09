<template>
  <div class="daily-task-completion-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <i class="el-icon-document-checked"></i>
          日清表 - {{ reportDate || '新建' }}
        </h1>
        <div class="report-meta">
          <el-tag v-if="reportId" type="success" size="small">日报ID: {{ reportId }}</el-tag>
          <el-tag v-else type="warning" size="small">待创建</el-tag>
        </div>
      </div>
      
      <div class="header-right">
        <el-button 
          v-if="reportId" 
          type="success" 
          size="large" 
          @click="handleSave" 
          :loading="saving"
        >
          <i class="el-icon-check"></i>
          保存
        </el-button>
        <el-button 
          v-if="reportId && !isSubmitted"
          type="primary" 
          size="large" 
          @click="handleSubmit" 
          :loading="saving"
          :disabled="!canSubmit"
        >
          <i class="el-icon-upload"></i>
          提交
        </el-button>
      </div>
    </div>

    <!-- 日期选择和快速操作 -->
    <div class="quick-actions">
      <div class="date-selector">
        <label>日报日期：</label>
        <el-date-picker
          v-model="selectedDate"
          type="date"
          placeholder="选择日报日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="handleDateChange"
          size="small"
          style="margin-left: 8px;"
        />
      </div>
      
      <div class="quick-add">
        <el-button 
          type="success" 
          size="small" 
          @click="addNewTask"
          plain
        >
          <i class="el-icon-plus"></i>
          添加任务
        </el-button>
        <el-button 
          type="warning" 
          size="small" 
          @click="loadMyTasks"
          plain
        >
          <i class="el-icon-refresh"></i>
          加载我的任务
        </el-button>
      </div>
    </div>

    <!-- 工作事项表格 -->
    <div class="task-table-section">
      <div class="table-header">
        <h3>
          <i class="el-icon-list"></i>
          工作事项清单
          <span class="table-summary">
            ({{ taskCompletions.length }} 项任务,
            <span class="hours-total">总计 {{ totalHours }} 小时</span>)
          </span>
        </h3>
      </div>
      
      <div class="table-container">
        <el-table 
          :data="taskCompletions" 
          border 
          style="width: 100%"
          :row-class-name="getRowClassName"
          class="daily-task-table"
          v-loading="loading"
        >
          <!-- 第一列：工作内容详情（内嵌关联任务） -->
          <el-table-column label="工作内容详情" min-width="800" align="left">
            <template #default="{ row, $index }">
              <div class="work-content-section">
                
                <!-- 第一行：关联任务信息 -->
                <div class="task-association-row">
                  <div class="task-selector-group">
                    <el-select 
                      v-model="row.project_id" 
                      placeholder="选择项目"
                      size="small"
                      style="width: 180px; margin-right: 8px;"
                      @change="(val) => handleProjectChange(val, $index)"
                    >
                      <el-option
                        v-for="project in projectOptions"
                        :key="project.project_id"
                        :label="project.project_name"
                        :value="project.project_id"
                      />
                    </el-select>
                    
                    <el-select 
                      v-model="row.task_id" 
                      placeholder="选择任务或输入自定义"
                      filterable
                      allow-create
                      default-first-option
                      size="small"
                      style="width: 200px; margin-right: 8px;"
                      @change="(val) => handleTaskChange(val, $index)"
                    >
                      <el-option
                        v-for="task in getTasksForProject(row.project_id)"
                        :key="task.task_id"
                        :label="task.task_name"
                        :value="task.task_id"
                      />
                    </el-select>
                    
                    <el-tag 
                      :type="row.task_source === 'my_tasks' ? 'primary' : 'info'"
                      size="small"
                    >
                      {{ row.task_source === 'my_tasks' ? '我的任务' : '自定义' }}
                    </el-tag>
                  </div>
                </div>

                <!-- 第二行：时间和工时 -->
                <div class="time-row">
                  <div class="time-inputs">
                    <el-time-picker
                      v-model="row.start_time"
                      placeholder="开始时间"
                      size="small"
                      style="width: 120px; margin-right: 8px;"
                      @change="() => updateTaskCompletion($index)"
                    />
                    <span class="time-separator">-</span>
                    <el-time-picker
                      v-model="row.end_time"
                      placeholder="结束时间"
                      size="small"
                      style="width: 120px; margin-left: 8px; margin-right: 8px;"
                      @change="() => updateTaskCompletion($index)"
                    />
                    <el-input-number
                      v-model="row.hours_spent"
                      :min="0"
                      :max="24"
                      :step="0.5"
                      size="small"
                      style="width: 100px;"
                      placeholder="小时数"
                      @change="() => updateTaskCompletion($index)"
                    />
                    <span class="unit">小时</span>
                  </div>
                </div>

                <!-- 第三行：工作内容 -->
                <div class="content-row">
                  <el-input
                    v-model="row.work_content"
                    type="textarea"
                    :rows="2"
                    placeholder="详细描述具体工作内容..."
                    size="small"
                    @input="() => debouncedUpdate($index)"
                  />
                </div>

                <!-- 第四行：进度和质量 -->
                <div class="progress-row">
                  <div class="progress-controls">
                    <!-- 进度百分比 -->
                    <div class="progress-group">
                      <label>进度：</label>
                      <el-progress
                        :percentage="row.progress_percentage || 0"
                        :stroke-width="8"
                        style="width: 100px;"
                      />
                      <el-input-number
                        v-model="row.progress_percentage"
                        :min="0"
                        :max="100"
                        :step="5"
                        size="small"
                        style="width: 70px; margin-left: 8px;"
                        @change="() => updateTaskCompletion($index)"
                      />
                      <span>%</span>
                    </div>

                    <!-- 进度状态 -->
                    <el-select 
                      v-model="row.progress_status" 
                      size="small"
                      style="width: 100px; margin-left: 8px;"
                      @change="() => updateTaskCompletion($index)"
                    >
                      <el-option label="正常" value="正常" />
                      <el-option label="延期" value="延期" />
                      <el-option label="提前" value="提前" />
                    </el-select>

                    <!-- 自评 -->
                    <el-select 
                      v-model="row.self_evaluation" 
                      placeholder="自评"
                      size="small"
                      style="width: 80px; margin-left: 8px;"
                      @change="() => updateTaskCompletion($index)"
                    >
                      <el-option label="A" value="A" />
                      <el-option label="B" value="B" />
                      <el-option label="C" value="C" />
                      <el-option label="D" value="D" />
                    </el-select>

                    <!-- 重点工作 -->
                    <el-checkbox 
                      v-model="row.is_key_work"
                      size="small"
                      style="margin-left: 8px;"
                      @change="() => updateTaskCompletion($index)"
                    >
                      重点工作
                    </el-checkbox>
                  </div>
                </div>

                <!-- 第五行：工作结果 -->
                <div class="result-row">
                  <el-input
                    v-model="row.result"
                    placeholder="工作结果（可选）..."
                    size="small"
                    @input="() => debouncedUpdate($index)"
                  />
                </div>
              </div>
            </template>
          </el-table-column>

          <!-- 第二列：操作 -->
          <el-table-column label="操作" width="120" align="center">
            <template #default="{ $index }">
              <div class="table-actions">
                <!-- 状态标签 -->
                <el-tag 
                  :type="getStatusType(taskCompletions[$index].status)"
                  size="small"
                  style="margin-bottom: 8px;"
                >
                  {{ taskCompletions[$index].status || '进行中' }}
                </el-tag>
                
                <!-- 操作按钮组 -->
                <div class="action-buttons">
                  <el-button 
                    type="text" 
                    size="small"
                    @click="duplicateTask($index)"
                    title="复制任务"
                  >
                    <i class="el-icon-copy-document"></i>
                  </el-button>
                  <el-button 
                    type="text" 
                    size="small"
                    @click="deleteTask($index)"
                    title="删除任务"
                    style="color: #f56c6c;"
                  >
                    <i class="el-icon-delete"></i>
                  </el-button>
                </div>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 底部统计 -->
    <div class="page-footer">
      <div class="task-summary">
        <div class="summary-item">
          <label>总任务数：</label>
          <span>{{ taskCompletions.length }}</span>
        </div>
        <div class="summary-item">
          <label>总工时：</label>
          <span>{{ totalHours }} 小时</span>
        </div>
        <div class="summary-item">
          <label>重点工作：</label>
          <span>{{ keyWorksCount }} 项</span>
        </div>
        <div class="summary-item">
          <label>平均进度：</label>
          <span>{{ averageProgress }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  createDailyTaskCompletion, 
  updateDailyTaskCompletion, 
  deleteDailyTaskCompletion,
  getTaskCompletionsByReport,
  getMyTasksAvailable 
} from '@/api/dailyTaskCompletion'

// Props
interface Props {
  reportId?: number
  employeeId?: string
}

const props = withDefaults(defineProps<Props>(), {
  employeeId: '1' // 默认用户ID
})

// 响应式数据
const selectedDate = ref('')
const reportId = ref<number | null>(null)
const taskCompletions = ref<any[]>([])
const saving = ref(false)
const loading = ref(false)

// 可用任务数据
const availableTasks = ref<any[]>([])
const projectOptions = computed(() => {
  // 获取所有唯一项目
  const projects = new Map()
  availableTasks.value.forEach(task => {
    if (!projects.has(task.project_id)) {
      projects.set(task.project_id, {
        project_id: task.project_id,
        project_name: task.project_name
      })
    }
  })
  return Array.from(projects.values())
})

// 计算属性
const totalHours = computed(() => {
  return taskCompletions.value.reduce((sum, task) => {
    return sum + (task.hours_spent || 0)
  }, 0).toFixed(1)
})

const keyWorksCount = computed(() => {
  return taskCompletions.value.filter(task => task.is_key_work).length
})

const averageProgress = computed(() => {
  const totalProgress = taskCompletions.value.reduce((sum, task) => {
    return sum + (task.progress_percentage || 0)
  }, 0)
  return taskCompletions.value.length > 0 
    ? Math.round(totalProgress / taskCompletions.value.length) 
    : 0
})

const canSubmit = computed(() => {
  return taskCompletions.value.length > 0 && 
         taskCompletions.value.some(task => task.work_content && task.work_content.trim())
})

const isSubmitted = computed(() => {
  return false // TODO: 根据实际状态判断
})

// 方法
const getTasksForProject = (projectId: string) => {
  return availableTasks.value.filter(task => task.project_id === projectId)
}

const getRowClassName = ({ row }: any) => {
  return row.is_key_work ? 'key-work-row' : ''
}

const getStatusType = (status: string) => {
  switch (status) {
    case '已完成': return 'success'
    case '进行中': return 'warning'
    case '暂停': return 'info'
    case '取消': return 'danger'
    default: return 'info'
  }
}

const loadMyTasks = async () => {
  try {
    loading.value = true
    const response = await getMyTasksAvailable()
    availableTasks.value = response.items || []
    ElMessage.success(`加载了 ${availableTasks.value.length} 个任务`)
  } catch (error) {
    console.error('加载任务失败:', error)
    ElMessage.error('加载任务失败')
  } finally {
    loading.value = false
  }
}

const addNewTask = () => {
  const newTask = {
    id: null,
    report_id: reportId.value,
    project_id: null,
    project_name: null,
    task_id: null,
    task_name: null,
    task_source: 'custom',
    start_time: null,
    end_time: null,
    hours_spent: 0,
    progress_percentage: 0,
    progress_status: '正常',
    work_content: '',
    result: '',
    self_evaluation: null,
    status: '进行中',
    is_key_work: false,
    create_time: null,
    update_time: null
  }
  
  taskCompletions.value.push(newTask)
}

const handleProjectChange = (projectId: string, index: number) => {
  const project = projectOptions.value.find(p => p.project_id === projectId)
  if (project) {
    taskCompletions.value[index].project_name = project.project_name
  }
  updateTaskCompletion(index)
}

const handleTaskChange = (taskId: string, index: number) => {
  const task = availableTasks.value.find(t => t.task_id === taskId)
  if (task) {
    taskCompletions.value[index].task_name = task.task_name
    if (!taskCompletions.value[index].project_id) {
      taskCompletions.value[index].project_id = task.project_id
      taskCompletions.value[index].project_name = task.project_name
    }
    taskCompletions.value[index].task_source = 'my_tasks'
  }
  updateTaskCompletion(index)
}

const debounce = (fn: Function, delay: number) => {
  let timeout: NodeJS.Timeout
  return (...args: any[]) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => fn(...args), delay)
  }
}

const debouncedUpdate = debounce((index: number) => {
  updateTaskCompletion(index)
}, 1000)

const updateTaskCompletion = async (index: number) => {
  if (!reportId.value) return
  
  const task = taskCompletions.value[index]
  try {
    if (task.id) {
      // 更新现有任务
      await updateDailyTaskCompletion(task.id, task)
    } else {
      // 创建新任务
      const response = await createDailyTaskCompletion(task)
      taskCompletions.value[index] = { ...task, ...response }
      if (!reportId.value && response.report_id) {
        reportId.value = response.report_id
      }
    }
  } catch (error) {
    console.error('更新任务失败:', error)
    ElMessage.error('保存任务失败')
  }
}

const deleteTask = async (index: number) => {
  const task = taskCompletions.value[index]
  
  try {
    if (task.id) {
      await deleteDailyTaskCompletion(task.id)
      ElMessage.success('删除成功')
    }
    taskCompletions.value.splice(index, 1)
  } catch (error) {
    console.error('删除任务失败:', error)
    ElMessage.error('删除失败')
  }
}

const duplicateTask = (index: number) => {
  const originalTask = taskCompletions.value[index]
  const duplicatedTask = {
    ...originalTask,
    id: null,
    create_time: null,
    update_time: null
  }
  taskCompletions.value.splice(index + 1, 0, duplicatedTask)
  ElMessage.success('任务复制成功')
}

const handleSave = async () => {
  try {
    saving.value = true
    // 保存所有任务
    for (let i = 0; i < taskCompletions.value.length; i++) {
      await updateTaskCompletion(i)
    }
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleSubmit = async () => {
  try {
    if (!canSubmit.value) {
      ElMessage.warning('请至少填写一个工作内容')
      return
    }
    
    saving.value = true
    // TODO: 调用提交API
    ElMessage.success('提交成功')
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败')
  } finally {
    saving.value = false
  }
}

const handleDateChange = (date: string) => {
  if (date) {
    loadReportData(date)
  }
}

const loadReportData = async (date: string) => {
  if (!date) return
  
  try {
    loading.value = true
    // TODO: 根据日期加载已有的日报数据
    // const response = await getDailyReportByDate(date, props.employeeId)
    // reportId.value = response.id
  } catch (error) {
    console.error('加载日报数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  selectedDate.value = new Date().toISOString().split('T')[0]
  loadMyTasks()
})
</script>

<style scoped>
.daily-task-completion-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  margin: 0;
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
}

.page-title i {
  margin-right: 8px;
  color: #409eff;
}

.report-meta {
  display: flex;
  gap: 8px;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* 快速操作 */
.quick-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.date-selector {
  display: flex;
  align-items: center;
  font-weight: 500;
}

.quick-add {
  display: flex;
  gap: 8px;
}

/* 任务表格 */
.task-table-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.table-header {
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
  background: #fafafa;
}

.table-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.table-header i {
  margin-right: 8px;
  color: #409eff;
}

.table-summary {
  margin-left: 12px;
  font-size: 14px;
  color: #666;
  font-weight: normal;
}

.hours-total {
  color: #e6a23c;
  font-weight: 600;
}

.table-container {
  padding: 0 20px 20px;
}

/* 工作内容部分 */
.work-content-section {
  padding: 16px 0;
}

/* 关联任务行 */
.task-association-row {
  margin-bottom: 12px;
}

.task-selector-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 时间行 */
.time-row {
  margin-bottom: 12px;
}

.time-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-separator {
  color: #666;
  font-weight: 500;
}

.unit {
  color: #666;
  font-size: 12px;
  margin-left: 4px;
}

/* 内容行 */
.content-row {
  margin-bottom: 12px;
}

/* 进度行 */
.progress-row {
  margin-bottom: 12px;
}

.progress-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.progress-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 结果行 */
.result-row {
  margin-bottom: 8px;
}

/* 表格操作 */
.table-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.action-buttons {
  display: flex;
  gap: 4px;
}

/* 重点工作行样式 */
:deep(.key-work-row) {
  background-color: #fff3cd !important;
}

:deep(.key-work-row:hover) {
  background-color: #ffeaa7 !important;
}

/* 页面底部 */
.page-footer {
  margin-top: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.task-summary {
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.summary-item label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.summary-item span {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .task-summary {
    flex-wrap: wrap;
    gap: 16px;
  }
  
  .progress-controls {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .task-selector-group {
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .daily-task-completion-container {
    padding: 10px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .quick-actions {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .date-selector {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .time-inputs {
    flex-wrap: wrap;
  }
  
  .work-content-section {
    padding: 12px 0;
  }
}
</style>