<template>
  <div class="project-board-container">
    <div class="board-header">
      <div class="header-left">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="handleDateFilter"
          style="width: 280px;"
        />
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>
    
    <div class="board-content">
      <div class="projects-panel">
        <div v-if="loading && !projects.length" class="loading-container">
          <el-icon class="is-loading" :size="40"><Loading /></el-icon>
          <p>加载中...</p>
        </div>
        
        <div v-else-if="!filteredProjects.length" class="empty-container">
          <el-empty description="暂无项目数据" />
        </div>
        
        <div v-else class="project-cards">
          <div 
            v-for="project in filteredProjects" 
            :key="project.id"
            class="project-card"
            :class="{ 'is-selected': selectedProject?.id === project.id }"
            @click="selectProject(project)"
          >
            <div class="card-top">
              <div class="project-status" :class="getStatusClass(project.status)">
                {{ getStatusText(project.status) }}
              </div>
              <div class="project-menu">
                <el-dropdown trigger="click" @command="(cmd: string) => handleProjectCommand(cmd, project)">
                  <el-icon class="menu-icon"><MoreFilled /></el-icon>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="detail">查看详情</el-dropdown-item>
                      <el-dropdown-item command="chat" :disabled="selectedProject?.id !== project.id">
                        与AI对话
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
            
            <div class="card-title">{{ project.name }}</div>
            <div class="card-desc">{{ project.describe || '暂无描述' }}</div>
            
            <div class="card-info">
              <div class="info-row">
                <span class="info-label">负责人</span>
                <span class="info-value">
                  <el-icon><User /></el-icon>
                  {{ project.leader || '未指定' }}
                </span>
              </div>
              <div class="info-row">
                <span class="info-label">开始时间</span>
                <span class="info-value">
                  <el-icon><Calendar /></el-icon>
                  {{ formatDate(project.start_date) }}
                </span>
              </div>
              <div class="info-row">
                <span class="info-label">预算金额</span>
                <span class="info-value budget">
                  <el-icon><Money /></el-icon>
                  ¥{{ formatMoney(project.budget_total_cost) }}
                </span>
              </div>
              <div class="info-row">
                <span class="info-label">实际成本</span>
                <span class="info-value" :class="{ 'over-budget': project.actual_total_cost > project.budget_total_cost }">
                  <el-icon><Wallet /></el-icon>
                  ¥{{ formatMoney(project.actual_total_cost) }}
                </span>
              </div>
            </div>
            
            <div class="card-progress">
              <div class="progress-header">
                <span>项目进度</span>
                <span class="progress-value" :style="{ color: getProgressColor(project.progress) }">{{ project.progress }}%</span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: project.progress + '%', background: getProgressColor(project.progress) }"></div>
              </div>
            </div>
            
            <div class="card-footer">
              <div class="cost-rate" :class="getCostRateClass(project)">
                <span class="rate-label">成本率</span>
                <span class="rate-value">{{ getCostRate(project) }}%</span>
              </div>
              <div class="days-left">
                <el-icon><Clock /></el-icon>
                <span>{{ getDaysLeft(project) }}天</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="chat-panel">
        <div class="chat-header">
          <div class="chat-title">
            <el-icon><ChatDotRound /></el-icon>
            <span>AI 智能助手</span>
          </div>
          <div class="chat-context" v-if="selectedProject">
            <span class="context-label">当前项目：</span>
            <span class="context-name">{{ selectedProject.name }}</span>
          </div>
        </div>
        
        <div class="chat-messages" ref="chatContainer">
          <div v-if="!selectedProject" class="chat-empty">
            <el-empty description="请选择一个项目开始对话" />
          </div>
          <template v-else>
            <div 
              v-for="(msg, index) in chatMessages" 
              :key="index"
              class="chat-message"
              :class="msg.role"
            >
              <div class="message-avatar">
                <el-avatar :size="32" :icon="msg.role === 'user' ? 'User' : 'ChatDotRound'" />
              </div>
              <div class="message-content">
                <div class="message-header">
                  <span class="message-name">{{ msg.role === 'user' ? '我' : 'AI助手' }}</span>
                  <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
                </div>
                <div class="message-text" v-html="formatMessage(msg.content)"></div>
              </div>
            </div>
            <div v-if="aiTyping" class="chat-message ai typing">
              <div class="message-avatar">
                <el-avatar :size="32" icon="ChatDotRound" />
              </div>
              <div class="message-content">
                <div class="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          </template>
        </div>
        
        <div class="chat-input" v-if="selectedProject">
          <div class="quick-questions">
            <el-tag 
              v-for="(q, i) in quickQuestions" 
              :key="i"
              type="info" 
              effect="plain" 
              round
              @click="sendQuickQuestion(q)"
            >
              {{ q }}
            </el-tag>
          </div>
          <div class="input-area">
            <el-input
              v-model="userInput"
              type="textarea"
              :rows="2"
              placeholder="输入问题，与AI讨论当前项目..."
              @keydown.enter.ctrl="sendMessage"
              resize="none"
            />
            <el-button type="primary" :loading="aiLoading" @click="sendMessage">
              <el-icon><Promotion /></el-icon>
            </el-button>
          </div>
          <div class="input-tip">按 Ctrl + Enter 发送</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Refresh, Loading, MoreFilled, User, Calendar, ChatDotRound, Promotion, Money, Wallet, Clock 
} from '@element-plus/icons-vue'
import { getProjects, type Project } from '../../api/project'
import { getProjectFullData, chatWithAI } from '../../api/aiChat'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const router = useRouter()
const loading = ref(false)
const aiLoading = ref(false)
const aiTyping = ref(false)
const projects = ref<Project[]>([])
const selectedProject = ref<Project | null>(null)
const dateRange = ref<[string, string] | null>(null)
const userInput = ref('')
const chatMessages = ref<ChatMessage[]>([])
const chatContainer = ref<HTMLElement | null>(null)

