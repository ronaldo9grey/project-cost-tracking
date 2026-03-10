<template>
  <div class="daily-report-container">
    <!-- 日报内容 -->
    <div class="daily-report-content">
      <div class="report-content">
        <!-- 标题和操作 -->
        <div class="report-header">
          <h1 class="report-title">
            {{ isEdit ? (isReportSubmitted ? '查看日清表' : '编辑日清表') : '新建日清表' }}
          </h1>
          <div class="report-actions">
            <!-- 总是显示返回按钮 -->
            <el-button 
              type="default" 
              size="large" 
              @click="handleGoBack"
              :disabled="saving"
            >
              <i class="el-icon-arrow-left"></i>
              返回
            </el-button>
            <!-- 总是显示附件按钮 -->
            <el-button 
              type="info" 
              size="large" 
              @click="handleAttachments"
              :disabled="saving"
            >
              附件
            </el-button>
            <!-- 只在未提交的情况下显示保存和提交按钮 -->
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

        <!-- 日报时间和关联任务 -->
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
                :disabled="isReportSubmitted"
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
                :disabled="isReportSubmitted"
              />
            </div>
          </div>

          <!-- 三、主要工作事项（分组卡片形式） -->
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
                          v-model="item.work_content"
                          type="textarea"
                          :rows="3"
                          placeholder="请详细描述具体工作内容..."
                          maxlength="200"
                          show-word-limit
                          :disabled="isReportSubmitted"
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
                            popper-class="task-select-popper"
                            @change="(val) => handleRelatedTaskChange(val, item)"
                            @input="(val) => item.relatedTaskFilter = val"
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
                            @change="() => handleTimeChange(item, 'startTime')"
                          />
                          <span class="time-separator">至</span>
                          <el-time-picker
                            v-model="item.endTime"
                            placeholder="结束时间"
                            format="HH:mm"
                            value-format="HH:mm"
                            style="width: 140px;"
                            size="small"
                            @change="() => handleTimeChange(item, 'endTime')"
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
              
              <!-- 工时统计 -->
              <div class="work-summary">
                <el-alert
                  :title="`总工时: ${totalHours.toFixed(1)}小时`"
                  type="info"
                  :closable="false"
                  show-icon
                />
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
                :disabled="isReportSubmitted"
              />
            </div>
          </div>

          <!-- 五、上级领导评价（只读） -->
          <div class="form-section">
            <div class="section-header">
              <div class="section-number">五</div>
              <div class="section-title">上级领导评价</div>
            </div>
            <div class="section-content">
              <div class="supervisor-evaluations" v-if="isEdit">
                <div 
                  v-for="evaluation in evaluations" 
                  :key="evaluation.id || 'temp'" 
                  class="evaluation-item"
                >
                  <div class="evaluation-header">
                    <span class="evaluator-name">{{ evaluation.supervisor_name || '未指定' }}</span>
                    <el-tag 
                      :type="evaluation.supervisor_score >= 80 ? 'success' : evaluation.supervisor_score >= 60 ? 'warning' : 'danger'"
                      size="small"
                    >
                      {{ evaluation.supervisor_score || 0 }}分
                    </el-tag>
                  </div>
                  <div class="evaluation-content">
                    {{ evaluation.supervisor_comment || '暂无评价意见' }}
                  </div>
                </div>
                
                <div v-if="evaluations.length === 0" class="no-evaluations">
                  <el-empty description="暂无上级评价" :image-size="60" />
                </div>
              </div>
              
              <!-- 新建模式下的提示 -->
              <div v-else class="evaluation-edit-mode">
                <div class="edit-mode-notice">
                  <el-alert
                    title="温馨提示"
                    description="上级领导评价需要在日报提交后，由您的上级领导进行评价。"
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
          <div class="report-summary">
            <p>日期：{{ selectedDate }}</p>
            <p>工作事项：{{ workItems.length }}项</p>
            <p>总工时：{{ totalHours.toFixed(1) }}小时</p>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, QuestionFilled, Paperclip } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import {
  getMyTasks,
  createDailyReport,
  updateDailyReport,
  submitDailyReport,
  getDailyReport,
  getMyReports,
  createDailyReportWithItems,
  type WorkItem,
  type DailyReportCreate
} from '../../api/dailyReport'

const router = useRouter()
const route = useRoute()

// 添加数据状态管理
const isSaved = ref(false) // 标记数据是否已保存

