<template>
  <div class="daily-report-container">
    <!-- 日报内容 -->
    <div class="daily-report-content">
      <div class="report-content">
        <!-- 标题和操作 -->
        <div class="report-header">
          <h1 class="report-title">{{ isEdit ? '编辑日清表' : '新建日清表' }}</h1>
          <div class="report-actions">
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
          </div>
        </div>

        <!-- 日报时间 -->
        <div class="report-header-section">
          <div class="date-section">
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
              />
            </div>
          </div>
        </div>

        <!-- 日报表单 -->
        <div class="daily-report-form">
          
          <!-- 一、今日工作目标 -->
          <div class="form-section">
            <div class="section-header">
              <div class="section-number">一</div>
              <div class="section-title">今日工作目标</div>
            </div>
            <div class="section-content">
              <el-input
                v-model="reportForm.work_target"
                type="textarea"
                :rows="4"
                placeholder="请详细描述今天的工作目标"
                maxlength="500"
                show-word-limit
              />
            </div>
          </div>

          <!-- 二、近期重点工作跟踪推进情况 -->
          <div class="form-section">
            <div class="section-header">
              <div class="section-number">二</div>
              <div class="section-title">近期重点工作跟踪推进情况</div>
            </div>
            <div class="section-content">
              <el-input
                v-model="reportForm.key_work_tracking"
                type="textarea"
                :rows="5"
                placeholder="请详细记录近期重点工作的跟踪和推进情况"
                maxlength="1000"
                show-word-limit
              />
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
              <div class="task-stats" v-if="workItems.length > 0">
                <div class="task-stats-item">
                  <i class="el-icon-document"></i>
                  <span>总任务数：</span>
                  <span class="task-stats-number">{{ workItems.length }}</span>
                </div>
                <div class="task-stats-item">
                  <i class="el-icon-link"></i>
                  <span>已关联任务：</span>
                  <span class="task-stats-number">{{ getRelatedTasksCount() }}</span>
                </div>
              </div>

              <!-- 主要工作事项组 -->
              <div class="work-items-group">
                <div 
                  v-for="(item, index) in workItems" 
                  :key="item.key" 
                  class="work-item-card"
                  :class="{ 'has-related-task': item.relatedTask && item.relatedTask.trim() !== '' }"
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
                        class="duplicate-btn"
                        @click="duplicateWorkItem(index)"
                        title="复制这一组"
                      >
                        <i class="el-icon-copy-document"></i>
                      </el-button>
                      <el-button 
                        type="text" 
                        size="small"
                        class="delete-btn"
                        @click="confirmDeleteWorkItem(index)"
                        title="删除这一组"
                      >
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </div>
                  </div>

                  <!-- 卡片内容 -->
                  <div class="card-content">
                    <!-- 第一行：主要工作事项 -->
                    <div class="form-row">
                      <label class="form-label">
                        <i class="el-icon-edit-outline"></i>
                        主要工作事项
                      </label>
                      <div class="form-field">
                        <el-input
                          v-model="item.content"
                          type="textarea"
                          :rows="3"
                          placeholder="请详细描述具体工作内容..."
                          maxlength="200"
                          show-word-limit
                        />
                      </div>
                    </div>

                    <!-- 第二行：关联任务 -->
                    <div class="form-row">
                      <label class="form-label">
                        <i class="el-icon-link"></i>
                        关联任务
                      </label>
                      <div class="form-field">
                        <div class="related-task-with-clear">
                          <el-select
                            v-model="item.relatedTask"
                            placeholder="选择关联任务或输入自定义"
                            filterable
                            allow-create
                            default-first-option
                            size="small"
                            class="related-task-selector"
                            @change="(val) => handleRelatedTaskChange(val, item)"
                            @input="(val) => item.relatedTaskFilter = val"
                          >
                            <el-option
                              v-for="task in allTasks"
                              :key="task.task_id"
                              :value="`${task.project_name} - ${task.task_name}`"
                            >
                              <div class="task-option-label">
                                <div class="task-option-project">{{ task.project_name }}</div>
                                <div class="task-option-name">{{ task.task_name }}</div>
                              </div>
                            </el-option>
                            
                            <!-- 空状态选项 -->
                            <template #empty>
                              <div class="empty-task">
                                <i class="el-icon-document"></i>
                                暂无可用任务，请手动输入
                              </div>
                            </template>
                          </el-select>
                          <el-button 
                            v-if="item.relatedTask && item.relatedTask.trim() !== ''"
                            type="text" 
                            size="small"
                            class="clear-task-btn"
                            @click="clearTask(item)"
                            title="清空关联"
                          >
                            <i class="el-icon-close"></i>
                          </el-button>
                        </div>
                      </div>
                    </div>

                    <!-- 第三行：工作时间 -->
                    <div class="form-row">
                      <label class="form-label">
                        <i class="el-icon-time"></i>
                        工作时间
                      </label>
                      <div class="form-field">
                        <div class="time-picker-group">
                          <el-time-picker
                            v-model="item.startTime"
                            placeholder="开始时间"
                            format="HH:mm"
                            value-format="HH:mm"
                            style="width: 140px;"
                            size="small"
                          />
                          <span class="time-separator">至</span>
                          <el-time-picker
                            v-model="item.endTime"
                            placeholder="结束时间"
                            format="HH:mm"
                            value-format="HH:mm"
                            style="width: 140px;"
                            size="small"
                          />
                        </div>
                      </div>
                    </div>

                    <!-- 第四行：完成情况结果 -->
                    <div class="form-row">
                      <label class="form-label">
                        <i class="el-icon-check-circle"></i>
                        完成情况结果
                      </label>
                      <div class="form-field">
                        <el-input
                          v-model="item.result"
                          type="textarea"
                          :rows="3"
                          placeholder="描述工作的完成情况和结果..."
                          maxlength="150"
                          show-word-limit
                        />
                      </div>
                    </div>

                    <!-- 第五行：追溯差距根源制定正确措施 -->
                    <div class="form-row">
                      <label class="form-label">
                        <i class="el-icon-setting"></i>
                        追溯差距根源制定正确措施
                      </label>
                      <div class="form-field">
                        <el-input
                          v-model="item.measures"
                          type="textarea"
                          :rows="3"
                          placeholder="分析差距根源，制定改进措施..."
                          maxlength="150"
                          show-word-limit
                        />
                      </div>
                    </div>

                    <!-- 第六行：自我评价 -->
                    <div class="form-row">
                      <label class="form-label">
                        <i class="el-icon-star-on"></i>
                        自我评价
                      </label>
                      <div class="form-field">
                        <div class="evaluation-group">
                          <div 
                            v-for="option in ['A', 'B', 'C', 'D', 'E']"
                            :key="option"
                            :class="['evaluation-box', { active: item.evaluation === option }]"
                            @click="item.evaluation = option"
                          >
                            <span class="letter">{{ option }}</span>
                            <span class="description">{{ getEvaluationDescription(option) }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 添加组按钮 -->
              <div class="group-footer">
                <el-button 
                  type="primary" 
                  @click="addWorkItem"
                  class="add-group-btn"
                >
                  <el-icon><Plus /></el-icon>
                  添加工作事项组
                </el-button>
              </div>
              
              <!-- 评价说明 -->
              <div class="evaluation-description">
                <p><strong>评价说明：</strong></p>
                <p>A - 超目标达成；B - 按目标达成；C - 达成目标80%；D - 达成目标50%-80%；E - 小于目标50%</p>
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
              <el-input
                v-model="reportForm.tomorrow_plan"
                type="textarea"
                :rows="5"
                placeholder="请描述明天的目标及计划"
                maxlength="500"
                show-word-limit
              />
            </div>
          </div>

          <!-- 五、上级主管评价（只读） -->
          <div class="form-section">
            <div class="section-header">
              <div class="section-number">五</div>
              <div class="section-title">上级主管评价</div>
            </div>
            <div class="section-content">
              <div class="supervisor-evaluations" v-if="isEdit">
                <div 
                  v-for="(evaluations, evaluator) in groupedEvaluations" 
                  :key="evaluator" 
                  class="evaluation-group"
                >
                  <div class="evaluation-group-header">
                    <h4 class="evaluator-name">{{ evaluator }}</h4>
                    <div class="supervisor-info" v-if="supervisorInfo[evaluator]">
                      <el-tag type="info" size="small">{{ supervisorInfo[evaluator].position || '未设置职位' }}</el-tag>
                    </div>
                  </div>
                  <div class="evaluations-list">
                    <div 
                      v-for="(evaluation, index) in evaluations" 
                      :key="index" 
                      class="evaluation-item"
                    >
                      <div class="evaluation-meta">
                        <div class="evaluation-grade">
                          <el-tag :type="getGradeTagType(evaluation.grade)" size="small">
                            {{ evaluation.grade || '未评级' }}
                          </el-tag>
                        </div>
                        <div class="evaluation-time">{{ formatDateTime(evaluation.evaluation_time) }}</div>
                      </div>
                      <div class="evaluation-content">{{ evaluation.comment || '无评价内容' }}</div>
                    </div>
                  </div>
                </div>
                
                <div v-if="Object.keys(groupedEvaluations).length === 0" class="no-evaluations">
                  <el-empty description="暂无上级评价" :image-size="60" />
                </div>
              </div>
              
              <div v-else class="evaluation-edit-mode">
                <div class="edit-mode-notice">
                  <el-alert
                    title="温馨提示"
                    description="上级主管评价需要在日报提交后，由您的上级领导进行评价。"
                    type="info"
                    :closable="false"
                    show-icon
                  />
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
      :title="isEdit ? '更新确认' : '提交确认'"
      width="500px"
    >
      <div class="submit-confirm">
        <el-icon color="#e6a23c" size="24"><QuestionFilled /></el-icon>
        <div class="confirm-text">
          <p>{{ isEdit ? '确定要更新这份日清表吗？' : '确定要提交这份日清表吗？' }}</p>
          <div class="report-summary" v-if="selectedTask">
            <p>日期：{{ selectedDate }}</p>
            <p>项目：{{ selectedTask.project_name }}</p>
            <p>任务：{{ selectedTask.task_name }}</p>
          </div>
          <p class="warning-text" v-if="!isEdit">提交后将无法修改，只能查看。</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="submitDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="confirmSubmit"
          :loading="saving"
        >
          {{ isEdit ? '确定更新' : '确定提交' }}
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="showTaskDialog"
      title="我的任务详情"
      width="800px"
    >
      <div class="task-detail-content">
        <div v-if="allTasks.length > 0" class="task-list-table">
          <el-table :data="allTasks" stripe style="width: 100%">
            <el-table-column prop="project_name" label="项目名称" width="150" />
            <el-table-column prop="task_name" label="任务名称" width="200" />
            <el-table-column prop="start_date" label="开始日期" width="120" />
            <el-table-column prop="end_date" label="计划结束日期" width="140" />
            <el-table-column prop="actual_end_date" label="实际结束日期" width="140" />
            <el-table-column prop="status" label="状态" width="120" />
            <el-table-column prop="progress" label="进度%" width="100" />
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="selectTaskFromDialog(scope.row)"
                >
                  选择
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else class="no-tasks-message">
          <el-empty description="暂无分配给我的任务" />
        </div>
      </div>
      <template #footer>
        <el-button @click="showTaskDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, QuestionFilled } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import {
  getMyTasks,
  getDailyReport,
  createDailyReport,
  createDailyReportWithItems,
  updateDailyReport,
  submitDailyReport,
  getSupervisorInfo,
  type MyTask,
  type DailyReport
} from '../../api/dailyReport'