const quickQuestions = [
  '项目成本超支原因分析',
  '进度落后的原因和改进建议',
  '资源配置是否合理',
  '风险点识别和建议'
]

const filteredProjects = computed(() => {
  if (!dateRange.value || !dateRange.value[0] || !dateRange.value[1]) {
    return projects.value
  }
  const [start, end] = dateRange.value
  return projects.value.filter(p => {
    if (!p.start_date) return false
    return p.start_date >= start && p.start_date <= end
  })
})

const getStatusClass = (status: string) => {
  const statusMap: Record<string, string> = {
    '进行中': 'status-active',
    '已完成': 'status-completed',
    '已暂停': 'status-paused',
    '未开始': 'status-pending'
  }
  return statusMap[status] || 'status-default'
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    '进行中': '进行中',
    '已完成': '已完成',
    '已暂停': '已暂停',
    '未开始': '未开始'
  }
  return statusMap[status] || status || '未知'
}

const getProgressColor = (progress: number) => {
  if (progress >= 80) return '#52c41a'
  if (progress >= 50) return '#faad14'
  return '#ff4d4f'
}

const getCostRate = (project: Project) => {
  if (!project.budget_total_cost || project.budget_total_cost === 0) return '0'
  return ((project.actual_total_cost / project.budget_total_cost) * 100).toFixed(1)
}

const getCostRateClass = (project: Project) => {
  const rate = parseFloat(getCostRate(project))
  if (rate < 80) return 'rate-good'
  if (rate < 100) return 'rate-warning'
  return 'rate-danger'
}