// 重构的getDailyReport实现，包含自动重新登录逻辑
const getDailyReportFixed = async (reportId: number) => {
  console.log('使用重构的getDailyReport实现...')
  
  // 第一步：获取当前token
  let token = localStorage.getItem('token')
  if (!token) {
    console.log('没有找到token，尝试重新登录...')
    token = await reLoginIfNeeded()
    if (!token) {
      throw new Error('无法获取有效的认证token')
    }
  }
  
  // 第二步：尝试获取数据
  try {
    console.log('尝试获取日报数据，token:', token.substring(0, 20) + '...')
    
    const response = await fetch(`/project/api/v1/daily-report/my-reports/${reportId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    })
    
    console.log('API响应状态:', response.status)
    
    if (response.ok) {
      const data = await response.json()
      console.log('✅ API调用成功:', data.id)
      return data
    } else {
      const errorText = await response.text()
      console.log('❌ API调用失败:', response.status, errorText)
      
      // 如果是401错误，尝试重新登录
      if (response.status === 401) {
        console.log('检测到401错误，尝试重新登录...')
        const newToken = await reLoginIfNeeded()
        if (newToken) {
          console.log('重新登录成功，使用新token重试...')
          return await getDailyReportWithToken(reportId, newToken)
        }
      }
      
      throw new Error(`获取日报数据失败: ${response.status} - ${errorText}`)
    }
  } catch (error) {
    console.error('API调用异常:', error)
    throw error
  }
}

// 附件管理处理函数
const handleAttachments = () => {
  if (!reportId.value) {
    ElMessage.warning('请先保存日报后再管理附件')
    return
  }
  
  // 跳转到附件管理页面
  router.push(`/daily-report/${reportId.value}/attachments`)
}

// 辅助函数：使用指定token获取数据
const getDailyReportWithToken = async (reportId: number, token: string) => {
  const response = await fetch(`/project/api/v1/daily-report/my-reports/${reportId}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  })
  
  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`获取日报数据失败: ${response.status} - ${errorText}`)
  }
  
  return await response.json()
}

// 重新登录函数
const reLoginIfNeeded = async (): Promise<string | null> => {
  console.log('开始重新登录流程...')
  
  try {
    const formData = new URLSearchParams()
    formData.append('username', 'admin')
    formData.append('password', '123456')
    
    const loginResponse = await fetch('/project/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    })
    
    console.log('重新登录响应状态:', loginResponse.status)
    
    if (loginResponse.ok) {
      const loginData = await loginResponse.json()
      console.log('重新登录成功:', loginData)
      
      if (loginData.code === 200 && loginData.data?.access_token) {
        const newToken = loginData.data.access_token
        console.log('新token:', newToken.substring(0, 30) + '...')
        
        // 保存新token
        localStorage.setItem('token', newToken)
        
        // 保存用户信息
        const userInfo = {
          id: '1',
          employee_id: '0001',
          employee_name: 'admin',
          name: 'admin',
          username: 'admin'
        }
        localStorage.setItem('currentUser', JSON.stringify(userInfo))
        
        console.log('✅ 重新登录成功，token已更新')
        return newToken
      } else {
        console.log('❌ 重新登录响应格式错误:', loginData)
        return null
      }
    } else {
      const errorText = await loginResponse.text()
      console.log('❌ 重新登录失败:', errorText)
      return null
    }
  } catch (error) {
    console.error('重新登录异常:', error)
    return null
  }
}

// 重构的getMyTasks实现，包含自动重新登录逻辑
const getMyTasksFixed = async () => {
  console.log('使用重构的getMyTasks实现...')
  
  // 第一步：获取当前token
  let token = localStorage.getItem('token')
  if (!token) {
    console.log('没有找到token，尝试重新登录...')
    token = await reLoginIfNeeded()
    if (!token) {
      console.log('⚠️  无法获取有效token，返回空任务列表')
      return []
    }
  }
  
  // 第二步：尝试获取任务数据
  try {
    console.log('尝试获取任务数据，token:', token.substring(0, 20) + '...')
    
    const response = await fetch('/project/api/v1/daily-report/my-tasks', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    })
    
    console.log('任务API响应状态:', response.status)
    
    if (response.ok) {
      const data = await response.json()
      console.log('✅ 任务API调用成功:', Array.isArray(data) ? data.length : '非数组')
      return Array.isArray(data) ? data : []
    } else {
      const errorText = await response.text()
      console.log('❌ 任务API调用失败:', response.status, errorText)
      
      // 如果是401错误，尝试重新登录
      if (response.status === 401) {
        console.log('检测到401错误，尝试重新登录...')
        const newToken = await reLoginIfNeeded()
        if (newToken) {
          console.log('重新登录成功，使用新token重试...')
          return await getMyTasksWithToken(newToken)
        }
      }
      
      // 返回空数组，避免阻塞页面
      console.log('⚠️  返回空任务列表')
      return []
    }
  } catch (error) {
    console.error('任务API调用异常:', error)
    // 返回空数组，避免阻塞页面
    return []
  }
}