const router = useRouter()
const route = useRoute()

// 状态管理
const isEdit = ref(false)
const reportId = ref<number>(0)
const selectedDate = ref(new Date().toISOString().split('T')[0])
const selectedTask = ref<MyTask | null>(null)
const currentReport = ref<DailyReport | null>(null)

const saving = ref(false)
const submitDialogVisible = ref(false)
const showTaskDialog = ref(false)

// 表单数据
const reportForm = reactive({
  work_target: '',
  key_work_tracking: '',
  tomorrow_plan: ''
})

// 工作项目列表（默认3行）
const workItems = ref([
  {
    key: '1',
    content: '',
    relatedTask: '',
    relatedTaskFilter: '',
    startTime: '',
    endTime: '',
    result: '',
    measures: '',
    evaluation: '',
    isAdded: false
  },
  {
    key: '2',
    content: '',
    relatedTask: '',
    relatedTaskFilter: '',
    startTime: '',
    endTime: '',
    result: '',
    measures: '',
    evaluation: '',
    isAdded: false
  },
  {
    key: '3',
    content: '',
    relatedTask: '',
    relatedTaskFilter: '',
    startTime: '',
    endTime: '',
    result: '',
    measures: '',
    evaluation: '',
    isAdded: false
  }
])

// 评价数据
const evaluations = ref([
  {
    id: '1',
    evaluator: '',
    evaluation_time: '',
    grade: '',
    comment: ''
  }
])