const getDaysLeft = (project: Project) => {
  if (!project.start_date || !project['计划结束日期']) return '-'
  const start = new Date(project.start_date)
  const end = new Date(project['计划结束日期'])
  const now = new Date()
  const diff = Math.ceil((end.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
  return diff > 0 ? diff : 0
}

const formatMoney = (amount: number) => {
  if (!amount) return '0'
  if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  }
  return amount.toLocaleString()
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return date.substring(0, 10)
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const formatMessage = (content: string) => {
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
}

const loadProjects = async () => {
  loading.value = true
  try {
    const response = await getProjects({ page: 1, size: 100 })
    projects.value = response.items || []
  } catch (error) {
    console.error('加载项目失败:', error)
    ElMessage.error('加载项目失败')
  } finally {
    loading.value = false
  }
}

const handleDateFilter = () => {
  ElMessage.success('已按时间筛选')
}

const refreshData = async () => {
  dateRange.value = null
  await loadProjects()
  ElMessage.success('刷新成功')
}

const selectProject = async (project: Project) => {
  selectedProject.value = project
  chatMessages.value = []
  
  try {
    const response = await getProjectFullData(project.id)
    console.log('获取项目完整数据:', response)
    
    const contextMessage: ChatMessage = {
      role: 'assistant',
      content: `已加载项目【${project.name}】的完整数据。<br><br>
      <strong>基本信息：</strong><br>
      - 负责人：${project.leader || '未指定'}<br>
      - 预算：¥${formatMoney(project.budget_total_cost)}<br>
      - 实际成本：¥${formatMoney(project.actual_total_cost)}<br>
      - 进度：${project.progress}%<br>
      - 状态：${project.status}<br><br>
      <strong>数据统计：</strong><br>
      - 任务数量：${response.tasks?.length || 0}<br>
      - 物料成本记录：${response.material_costs?.length || 0}<br>
      - 人力成本记录：${response.labor_costs?.length || 0}<br>
      - 外包成本记录：${response.outsourcing_costs?.length || 0}<br>
      - 间接成本记录：${response.indirect_costs?.length || 0}<br><br>
      您可以问我关于这个项目的任何问题，我会基于完整数据为您提供分析和建议。`,
      timestamp: new Date()
    }
    chatMessages.value.push(contextMessage)
  } catch (error) {
    console.error('加载项目数据失败:', error)
    const contextMessage: ChatMessage = {
      role: 'assistant',
      content: `已加载项目【${project.name}】的基本信息。<br><br>
      - 负责人：${project.leader || '未指定'}<br>
      - 预算：¥${formatMoney(project.budget_total_cost)}<br>
      - 实际成本：¥${formatMoney(project.actual_total_cost)}<br>
      - 进度：${project.progress}%<br>
      - 状态：${project.status}<br><br>
      您可以问我关于这个项目的任何问题。`,
      timestamp: new Date()
    }
    chatMessages.value.push(contextMessage)
  }
}

const handleProjectCommand = (command: string, project: Project) => {
  switch (command) {
    case 'detail':
      router.push(`/projects/${project.id}`)
      break
    case 'chat':
      selectProject(project)
      break
  }
}

const sendQuickQuestion = (question: string) => {
  if (!selectedProject.value) return
  userInput.value = question
  sendMessage()
}

const sendMessage = async () => {
  if (!userInput.value.trim() || !selectedProject.value || aiLoading.value) return
  
  const userMessage: ChatMessage = {
    role: 'user',
    content: userInput.value.trim(),
    timestamp: new Date()
  }
  chatMessages.value.push(userMessage)
  userInput.value = ''
  
  await nextTick()
  scrollToBottom()
  
  aiLoading.value = true
  aiTyping.value = true
  
  try {
    const response = await getProjectFullData(selectedProject.value.id)
    
    const projectContext = {
      project: {
        id: selectedProject.value.id,
        name: selectedProject.value.name,
        describe: selectedProject.value.describe,
        leader: selectedProject.value.leader,
        status: selectedProject.value.status,
        progress: selectedProject.value.progress,
        start_date: selectedProject.value.start_date,
        budget_total_cost: selectedProject.value.budget_total_cost,
        actual_total_cost: selectedProject.value.actual_total_cost
      },
      project_tasks: response.tasks || [],
      material_costs: response.material_costs || [],
      labor_costs: response.labor_costs || [],
      outsourcing_costs: response.outsourcing_costs || [],
      indirect_costs: response.indirect_costs || []
    }
    
    const aiResponse = await chatWithAI(projectContext, userMessage.content)
    
    const aiMessage: ChatMessage = {
      role: 'assistant',
      content: aiResponse,
      timestamp: new Date()
    }
    chatMessages.value.push(aiMessage)
  } catch (error: any) {
    ElMessage.error(error.message || 'AI响应失败')
  } finally {
    aiLoading.value = false
    aiTyping.value = false
    await nextTick()
    scrollToBottom()
  }
}

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.project-board-container {
  padding: 16px;
  background: #f7f8fa;
  min-height: calc(100vh - 40px);
}

.board-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding: 12px 0;
  background: transparent;
}

.header-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.board-content {
  display: flex;
  gap: 16px;
  height: calc(100vh - 140px);
}

.projects-panel {
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
}

.loading-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #8c8c8c;
}

.project-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.project-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.25s ease;
  border: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: relative;
  overflow: hidden;
}