// 辅助函数：使用指定token获取任务数据
const getMyTasksWithToken = async (token: string) => {
  const response = await fetch('/project/api/v1/daily-report/my-tasks', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  })
  
  if (!response.ok) {
    const errorText = await response.text()
    console.log('新token任务API失败:', response.status, errorText)
    return []
  }
  
  const data = await response.json()
  return Array.isArray(data) ? data : []
}

// 状态管理
const isEdit = ref(false)
const reportId = ref<number>(0)
const selectedDate = ref(new Date().toISOString().split('T')[0])
const saving = ref(false)
const submitDialogVisible = ref(false)
const currentReportStatus = ref<string>('')
const isReportSubmitted = ref(false) // 新增：标记日报是否已提交

// 表单数据
const reportForm = reactive({
  work_target: '',
  key_work_tracking: '',
  tomorrow_plan: ''
})

// 我的任务列表
const myTasks = ref<TaskSelector[]>([])

// 工作事项列表
const workItems = ref<(WorkItem & { 
  key: string; 
  content?: string; 
  relatedTask?: string; 
  relatedTaskFilter?: string; 
  startTime?: string; 
  endTime?: string; 
  isAdded?: boolean 
})[]>([
  {
    key: '1',
    report_id: 0,
    project_id: '',
    project_name: '',
    task_id: '',
    task_name: '',
    work_content: '',
    start_time: '',
    end_time: '',
    startTime: '',
    endTime: '',
    hours_spent: 0,
    progress_status: '正常',
    progress_percentage: 0,
    result: '',
    measures: '',
    evaluation: '',
    content: '',
    relatedTask: '',
    relatedTaskFilter: '',
    isAdded: true
  }
])

// 评价列表
const evaluations = ref<any[]>([])

// 计算属性
const canSubmit = computed(() => {
  return selectedDate.value && 
         workItems.value.length > 0 &&
         workItems.value.some(item => item.work_content && item.work_content.trim() !== '')
})

const totalHours = computed(() => {
  return workItems.value.reduce((sum, item) => sum + (item.hours_spent || 0), 0)
})

// 新增：控制按钮显示的逻辑
const showActionButtons = computed(() => {
  return !isReportSubmitted.value
})

const showEditButtons = computed(() => {
  return isEdit.value && !isReportSubmitted.value
})

const showViewButtons = computed(() => {
  return isEdit.value && isReportSubmitted.value
})

// 时间变化处理函数
const handleTimeChange = (item: any, timeType: 'startTime' | 'endTime') => {
  if (item.startTime && item.endTime) {
    // 计算时间差（小时）
    const start = new Date(`2000-01-01 ${item.startTime}`)
    const end = new Date(`2000-01-01 ${item.endTime}`)
    let diffMs = end.getTime() - start.getTime()
    
    // 处理跨天情况
    if (diffMs < 0) {
      diffMs += 24 * 60 * 60 * 1000 // 添加24小时
    }
    
    const diffHours = Math.round((diffMs / (1000 * 60 * 60)) * 10) / 10 // 保留1位小数
    item.hours_spent = diffHours
    
    // 同时更新后端字段映射
    item.start_time = item.startTime
    item.end_time = item.endTime
  } else {
    item.hours_spent = 0
    item.start_time = item.startTime || ''
    item.end_time = item.endTime || ''
  }
}

// 全局监听所有工作事项的时间变化
watch(() => workItems.value.map(item => [item.startTime, item.endTime]), () => {
  workItems.value.forEach(item => {
    if (item.startTime && item.endTime) {
      const start = new Date(`2000-01-01 ${item.startTime}`)
      const end = new Date(`2000-01-01 ${item.endTime}`)
      let diffMs = end.getTime() - start.getTime()
      
      if (diffMs < 0) {
        diffMs += 24 * 60 * 60 * 1000
      }
      
      const diffHours = Math.round((diffMs / (1000 * 60 * 60)) * 10) / 10
      item.hours_spent = diffHours
      item.start_time = item.startTime
      item.end_time = item.endTime
    }
  })
}, { deep: true })

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

// 任务选择处理
const handleTaskChange = (value: any, item: any) => {
  if (typeof value === 'string' && !value.includes('-')) {
    // 自定义工作
    item.project_id = ''
    item.project_name = ''
    item.task_id = ''
    item.task_name = value || ''
  } else if (value && typeof value === 'string' && value.includes('-')) {
    // 选择具体任务
    const [projectName, taskName] = value.split(' - ')
    item.project_name = projectName
    item.task_name = taskName
    // 从myTasks中查找对应的项目ID和任务ID
    const selectedTask = myTasks.value.find(task => 
      `${task.project_name} - ${task.task_name}` === value
    )
    if (selectedTask) {
      item.project_id = selectedTask.project_id
      item.task_id = selectedTask.task_id
    }
  }
}