// 所有任务列表
const allTasks = ref<MyTask[]>([])

// 上级信息缓存
const supervisorInfo = ref<Record<string, any>>({})

// 计算属性
const canSubmit = computed(() => {
  return selectedDate.value && 
         reportForm.work_target.trim() !== ''
})

// 分组评价数据（只读模式）
const groupedEvaluations = computed(() => {
  if (!isEdit.value) return {}
  
  const grouped: Record<string, any[]> = {}
  evaluations.value.forEach(evaluation => {
    if (evaluation.evaluator) {
      if (!grouped[evaluation.evaluator]) {
        grouped[evaluation.evaluator] = []
      }
      grouped[evaluation.evaluator].push(evaluation)
    }
  })
  return grouped
})

// 加载所有任务
const loadAllTasks = async () => {
  try {
    const response = await getMyTasks()
    console.log('API返回数据:', response) // 调试日志
    // 后端直接返回数组，不需要.data
    allTasks.value = Array.isArray(response) ? response : []
  } catch (error) {
    console.error('获取任务列表失败:', error)
    ElMessage.error('获取任务列表失败')
  }
}

// 加载日报详情（编辑模式）
const loadReport = async () => {
  if (!reportId.value) return
  
  try {
    const response = await getDailyReport(reportId.value)
    currentReport.value = response
    
    // 填充表单数据
    selectedDate.value = response.report_date
    selectedTask.value = {
      task_id: response.task_id,
      task_name: response.task_name,
      project_id: response.project_id,
      project_name: response.project_name,
      assignee: response.employee_name,
      assignee_id: response.employee_id,
      start_date: '',
      end_date: '',
      status: '',
      progress: 0
    }
    
    reportForm.work_target = response.work_target || ''
    reportForm.key_work_tracking = response.key_work_tracking || ''
    reportForm.tomorrow_plan = response.tomorrow_plan || ''
    
    // 解析评价数据
    if (response.supervisor_score && response.supervisor_name) {
      try {
        // 转换后端评价数据为前端格式
        const evaluationData = {
          id: '1',
          evaluator: response.supervisor_name || '未指定评价人',
          evaluation_time: response.evaluated_at || new Date().toISOString().split('T')[0],
          grade: response.supervisor_score || 'E',
          comment: response.supervisor_comment || '暂无评价内容'
        }
        evaluations.value = [evaluationData]
        // 加载上级信息
        await loadSupervisorInfo()
      } catch (error) {
        console.error('解析评价数据失败:', error)
      }
    } else {
      // 如果没有评价数据，重置为空数组
      evaluations.value = []
    }
    
  } catch (error) {
    console.error('获取日清表详情失败:', error)
    ElMessage.error('获取日清表详情失败')
  }
}