.project-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #1890ff 0%, #52c41a 100%);
  opacity: 0;
  transition: opacity 0.25s;
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.project-card:hover::before {
  opacity: 1;
}

.project-card.is-selected {
  border-color: #1890ff;
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.15);
}

.project-card.is-selected::before {
  opacity: 1;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.project-status {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.status-active {
  background: #e6fffb;
  color: #13c2c2;
}

.status-completed {
  background: #f6ffed;
  color: #52c41a;
}

.status-paused {
  background: #fff7e6;
  color: #fa8c16;
}

.status-pending {
  background: #f5f5f5;
  color: #8c8c8c;
}

.status-default {
  background: #f0f0f0;
  color: #666;
}

.project-menu .menu-icon {
  color: #bfbfbf;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.project-menu .menu-icon:hover {
  background: #f5f5f5;
  color: #1890ff;
}

.card-title {
  font-size: 17px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 8px;
  line-height: 1.4;
  letter-spacing: 0.3px;
}

.card-desc {
  font-size: 13px;
  color: #8c8c8c;
  margin-bottom: 16px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-info {
  background: #fafafa;
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
}

.info-row:not(:last-child) {
  border-bottom: 1px solid #f0f0f0;
}

.info-label {
  font-size: 12px;
  color: #8c8c8c;
}

.info-value {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #595959;
}

.info-value .el-icon {
  font-size: 14px;
  color: #1890ff;
}

.info-value.budget .el-icon {
  color: #52c41a;
}

.info-value.over-budget {
  color: #ff4d4f;
}

.info-value.over-budget .el-icon {
  color: #ff4d4f;
}

.card-progress {
  margin-bottom: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 13px;
  color: #595959;
}

.progress-value {
  font-weight: 600;
  font-size: 14px;
}

.progress-bar {
  height: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f5f5f5;
}

.cost-rate {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
}

.cost-rate.rate-good {
  background: #f6ffed;
  color: #52c41a;
}

.cost-rate.rate-warning {
  background: #fff7e6;
  color: #fa8c16;
}

.cost-rate.rate-danger {
  background: #fff2f0;
  color: #ff4d4f;
}

.rate-label {
  color: #8c8c8c;
}

.rate-value {
  font-weight: 600;
}

.days-left {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #8c8c8c;
}

.days-left .el-icon {
  font-size: 14px;
}

.chat-panel {
  width: 400px;
  height: 100%;
  background: white;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  border: 1px solid #e8e8e8;
  align-self: stretch;
}

.chat-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f5f5f5;
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 10px;
}

.chat-title .el-icon {
  color: #1890ff;
  font-size: 18px;
}

.chat-context {
  font-size: 13px;
  color: #8c8c8c;
}

.context-name {
  color: #1890ff;
  font-weight: 500;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.chat-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.chat-message {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.chat-message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  max-width: 78%;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 12px;
}

.chat-message.user .message-header {
  flex-direction: row-reverse;
}

.message-name {
  font-weight: 500;
  color: #262626;
}

.message-time {
  color: #bfbfbf;
}

.message-text {
  padding: 12px 14px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.6;
}

.chat-message.user .message-text {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.chat-message.assistant .message-text {
  background: #f5f5f5;
  color: #262626;
  border-bottom-left-radius: 4px;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 14px;
  background: #f5f5f5;
  border-radius: 14px;
}

.typing-indicator span {
  width: 7px;
  height: 7px;
  background: #bfbfbf;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-6px);
    opacity: 1;
  }
}

.chat-input {
  padding: 14px 16px;
  border-top: 1px solid #f5f5f5;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.quick-questions .el-tag {
  cursor: pointer;
  transition: all 0.2s;
  font-size: 12px;
}

.quick-questions .el-tag:hover {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}

.input-area {
  display: flex;
  gap: 8px;
}

.input-area .el-input {
  flex: 1;
}

.input-area .el-button {
  height: auto;
  padding: 0 14px;
}

.input-tip {
  font-size: 12px;
  color: #bfbfbf;
  margin-top: 6px;
  text-align: right;
}

::-webkit-scrollbar {
  width: 4px;
}

::-webkit-scrollbar-thumb {
  background: #d9d9d9;
  border-radius: 2px;
}

::-webkit-scrollbar-thumb:hover {
  background: #bfbfbf;
}
</style>