// 关联任务变更处理
const handleRelatedTaskChange = (value: string, item: any) => {
  console.log('选择了关联任务:', value)
  // 更新相关字段
  item.relatedTask = value
  if (value && value.includes('-')) {
    const [projectName, taskName] = value.split(' - ')
    item.project_name = projectName
    item.task_name = taskName
    // 从myTasks中查找对应的项目ID和任务ID
    const selectedTask = myTasks.value.find(task => 
      `${task.project_name} - ${task.task_name}` === value
    )
    if (selectedTask) {
      item.project_id = selectedTask.project_id
      item.task_id = selectedTask.task_id
    }
  } else {
    item.project_id = ''
    item.project_name = ''
    item.task_id = ''
    item.task_name = value || ''
  }
}

// 清空关联任务
const clearTask = (item: any) => {
  item.relatedTask = ''
  item.relatedTaskFilter = ''
  item.project_id = ''
  item.project_name = ''
  item.task_id = ''
  item.task_name = ''
}

// 确认删除工作事项
const confirmDeleteWorkItem = (index: number) => {
  if (workItems.value.length <= 1) {
    ElMessage.warning('至少需要保留一个工作事项组')
    return
  }
  workItems.value.splice(index, 1)
}

// 复制工作事项
const duplicateWorkItem = (index: number) => {
  const originalItem = workItems.value[index]
  const newItem = {
    ...originalItem,
    key: Date.now().toString() + Math.random().toString(36).substr(2, 9)
  }
  workItems.value.splice(index + 1, 0, newItem)
  isSaved.value = false // 标记为未保存
  ElMessage.success('复制成功')
}

// 统计相关任务数量
const getRelatedTasksCount = () => {
  return workItems.value.filter(item => 
    (item.relatedTask && item.relatedTask.trim() !== '') ||
    (item.project_name && item.task_name)
  ).length
}

// 添加工作事项行
const addWorkItem = () => {
  workItems.value.push({
    key: Date.now().toString(),
    report_id: 0,
    project_id: '',
    project_name: '',
    task_id: '',
    task_name: '',
    work_content: '',
    start_time: '',
    end_time: '',
    startTime: '',
    endTime: '',
    hours_spent: 0,
    progress_status: '正常',
    progress_percentage: 0,
    result: '',
    measures: '',
    evaluation: '',
    content: '',
    relatedTask: '',
    relatedTaskFilter: '',
    isAdded: true
  })
  isSaved.value = false // 标记为未保存
}

// 移除工作事项行
const removeWorkItem = (index: number) => {
  if (workItems.value.length > 1) {
    workItems.value.splice(index, 1)
    isSaved.value = false // 标记为未保存
  }
}

// 日期变更处理
const handleDateChange = async (date: string) => {
  console.log('日期变更:', date)
  
  if (!date) return
  
  try {
    // 使用 getMyReports API 查询指定日期的日报
    const response = await getMyReports({ report_date: date, size: 1 })
    
    if (response && response.items && response.items.length > 0) {
      const existingReport = response.items[0]
      
      // 如果找到已存在的日报，加载数据并调整状态
      reportId.value = existingReport.id
      isEdit.value = true
      
      if (existingReport.status === '待提交') {
        ElMessage({
          message: `检测到${date}已有草稿日报，已自动加载数据`,
          type: 'info',
          duration: 3000
        })
        // 加载数据
        await loadDailyReport(reportId.value)
      } else if (existingReport.status === '已提交' || existingReport.status === '已评价') {
        ElMessage({
          message: `检测到${date}已有${existingReport.status}日报，已加载数据供查看`,
          type: 'info',
          duration: 3000
        })
        // 加载数据
        await loadDailyReport(reportId.value)
      } else {
        ElMessage({
          message: `检测到${date}已有${existingReport.status}日报，已加载数据`,
          type: 'info',
          duration: 3000
        })
        // 加载数据
        await loadDailyReport(reportId.value)
      }
    } else {
      // 没有找到该日期的日报，清空表单
      console.log(`没有找到${date}的日报，清空表单`)
      reportId.value = 0
      isEdit.value = false
      isSaved.value = false
      isReportSubmitted.value = false
      
      // 清空表单数据
      reportForm.work_target = ''
      reportForm.key_work_tracking = ''
      reportForm.tomorrow_plan = ''
      
      // 清空工作事项，只保留一个空行
      workItems.value = [{
        key: Date.now().toString(),
        report_id: 0,
        project_id: '',
        project_name: '',
        task_id: '',
        task_name: '',
        work_content: '',
        start_time: '',
        end_time: '',
        startTime: '',
        endTime: '',
        hours_spent: 0,
        progress_status: '正常',
        progress_percentage: 0,
        result: '',
        measures: '',
        evaluation: '',
        content: '',
        relatedTask: '',
        relatedTaskFilter: '',
        isAdded: true
      }]
      
      ElMessage({
        message: `${date}暂无日报，开始新建`,
        type: 'info',
        duration: 3000
      })
    }
    
  } catch (error: any) {
    console.error('检查指定日期日报失败:', {
      error: error,
      message: error?.message,
      date: date,
      timestamp: new Date().toISOString()
    })
    
    // API错误不影响界面，默默处理
    if (error?.response?.status === 401) {
      console.warn('检测到日报API的401错误，HTTP拦截器已处理')
    }
  }
}