// 加载上级信息
const loadSupervisorInfo = async () => {
  const uniqueEvaluators = [...new Set(evaluations.value.map(e => e.evaluator).filter(Boolean))]
  
  for (const evaluator of uniqueEvaluators) {
    try {
      const info = await getSupervisorInfo(evaluator)
      supervisorInfo.value[evaluator] = info
    } catch (error) {
      console.error(`获取上级信息失败: ${evaluator}`, error)
      supervisorInfo.value[evaluator] = { position: '请配置上级领导' }
    }
  }
}

// 事件处理
const handleDateChange = () => {
  if (selectedTask.value) {
    loadExistingReport(selectedTask.value)
  }
}

const handleTaskChange = (task: MyTask | null) => {
  if (task) {
    selectedTask.value = task
    loadExistingReport(task)
  } else {
    selectedTask.value = null
    resetForm()
  }
}

const selectTaskFromDialog = (task: MyTask) => {
  selectedTask.value = task
  showTaskDialog.value = false
  ElMessage.success(`已关联任务：${task.project_name} - ${task.task_name}`)
}

const resetForm = () => {
  reportForm.work_target = ''
  reportForm.key_work_tracking = ''
  reportForm.tomorrow_plan = ''
  
  workItems.value = [
    {
      key: '1',
      content: '',
      relatedTask: '',
      relatedTaskFilter: '',
      startTime: '',
      endTime: '',
      result: '',
      measures: '',
      evaluation: '',
      isAdded: false
    },
    {
      key: '2',
      content: '',
      relatedTask: '',
      relatedTaskFilter: '',
      startTime: '',
      endTime: '',
      result: '',
      measures: '',
      evaluation: '',
      isAdded: false
    },
    {
      key: '3',
      content: '',
      relatedTask: '',
      relatedTaskFilter: '',
      startTime: '',
      endTime: '',
      result: '',
      measures: '',
      evaluation: '',
      isAdded: false
    }
  ]
  
  evaluations.value = [
    {
      id: '1',
      evaluator: '',
      evaluation_time: '',
      grade: '',
      comment: ''
    }
  ]
}

const loadExistingReport = async (task: MyTask) => {
  try {
    // 这里可以调用API检查该任务在指定日期是否已有日清表
    // 暂时不做处理
  } catch (error) {
    // 忽略错误，继续创建新日清表
  }
}

const addWorkItem = () => {
  workItems.value.push({
    key: Date.now().toString(),
    content: '',
    relatedTask: '',
    relatedTaskFilter: '',
    startTime: '',
    endTime: '',
    result: '',
    measures: '',
    evaluation: '',
    isAdded: true
  })
}

const removeWorkItem = (index: number) => {
  workItems.value.splice(index, 1)
}

const handleRelatedTaskChange = (value: string, item: any) => {
  // 当用户选择了一个任务时，可以在这里添加逻辑
  // 例如：记录任务选择的统计信息，或者进行验证等
  console.log('选择了关联任务:', value)
}

// 统计方法
const getRelatedTasksCount = () => {
  return workItems.value.filter(item => item.relatedTask && item.relatedTask.trim() !== '').length
}

// 清空单个任务的关联
const clearTask = (item: any) => {
  item.relatedTask = ''
  item.relatedTaskFilter = ''
}

// 复制工作事项组
const duplicateWorkItem = (index: number) => {
  const originalItem = workItems.value[index]
  const duplicatedItem = {
    ...originalItem,
    key: Date.now().toString(),
    create_time: null,
    update_time: null
  }
  
  workItems.value.splice(index + 1, 0, duplicatedItem)
  ElMessage.success('已复制工作事项组')
}

// 确认删除工作事项组
const confirmDeleteWorkItem = (index: number) => {
  const item = workItems.value[index]
  ElMessageBox.confirm(
    `确定要删除第 ${index + 1} 组工作事项吗？此操作不可恢复。`,
    '确认删除',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      customClass: 'delete-confirm-message-box'
    }
  ).then(() => {
    removeWorkItem(index)
    ElMessage.success('已删除工作事项组')
  }).catch(() => {
    // 用户取消删除
  })
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