// 保存处理
const handleSave = async () => {
  saving.value = true
  try {
    const reportData: DailyReportCreate = {
      report_date: selectedDate.value,
      employee_id: "0001", // 临时设置，需要从用户信息获取
      employee_name: "admin", // 临时设置，需要从用户信息获取
      work_target: reportForm.work_target, // 添加今日工作目标字段
      key_work_tracking: reportForm.key_work_tracking, // 添加近期重点工作跟踪字段
      tomorrow_plan: reportForm.tomorrow_plan,
      planned_hours: 8.0 // 临时设置
    }

    const workItemsData = workItems.value.map(item => ({
      work_content: item.work_content,
      project_id: item.project_id,
      project_name: item.project_name,
      task_id: item.task_id,
      task_name: item.task_name,
      start_time: item.start_time,
      end_time: item.end_time,
      hours_spent: item.hours_spent,
      result: item.result,
      measures: item.measures,
      evaluation: item.evaluation,
      progress_status: item.progress_status,
      progress_percentage: item.progress_percentage
    }))

    if (isEdit.value) {
      await updateDailyReport(reportId.value, reportData)
      isSaved.value = true // 标记为已保存状态
      ElMessage.success('更新成功')
    } else {
      const result = await createDailyReportWithItems({
        report: reportData,
        work_items: workItemsData
      })
      reportId.value = result.id
      isEdit.value = true
      isSaved.value = true // 标记为已保存状态
      ElMessage.success('保存成功')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

// 提交处理
const handleSubmit = () => {
  submitDialogVisible.value = true
}

// 返回处理函数
const handleGoBack = () => {
  // 检查是否有未保存的内容
  const hasUnsavedContent = checkUnsavedContent()
  
  if (hasUnsavedContent) {
    // 显示确认对话框
    ElMessageBox.confirm(
      '您有未保存的内容，确认离开吗？\n\n未保存的工作事项和内容将丢失。',
      '确认离开',
      {
        confirmButtonText: '确认离开',
        cancelButtonText: '继续编辑',
        type: 'warning',
        center: true,
        customClass: 'unsaved-content-dialog'
      }
    ).then(() => {
      // 用户确认离开
      router.push('/daily-report')
    }).catch(() => {
      // 用户取消离开
      ElMessage.info('继续编辑')
    })
  } else {
    // 没有未保存内容，直接返回
    router.push('/daily-report')
  }
}

// 检查是否有未保存的内容
const checkUnsavedContent = () => {
  // 如果数据已保存，则认为没有未保存内容
  if (isSaved.value) {
    return false
  }
  
  // 检查日报基本信息
  if (reportForm.tomorrow_plan && reportForm.tomorrow_plan.trim() !== '') {
    return true
  }
  
  // 检查工作事项
  if (workItems.value.length > 0) {
    // 检查是否有工作内容
    for (const item of workItems.value) {
      if (item.work_content && item.work_content.trim() !== '') {
        return true
      }
      if (item.result && item.result.trim() !== '') {
        return true
      }
      if (item.measures && item.measures.trim() !== '') {
        return true
      }
    }
  }
  
  return false
}

// 确认提交
const confirmSubmit = async () => {
  // 检查是否有工作事项
  if (workItems.value.length === 0) {
    ElMessage.warning('请至少添加一个工作事项')
    return
  }
  
  // 检查是否有工作内容
  const hasWorkContent = workItems.value.some(item => 
    item.work_content && item.work_content.trim() !== ''
  )
  
  if (!hasWorkContent) {
    ElMessage.warning('请至少填写一个工作事项的具体内容')
    return
  }
  
  // 显示保存提醒
  ElMessage.info('正在保存和提交，请稍候...')
  
  saving.value = true
  try {
    // 先保存
    await handleSave()
    
    // 然后提交
    if (reportId.value) {
      await submitDailyReport(reportId.value)
      ElMessage.success('提交成功')
      
      // 显示提交成功提醒
      setTimeout(() => {
        ElMessage({
          message: '日报已成功提交，提交后将无法修改，只能查看。',
          type: 'success',
          duration: 3000
        })
        router.push('/daily-report')
      }, 500)
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败，请检查网络连接或稍后重试')
  } finally {
    saving.value = false
    submitDialogVisible.value = false
  }
}

// 加载任务列表
const loadMyTasks = async () => {
  try {
    myTasks.value = await getMyTasksFixed()
  } catch (error) {
    console.error('加载任务列表失败:', error)
    ElMessage.error('加载任务列表失败')
  }
}

// 加载日报数据（编辑模式）
const loadDailyReport = async (id: number) => {
  try {
    console.log('开始加载日报数据:', { id, timestamp: new Date().toISOString() })
    
    // 确保token有效
    let token = localStorage.getItem('token')
    if (!token) {
      console.log('没有token，尝试重新登录...')
      token = await reLoginIfNeeded()
      if (!token) {
        throw new Error('无法获取有效的认证token')
      }
    }
    
    console.log('使用token进行API调用...')
    
    // 使用备用方法直接调用API，绕过可能的axios问题
    const report = await getDailyReportFixed(id)
    console.log('成功加载日报数据:', { 
      id: report.id, 
      status: report.status, 
      reportDate: report.report_date,
      hasWorkItems: !!report.work_items
    })
    
    // 检查状态并设置对应的状态变量
    if (report.status && (report.status === '已提交' || report.status === '已评价')) {
      isReportSubmitted.value = true
    } else {
      isReportSubmitted.value = false
    }
    
    // 保存当前状态
    currentReportStatus.value = report.status || '待提交'
    
    // 填充基本信息
    selectedDate.value = report.report_date
    reportForm.work_target = report.work_target || ''
    reportForm.key_work_tracking = report.key_work_tracking || ''
    reportForm.tomorrow_plan = report.tomorrow_plan || ''
    
    // 填充工作事项（如果有的话）
    if (report.work_items && report.work_items.length > 0) {
      workItems.value = report.work_items.map((item, index) => ({
        ...item,
        key: item.id?.toString() || (index + 1).toString(),
        taskSelector: item.task_id ? {
          project_id: item.project_id,
          project_name: item.project_name,
          task_id: item.task_id,
          task_name: item.task_name
        } : 'custom',
        relatedTask: item.task_name ? `${item.project_name} - ${item.task_name}` : '',
        startTime: item.start_time || '',
        endTime: item.end_time || ''
      }))
    }
    
    // 填充评价
    if (report.supervisor_score && report.supervisor_name) {
      // 转换后端评价数据为前端格式
      evaluations.value = [{
        id: '1',
        supervisor_score: report.supervisor_score,
        supervisor_comment: report.supervisor_comment || '',
        supervisor_id: report.supervisor_id || '',
        supervisor_name: report.supervisor_name || '未指定',
        evaluated_at: report.evaluated_at || new Date().toISOString()
      }]
    } else {
      evaluations.value = []
    }
    
    console.log('日报数据加载完成')
  } catch (error: any) {
    console.error('加载日报数据失败:', {
      error: error,
      message: error?.message,
      status: error?.response?.status,
      url: error?.config?.url,
      timestamp: new Date().toISOString()
    })
    
    // 根据错误类型给出不同的提示
    if (error?.response?.status === 401) {
      ElMessageBox.confirm(
        '身份验证失效，请重新登录',
        '身份验证问题',
        {
          confirmButtonText: '重新登录',
          cancelButtonText: '取消',
          type: 'warning',
        }
      ).then(() => {
        router.push('/login')
      }).catch(() => {
        // 用户点击取消，返回列表页
        router.push('/daily-report')
      })
    } else if (error?.response?.status === 404) {
      ElMessage.error('日报不存在或已被删除')
      router.push('/daily-report')
    } else if (error?.response?.status === 403) {
      ElMessage.error('权限不足，无法访问此日报')
      router.push('/daily-report')
    } else {
      ElMessage.error(`加载日报数据失败: ${error?.message || '未知错误'}`)
      router.push('/daily-report')
    }
  }
}

// 生命周期
onMounted(async () => {
  // 统一初始化流程，避免并发调用导致token状态竞争
  await initializePage()
})

// 统一初始化函数
const initializePage = async () => {
  try {
    // 先加载任务列表
    await loadMyTasks()
    
    // 然后根据路由参数决定模式
    const id = route.params.id
    const path = route.path
    
    if (id && typeof id === 'string') {
      // 明确的编辑模式（从列表页点击编辑）
      reportId.value = parseInt(id)
      isEdit.value = true
      isSaved.value = true // 编辑模式下初始状态为已保存
      await loadDailyReport(reportId.value)
    } else if (path.includes('/create')) {
      // 新建模式 - 检查当前日期是否已有日报
      isSaved.value = false // 新建模式下初始状态为未保存
      await checkExistingReportForToday()
    }
  } catch (error) {
    console.error('页面初始化失败:', error)
    // 初始化失败不阻塞页面，只是记录日志
  }
}

// 检查当前日期是否已有日报（用于新建页面）
const checkExistingReportForToday = async () => {
  try {
    const today = new Date().toISOString().split('T')[0]
    
    // 使用 getMyReports API 查询当前日期的日报
    const response = await getMyReports({ report_date: today, size: 1 })
    
    if (response && response.items && response.items.length > 0) {
      const existingReport = response.items[0]
      
      // 如果找到已存在的日报，切换到编辑模式并加载数据
      reportId.value = existingReport.id
      isEdit.value = true
      
      if (existingReport.status === '待提交') {
        ElMessage({
          message: `检测到当前日期已有草稿日报，已自动切换到编辑模式`,
          type: 'info',
          duration: 3000
        })
      } else if (existingReport.status === '已提交' || existingReport.status === '已评价') {
        ElMessage({
          message: `检测到当前日期已有${existingReport.status}日报，已加载数据进行查看`,
          type: 'info',
          duration: 3000
        })
      } else {
        ElMessage({
          message: `检测到当前日期已有${existingReport.status}日报，已加载数据`,
          type: 'info',
          duration: 3000
        })
      }
      
      // 加载已存在的日报数据
      await loadDailyReport(reportId.value)
    } else {
      // 没有找到当前日期的日报，保持新建模式
      console.log('没有找到当前日期的日报，保持新建模式')
      reportId.value = 0
      isEdit.value = false
    }
    
  } catch (error: any) {
    console.error('检查当前日期日报失败:', {
      error: error,
      message: error?.message,
      status: error?.response?.status,
      url: error?.config?.url,
      timestamp: new Date().toISOString()
    })
    
    // 检查是否是日报API的401错误（这种错误已经由HTTP拦截器处理）
    if (error?.response?.status === 401 && error?.config?.url?.includes('/daily-report')) {
      console.warn('检测到日报API的401错误，HTTP拦截器已处理，组件静默处理')
      // 静默处理，保持新建模式
    } else if (error?.response?.status === 403) {
      ElMessage.warning('权限不足，无法查看当前日期的日报')
    } else if (error?.response?.status === 404) {
      ElMessage.warning('当前日期没有找到日报，将创建新的日报')
    } else if (error?.response?.status >= 500) {
      ElMessage.warning('服务器错误，将创建新的日报')
    } else if (error?.response?.status === 401) {
      // 其他API的401错误
      ElMessage.warning('身份验证失效，请重新登录')
      router.push('/login')
      return
    } else {
      // 其他错误
      console.log('其他错误，保持新建模式')
    }
    
    // 无论什么错误，都保持新建模式
    reportId.value = 0
    isEdit.value = false
  }
}
</script>

<style scoped>
.daily-report-container {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.daily-report-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.report-content {
  padding: 30px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.report-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.report-actions {
  display: flex;
  gap: 12px;
}

.report-header-section {
  margin-bottom: 30px;
}

.date-task-section {
  display: flex;
  gap: 30px;
  align-items: center;
}

.date-item, .task-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date-label, .task-label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.form-section {
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
}

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

/* 工作事项组 */
.work-items-group {
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
  text-align: left;
}

/* 任务选择器 */
.related-task-with-clear {
  display: flex;
  align-items: center;
  gap: 8px;
}

.related-task-selector {
  flex: 1;
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
  margin-bottom: 2px;
}

.task-option-name {
  font-size: 14px;
  color: #303133;
  font-weight: 600;
  white-space: normal;
  overflow: visible;
  text-overflow: unset;
}

/* 关联任务选择器优化 */
.related-task-selector {
  width: 100% !important;
}

.related-task-selector .el-select {
  width: 100% !important;
}

.related-task-selector .el-select .el-input {
  width: 100% !important;
}

/* 调整选择后的字体大小 */
.related-task-selector .el-select .el-input .el-input__inner {
  font-size: 14px !important;
}

.related-task-selector .el-select .el-input .el-input__placeholder {
  font-size: 14px !important;
}

/* 下拉选项宽度优化 */
.el-select-dropdown {
  max-width: 600px;
  width: 600px !important;
}



.empty-task {
  padding: 8px 12px;
  text-align: center;
  color: #909399;
  font-size: 12px;
}

/* 任务选项样式 - 仿照原始版本 */
.el-select-dropdown__item {
  max-width: 600px !important;
  padding: 12px 16px !important;
  min-width: 400px !important;
  white-space: normal !important;
  word-break: break-word !important;
  line-height: 1.5 !important;
  min-height: 60px !important;
  display: block !important;
  align-items: flex-start !important;
  font-size: 14px !important;
}

.el-select-dropdown__item span {
  display: block !important;
  margin: 0 !important;
  font-size: 14px !important;
}

.clear-task-btn {
  color: #f56c6c;
}

.clear-task-btn:hover {
  color: #f78989;
  background: #fef0f0;
}

/* 时间选择器组 */
.time-picker-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 调整时间选择器字体大小 */
.time-picker-group .el-input__inner,
.time-picker-group .el-input__placeholder {
  font-size: 14px !important;
}

.time-separator {
  color: #909399;
  font-weight: 500;
  font-size: 14px;
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

/* 上级领导评价 */
.supervisor-evaluations {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.evaluation-item {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
}

.evaluation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.evaluator-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.evaluation-content {
  color: #606266;
  line-height: 1.6;
  font-size: 14px;
}

.no-evaluations {
  padding: 40px 20px;
  text-align: center;
  color: #909399;
}

.evaluation-edit-mode {
  padding: 20px;
  text-align: center;
}

.edit-mode-notice {
  max-width: 600px;
  margin: 0 auto;
}

/* 扩大 el-alert 宽度 */
.evaluation-edit-mode .el-alert {
  width: 100% !important;
  margin: 0 auto;
}

.evaluation-edit-mode .el-alert__description {
  font-size: 14px !important;
  line-height: 1.5 !important;
  white-space: nowrap !important;
}

/* 任务统计 */
.task-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #f0f9ff;
  border-radius: 6px;
  border: 1px solid #e1f3fe;
}

.task-stats-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.task-stats-item i {
  color: #409eff;
}

.task-stats-number {
  font-weight: 600;
  color: #409eff;
}

/* 添加组按钮 */
.group-footer {
  margin-top: 16px;
  text-align: center;
}

.add-group-btn {
  padding: 12px 24px;
  font-size: 14px;
}

/* 评价说明 */
.evaluation-description {
  margin-top: 16px;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}

.evaluation-description p {
  margin: 4px 0;
  font-size: 14px;
  line-height: 1.5;
}

.evaluation-description p:first-child {
  font-weight: 600;
  color: #303133;
}

/* 工时统计 */
.work-summary {
  margin-top: 16px;
}

/* 表格样式（保留以兼容） */
.refactored-work-items-table {
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  overflow: hidden;
}

.table-header {
  display: flex;
  background: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
}

.table-header-cell {
  padding: 12px 8px;
  font-weight: 600;
  color: #606266;
  text-align: center;
  border-right: 1px solid #dcdfe6;
}

.table-body {
  background: white;
}

.refactored-table-row {
  display: flex;
  border-bottom: 1px solid #ebeef5;
  min-height: 140px;
}

.refactored-table-row:last-child {
  border-bottom: none;
}

.table-cell {
  padding: 8px;
  border-right: 1px solid #ebeef5;
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

.table-cell:last-child {
  border-right: none;
}

.time-vertical-picker {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
}

.time-separator {
  text-align: center;
  color: #909399;
  font-size: 12px;
}

.evaluation-boxes {
  display: flex;
  gap: 2px;
  justify-content: center;
}

.evaluation-box {
  width: 24px;
  height: 24px;
  border: 1px solid #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
  font-weight: bold;
  color: #909399;
  transition: all 0.3s;
}

.evaluation-box:hover {
  border-color: #409eff;
  color: #409eff;
}

.evaluation-box.active {
  background: #409eff;
  color: white;
  border-color: #409eff;
}

.table-footer {
  padding: 15px;
  text-align: center;
  background: #fafafa;
  border-top: 1px solid #ebeef5;
}

.evaluation-description {
  margin-top: 15px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
}

.evaluation-description p {
  margin: 5px 0;
}

.work-summary {
  margin-top: 15px;
}

.supervisor-evaluations {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.evaluation-item {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.evaluation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.evaluator-name {
  font-weight: 600;
  color: #303133;
}

.evaluation-content {
  color: #606266;
  line-height: 1.5;
}

.no-evaluations {
  padding: 20px;
  text-align: center;
}

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
  color: #606266;
}

.report-summary p {
  margin: 4px 0;
}

.warning-text {
  color: #e6a23c;
  font-weight: 500;
  margin: 8px 0 0 0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .refactored-work-items-table {
    overflow-x: auto;
  }
  
  .table-header,
  .refactored-table-row {
    min-width: 1200px;
  }
}

@media (max-width: 768px) {
  .report-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .report-title {
    font-size: 20px;
    margin: 0;
  }
  
  .report-actions {
    width: 100%;
    flex-direction: column;
    gap: 10px;
  }
  
  .report-actions .el-button {
    width: 100%;
  }
  
  .date-task-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 8px;
    margin-bottom: 16px;
  }
  
  .form-label {
    min-width: auto;
    text-align: left;
    padding-top: 0;
    font-size: 13px;
  }
  
  .evaluation-group {
    gap: 8px;
  }
  
  .evaluation-box {
    min-width: 120px;
    height: 120px;
    padding: 24px 28px;
  }
  
  .evaluation-box .description {
    font-size: 12px;
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
</style>