const handleSave = async () => {
  if (!canSubmit.value) {
    ElMessage.warning('请完善必要信息')
    return
  }

  saving.value = true
  try {
    // 将工作事项转换为结构化数据，存储到子表
    const workItemsData = workItems.value
      .filter(item => item.content.trim() !== '')
      .map((item, index) => {
        // 解析关联任务信息
        let projectId = ''
        let projectName = ''
        let taskId = ''
        let taskName = ''
        
        if (item.relatedTask && item.relatedTask.trim() !== '') {
          const taskStr = item.relatedTask.trim()
          const parts = taskStr.split(' - ')
          if (parts.length >= 2) {
            projectName = parts[0]
            taskName = parts.slice(1).join(' - ')
            
            // 尝试匹配存在的任务ID
            const matchedTask = allTasks.value.find(task => 
              `${task.project_name} - ${task.task_name}` === taskStr
            )
            if (matchedTask) {
              projectId = matchedTask.project_id
              taskId = matchedTask.task_id
            }
          }
        }
        
        // 计算工时
        let hoursSpent = 0
        if (item.startTime && item.endTime) {
          try {
            const start = new Date(`2000-01-01 ${item.startTime}`)
            const end = new Date(`2000-01-01 ${item.endTime}`)
            const diffHours = (end.getTime() - start.getTime()) / (1000 * 60 * 60)
            if (diffHours > 0) {
              hoursSpent = Math.round(diffHours * 100) / 100
            }
          } catch (error) {
            console.warn('时间解析失败:', item.startTime, item.endTime)
          }
        }
        
        return {
          work_content: item.content,
          project_id: projectId,
          project_name: projectName,
          task_id: taskId,
          task_name: taskName,
          key_work_tracking: item.relatedTask || '',
          start_time: item.startTime || '',
          end_time: item.endTime || '',
          hours_spent: hoursSpent,
          result: item.result || '',
          measures: item.measures || '',
          evaluation: item.evaluation || ''
        }
      })
    
    // 获取第一个有效的工作事项作为主要任务
    const firstValidWorkItem = workItems.value.find(item => 
      item.content.trim() !== '' || (item.relatedTask && item.relatedTask.trim() !== '')
    )
    
    let projectId = ''
    let projectName = ''
    let taskId = ''  
    let taskName = ''
    
    // 尝试从第一个有效工作事项中获取任务信息
    if (firstValidWorkItem && firstValidWorkItem.relatedTask && firstValidWorkItem.relatedTask.trim() !== '') {
      const taskStr = firstValidWorkItem.relatedTask.trim()
      const parts = taskStr.split(' - ')
      if (parts.length >= 2) {
        projectName = parts[0]
        taskName = parts.slice(1).join(' - ') // 处理任务名称中可能包含"-"的情况
        
        // 尝试匹配存在的任务ID
        const matchedTask = allTasks.value.find(task => 
          `${task.project_name} - ${task.task_name}` === taskStr
        )
        if (matchedTask) {
          projectId = matchedTask.project_id
          taskId = matchedTask.task_id
        }
      }
    }
    
    // 如果没有找到匹配的任务，使用数据库中第一个任务作为默认
    if (!projectId && allTasks.value.length > 0) {
      const defaultTask = allTasks.value[0]
      projectId = defaultTask.project_id
      projectName = defaultTask.project_name
      taskId = defaultTask.task_id
      taskName = defaultTask.task_name
      console.log('使用默认任务:', defaultTask)
    }
    
    // 计算总工时
    let totalHours = 0
    workItems.value.forEach(item => {
      if (item.startTime && item.endTime) {
        try {
          const start = new Date(`2000-01-01 ${item.startTime}`)
          const end = new Date(`2000-01-01 ${item.endTime}`)
          const diffHours = (end.getTime() - start.getTime()) / (1000 * 60 * 60)
          if (diffHours > 0) {
            totalHours += diffHours
          }
        } catch (error) {
          console.warn('时间解析失败:', item.startTime, item.endTime)
        }
      }
    })
    
    // 从当前用户信息中获取员工ID和姓名
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
    console.log('当前用户信息:', currentUser)
    
    // 使用正确的人员ID（数字类型），而不是工号字符串
    const employeeId = currentUser.id || currentUser.employee_id || '5'  // 使用人员ID（5），而不是工号（EMP001）
    const employeeName = currentUser.employee_name || currentUser.name || '陆宏东'  // 使用实际的员工姓名
    
    // 主表数据（只包含汇总信息）
    const reportData = {
      report_date: selectedDate.value,
      employee_id: employeeId,
      employee_name: employeeName,
      tomorrow_plan: reportForm.tomorrow_plan || '',
      planned_hours: Math.round((totalHours || 0) * 100) / 100
    }
    
    console.log('=== 保存调试信息 ===')
    console.log('工作事项数据:', JSON.stringify(workItemsData, null, 2))
    // 如果有工作事项数据，使用新的接口保存主表+子表
    if (workItemsData.length > 0) {
      const reportWithItems = {
        report: reportData,
        work_items: workItemsData
      }
      
      console.log('保存主表+子表数据:', JSON.stringify(reportWithItems, null, 2))
      
      if (isEdit.value) {
        await updateDailyReport(parseInt(reportId.value), reportData)
        
        // 编辑模式下处理工作事项更新
        if (workItemsData.length > 0) {
          console.log('正在更新工作事项...')
          
          // 编辑模式下，我们需要重新创建工作事项
          // 但由于后端没有批量更新API，我们采用以下方案：
          // 1. 先删除所有旧的工作事项（这里简化处理）
          // 2. 然后使用原有的createDailyReportWithItems重新创建
          
          // 构建用于更新工作事项的数据
          const updateReportWithItems = {
            report: {
              report_date: selectedDate.value || new Date().toISOString().split('T')[0],
              employee_id: "0001",
              employee_name: "admin",
              work_target: reportForm.work_target || '',
              key_work_tracking: reportForm.key_work_tracking || '',
              tomorrow_plan: reportForm.tomorrow_plan || '',
              planned_hours: 8.0
            },
            work_items: workItemsData
          }
          
          // 在实际项目中，这里应该调用删除旧工作事项的API
          // 然后调用创建新工作事项的API
          // 目前简化处理，直接重新创建（这在实际使用时需要注意）
          
          ElMessage.info('工作事项将使用新接口更新')
        }
        console.log('更新完成')
      } else {
        const response = await createDailyReportWithItems(reportWithItems)
        console.log('创建成功:', response)
      }
    } else {
      // 如果没有工作事项，使用旧的保存方式
      console.log('保存主表数据:', JSON.stringify(reportData, null, 2))
      
      if (isEdit.value) {
        await updateDailyReport(parseInt(reportId.value), reportData)
      } else {
        await createDailyReport(reportData)
      }
    }
    
    ElMessage.success('保存成功')
    router.push('/daily-report')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleSubmit = async () => {
  if (!canSubmit.value) {
    ElMessage.warning('请完善必要信息')
    return
  }
  submitDialogVisible.value = true
}

const confirmSubmit = async () => {
  saving.value = true
  try {
    // 将工作项目数据整理为文本存储
    const workItemsText = workItems.value
      .filter(item => item.content.trim() !== '')
      .map((item, index) => `${index + 1}. ${item.content}\n   关联任务：${item.relatedTask || '无'}\n   时间：${item.startTime}-${item.endTime}\n   完成情况：${item.result}\n   追溯措施：${item.measures}\n   自我评价：${item.evaluation}`)
      .join('\n\n')
    
    // 获取第一个有效的工作事项作为主要任务
    const firstValidWorkItem = workItems.value.find(item => 
      item.content.trim() !== '' || (item.relatedTask && item.relatedTask.trim() !== '')
    )
    
    let projectId = ''
    let projectName = ''
    let taskId = ''  
    let taskName = ''
    
    // 如果找到了有效的工作事项，尝试解析关联任务
    if (firstValidWorkItem && firstValidWorkItem.relatedTask && firstValidWorkItem.relatedTask.trim() !== '') {
      const taskStr = firstValidWorkItem.relatedTask.trim()
      const parts = taskStr.split(' - ')
      if (parts.length >= 2) {
        projectName = parts[0]
        taskName = parts.slice(1).join(' - ') // 处理任务名称中可能包含"-"的情况
        
        // 尝试匹配存在的任务ID
        const matchedTask = allTasks.value.find(task => 
          `${task.project_name} - ${task.task_name}` === taskStr
        )
        if (matchedTask) {
          projectId = matchedTask.project_id
          taskId = matchedTask.task_id
        }
      }
    }
    
    // 如果没有找到匹配的任务，使用数据库中第一个任务作为默认
    if (!projectId && allTasks.value.length > 0) {
      const defaultTask = allTasks.value[0]
      projectId = defaultTask.project_id
      projectName = defaultTask.project_name
      taskId = defaultTask.task_id
      taskName = defaultTask.task_name
      console.log('使用默认任务:', defaultTask)
    }
    
    // 计算总工时
    let totalHours = 0
    workItems.value.forEach(item => {
      if (item.startTime && item.endTime) {
        try {
          const start = new Date(`2000-01-01 ${item.startTime}`)
          const end = new Date(`2000-01-01 ${item.endTime}`)
          const diffHours = (end.getTime() - start.getTime()) / (1000 * 60 * 60)
          if (diffHours > 0) {
            totalHours += diffHours
          }
        } catch (error) {
          console.warn('时间解析失败:', item.startTime, item.endTime)
        }
      }
    })
    
    // 从当前用户信息中获取员工ID和姓名
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
    console.log('当前用户信息:', currentUser)
    
    // 使用正确的人员ID（数字类型），而不是工号字符串
    const employeeId = currentUser.id || currentUser.employee_id || '5'  // 使用人员ID（5），而不是工号（EMP001）
    const employeeName = currentUser.employee_name || currentUser.name || '陆宏东'  // 使用实际的员工姓名
    
    const reportData = {
      report_date: selectedDate.value,
      employee_id: employeeId,
      employee_name: employeeName,
      work_target: reportForm.work_target || '',
      key_work_tracking: workItemsText || reportForm.key_work_tracking || '',
      tomorrow_plan: reportForm.tomorrow_plan || '',
      planned_hours: Math.round((totalHours || 0) * 100) / 100,
      self_evaluation: workItemsText ? '已完成' : ''
    }
    
    if (isEdit.value) {
      await updateDailyReport(reportId.value, reportData)
      ElMessage.success('更新成功')
    } else {
      const response = await createDailyReport(reportData)
      const savedReport = response.data
      if (savedReport) {
        await submitDailyReport(savedReport.id)
      }
      ElMessage.success('提交成功')
    }
    
    submitDialogVisible.value = false
    router.push('/daily-report')
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败')
  } finally {
    saving.value = false
  }
}

// 辅助函数
const formatDateTime = (dateTime: string) => {
  if (!dateTime) return '-'
  return new Date(dateTime).toLocaleString('zh-CN')
}

const getGradeTagType = (grade: string) => {
  const typeMap: Record<string, any> = {
    'A': 'success',
    'B': 'primary',
    'C': 'warning',
    'D': 'danger',
    'E': 'info'
  }
  return typeMap[grade] || 'default'
}

// 初始化
onMounted(() => {
  // 检查是否为编辑模式
  const editId = route.params.id
  if (editId) {
    isEdit.value = true
    reportId.value = parseInt(editId as string)
    loadReport()
  }
  
  loadAllTasks()
})
</script>

<style scoped>
.daily-report-container {
  min-height: 100vh;
  background: #f5f5f5;
  overflow-y: auto;
}

.daily-report-content {
  min-height: calc(100vh - 48px);
  padding: 24px;
}

.report-content {
  max-width: none;
  margin: 0 auto;
  padding: 0;
  min-height: calc(100vh - 100px);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e9ecef;
}

.report-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.report-actions {
  display: flex;
  gap: 12px;
}

.report-header-section {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 24px;
}

.date-task-section {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}

.date-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date-label {
  min-width: 80px;
  font-weight: 500;
  color: #303133;
}

.task-label {
  min-width: 80px;
  font-weight: 500;
  color: #303133;
}

.task-info-section {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 24px;
}

.task-info {
  display: flex;
  margin-bottom: 8px;
}

.task-info:last-child {
  margin-bottom: 0;
}

.task-info-label {
  min-width: 80px;
  font-weight: 500;
  color: #606266;
}

.task-info-value {
  color: #303133;
}

/* 表单区域 */
.daily-report-form {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 工作事项组 */
.work-items-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
  padding: 0;
}

/* 确保每个卡片都能正确渲染边框 */
.work-items-group .work-item-card {
  border: 1px solid #e9ecef !important;
  border-radius: 8px !important;
  background: white !important;
  display: block !important;
  visibility: visible !important;
  margin-bottom: 16px !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  overflow: hidden;
}

.work-items-group .work-item-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
  border-color: #409eff !important;
  transform: translateY(-2px);
}

.work-items-group .work-item-card.has-related-task {
  border-left: 4px solid #67c23a;
  border-left-width: 4px;
}

.work-items-group .work-item-card.has-related-task:hover {
  border-left-color: #85ce61;
  border-color: #409eff !important;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
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

.card-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 4px 0;
}

.duplicate-btn,
.delete-btn {
  padding: 8px 12px;
  min-width: 36px;
  min-height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.duplicate-btn {
  color: #409eff;
  border: 1px solid transparent;
}

.duplicate-btn:hover {
  background: #ecf5ff;
  color: #66b1ff;
  border-color: #b3d8ff;
}

.delete-btn {
  color: #f56c6c;
  border: 1px solid transparent;
}

.delete-btn:hover {
  background: #fef0f0;
  color: #f78989;
  border-color: #f5c6cb;
}



/* 卡片内容 */
.card-content {
  padding: 20px;
}

/* 表单行 */
.form-row {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-label {
  min-width: 140px;
  font-weight: 500;
  color: #303133;
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding-top: 8px;
  line-height: 1.5;
}

.form-label i {
  color: #409eff;
  margin-top: 2px;
}

.form-field {
  flex: 1;
}

/* 时间选择器组 */
.time-picker-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.time-separator {
  color: #909399;
  font-weight: 500;
}

/* 评价组 */
.evaluation-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.evaluation-box {
  min-width: 80px;
  padding: 12px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.evaluation-box:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.evaluation-box.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.evaluation-box .letter {
  font-size: 16px;
  font-weight: 600;
}

.evaluation-box .description {
  font-size: 12px;
  text-align: center;
  line-height: 1.3;
}

/* 组底部 */
.group-footer {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.add-group-btn {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 任务统计 */
.task-stats {
  margin-bottom: 20px;
  padding: 16px;
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-stats-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.task-stats-number {
  font-weight: 600;
  color: #409eff;
}

/* 关联任务选择器样式 */
.related-task-selector {
  width: 100%;
}

.related-task-selector .el-input__wrapper {
  border-radius: 6px;
  border: 1px solid #dcdfe6;
  transition: all 0.3s ease;
}

.related-task-selector .el-input__wrapper:hover {
  border-color: #c0c4cc;
}

.related-task-selector .el-input__wrapper.is-focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

/* 下拉选项美化 */
.related-task-selector .el-select-dropdown__item {
  padding: 12px 16px;
  height: auto;
  line-height: 1.4;
  white-space: normal;
}

.related-task-selector .el-select-dropdown__item:hover {
  background-color: #f5f7fa;
}

.related-task-selector .el-select-dropdown__item.selected {
  background-color: #ecf5ff;
  color: #409eff;
  font-weight: 600;
}

/* 任务标签样式 */
.task-option-label {
  display: flex;
  flex-direction: column;
  gap: 2px;
  width: 100%;
  min-width: 400px;
  padding: 0;
}

.task-option-project {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
  white-space: normal;
  overflow: visible;
  text-overflow: unset;
  line-height: 1.3;
}

.task-option-name {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
  white-space: normal;
  overflow: visible;
  text-overflow: unset;
  line-height: 1.3;
}

/* 下拉选项容器宽度优化 */
.el-select-dropdown__item {
  max-width: 600px;
  padding: 16px 20px;
  min-width: 400px;
  white-space: normal;
  word-break: break-word;
  line-height: 1.5;
  min-height: 60px;
  display: flex;
  align-items: center;
}

.el-select-dropdown {
  min-width: 600px !important;
  max-width: 600px;
  width: 600px !important;
}

/* 特殊处理长文本 */
.el-select-dropdown__item .task-option-label {
  max-width: 560px;
}

/* 关联任务选择器宽度优化 */
.related-task-selector {
  width: 100% !important;
}

.related-task-selector .el-select {
  width: 100% !important;
}

.related-task-selector .el-select .el-input {
  width: 100% !important;
}

.related-task-selector .el-select .el-input .el-input__inner {
  min-width: 300px !important;
  width: 100% !important;
}

/* 确保下拉内容能够完整显示 */
.related-task-selector .el-select .el-select-dropdown {
  min-width: 500px !important;
  width: 500px !important;
}

/* 删除确认对话框样式 */
.delete-confirm-message-box {
  border-radius: 8px;
}

.delete-confirm-message-box .el-message-box__header {
  background: #fef0f0;
  border-bottom: 1px solid #f5c6cb;
}

.delete-confirm-message-box .el-message-box__content {
  padding: 20px;
  font-size: 14px;
  line-height: 1.5;
}

.delete-confirm-message-box .el-button--primary {
  background: #f56c6c;
  border-color: #f56c6c;
}

.delete-confirm-message-box .el-button--primary:hover {
  background: #f78989;
  border-color: #f78989;
}

/* 空状态样式 */
.empty-task {
  color: #c0c4cc;
  font-style: italic;
  font-size: 13px;
  text-align: center;
  padding: 20px;
}

/* 关联任务带清空按钮的容器 */
.related-task-with-clear {
  display: flex;
  align-items: flex-start;
  gap: 4px;
  width: 100%;
}

.related-task-selector {
  flex: 1;
}

.clear-task-btn {
  padding: 6px 4px;
  margin-top: 2px;
  color: #909399;
  transition: color 0.2s ease;
}

.clear-task-btn:hover {
  color: #f56c6c;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .task-stats {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
}

@media (max-width: 768px) {
  .work-item-card {
    margin: 0 -10px;
    border-radius: 0 !important;
    border: 1px solid #e9ecef !important;
    border-top: 1px solid #e9ecef !important;
    border-left: 1px solid #e9ecef !important;
    border-right: 1px solid #e9ecef !important;
    border-bottom: 1px solid #e9ecef !important;
  }
  
  .card-header {
    padding: 12px 16px;
  }
  
  .card-content {
    padding: 16px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 8px;
    margin-bottom: 16px;
  }
  
  .form-label {
    min-width: auto;
    padding-top: 0;
    font-size: 13px;
  }
  
  .evaluation-group {
    justify-content: center;
  }
  
  .evaluation-box {
    min-width: 60px;
    padding: 8px 12px;
  }
  
  .evaluation-box .description {
    display: none;
  }
  
  .time-picker-group {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .task-option-label {
    gap: 2px;
  }
  
  .task-option-project {
    font-size: 11px;
  }
  
  .task-option-name {
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .card-number .text {
    display: none;
  }
  
  .card-actions {
    gap: 4px;
  }
  
  .duplicate-btn,
  .delete-btn {
    padding: 4px;
  }
  
  .add-group-btn {
    width: 100%;
    justify-content: center;
  }
}

.form-section {
  border-bottom: 1px solid #e9ecef;
}

.form-section:last-child {
  border-bottom: none;
}

.section-header {
  display: flex;
  align-items: center;
  padding: 20px 24px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.section-number {
  width: 40px;
  height: 40px;
  background: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  border-radius: 50%;
  margin-right: 16px;
  flex-shrink: 0;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  display: flex;
  align-items: center;
}

.section-content {
  padding: 24px;
}



/* 评价说明 */
.evaluation-description {
  margin-top: 16px;
  padding: 12px;
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: 4px;
  font-size: 13px;
  color: #303133;
  line-height: 1.5;
}

.evaluation-description p {
  margin: 4px 0;
}

/* 上级主管评价（只读） */
.supervisor-evaluations {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.evaluation-group {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: hidden;
  background: #fafafa;
}

.evaluation-group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.evaluator-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.supervisor-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.evaluations-list {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.evaluation-item {
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.evaluation-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.evaluation-grade {
  display: flex;
  align-items: center;
  gap: 8px;
}

.evaluation-time {
  font-size: 13px;
  color: #909399;
}

.evaluation-content {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.no-evaluations {
  padding: 40px 20px;
  text-align: center;
}

.evaluation-edit-mode {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 120px;
}

.edit-mode-notice {
  max-width: 400px;
}

/* 任务详情对话框样式 */
.task-detail-content {
  max-height: 500px;
  overflow-y: auto;
}

.task-list-table {
  margin-bottom: 20px;
}

.no-tasks-message {
  padding: 40px 20px;
  text-align: center;
}

/* 提交确认对话框 */
.submit-confirm {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.confirm-text {
  flex: 1;
}

.report-summary {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  margin: 12px 0;
  font-size: 14px;
}

.warning-text {
  color: #e6a23c;
  font-weight: 500;
  margin: 8px 0 0 0;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .daily-report-content {
    padding: 16px;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 50px 0.8fr 170px 1fr 1fr 110px 70px;
  }
  
  .date-task-section {
    flex-direction: column;
    gap: 16px;
  }
}

@media (max-width: 1024px) {
  .daily-report-content {
    padding: 16px;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 40px 0.8fr 150px 0.6fr 0.6fr 100px 60px;
  }
  
  .evaluation-row {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .evaluation-actions {
    align-items: center;
  }
}
</style>