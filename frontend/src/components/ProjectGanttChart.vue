<template>
  <div class="project-gantt-chart">
    <div class="gantt-header">
      <div class="project-info">
        <h4>{{ project.project_name }}</h4>
        <div class="project-meta">
          <span class="leader">负责人: {{ project.leader }}</span>
          <span class="status" :class="getStatusClass(project.status)">{{ project.status }}</span>
          <span class="progress">进度: {{ Math.round(project.progress) }}%</span>
        </div>
      </div>
      <div class="reports-info">
        <span class="weekly">本周日报: {{ reports_count.weekly }}篇</span>
        <span class="total">总计: {{ reports_count.total }}篇</span>
      </div>
    </div>

    <div class="gantt-timeline">
      <div class="timeline-header">
        <div class="task-column">任务名称</div>
        <div class="timeline-column">
          <div class="time-grid">
            <div 
              v-for="month in timeRange" 
              :key="month.key" 
              class="time-cell"
              :style="{ width: month.width + 'px' }"
            >
              {{ month.label }}
            </div>
          </div>
        </div>
      </div>

      <div class="task-rows">
        <div 
          v-for="(task, index) in tasks" 
          :key="task.task_id" 
          class="task-row"
        >
          <div class="task-info">
            <div class="task-name">{{ task.task_name }}</div>
            <div class="task-assignee">负责人: {{ task.assignee }}</div>
          </div>
          <div class="task-timeline">
            <div class="task-bar-container">
              <!-- 甘特图条 -->
              <div 
                class="task-bar"
                :class="getTaskStatusClass(task.status)"
                :style="getTaskBarStyle(task)"
              >
                <div class="task-progress" :style="{ width: task.progress + '%' }"></div>
                <div class="task-label">{{ task.status }} {{ Math.round(task.progress) }}%</div>
              </div>
              
              <!-- 风险点标记 -->
              <div 
                v-if="task.risk_level === '高风险'" 
                class="risk-marker high-risk"
                title="高风险任务"
              >
                ●
              </div>
              <div 
                v-else-if="task.risk_level === '中风险'" 
                class="risk-marker medium-risk"
                title="中风险任务"
              >
                ●
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="tasks.length === 0" class="no-tasks">
        暂无任务数据
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Task {
  task_id: string
  task_name: string
  assignee: string
  status: string
  progress: number
  planned_start_date?: string
  planned_end_date?: string
  actual_start_date?: string
  actual_end_date?: string
  risk_level: string
}

interface Project {
  project_id: string
  project_name: string
  leader: string
  start_date?: string
  end_date?: string
  progress: number
  status: string
}

interface ReportsCount {
  weekly: number
  total: number
}

interface Props {
  project: Project
  tasks: Task[]
  reports_count: ReportsCount
}

const props = defineProps<Props>()

// 计算时间范围
const timeRange = computed(() => {
  if (!props.project.start_date || !props.project.end_date) {
    return []
  }

  const start = new Date(props.project.start_date)
  const end = new Date(props.project.end_date)
  
  // 计算总天数
  const totalDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))
  const cellWidth = Math.max(50, Math.min(100, 400 / totalDays * 30)) // 动态计算宽度
  
  const months = []
  const current = new Date(start.getFullYear(), start.getMonth(), 1)
  
  while (current <= end) {
    const monthStart = new Date(current)
    const monthEnd = new Date(current.getFullYear(), current.getMonth() + 1, 0)
    
    const daysInMonth = Math.ceil((monthEnd.getTime() - monthStart.getTime()) / (1000 * 60 * 60 * 24)) + 1
    const width = daysInMonth * cellWidth
    
    months.push({
      key: current.toISOString().slice(0, 7), // YYYY-MM
      label: `${current.getFullYear()}年${current.getMonth() + 1}月`,
      width: width
    })
    
    current.setMonth(current.getMonth() + 1)
  }
  
  return months
})

// 获取任务条样式
const getTaskBarStyle = (task: Task) => {
  if (!props.project.start_date || !task.planned_start_date || !task.planned_end_date) {
    return {}
  }

  const projectStart = new Date(props.project.start_date)
  const taskStart = new Date(task.planned_start_date)
  const taskEnd = new Date(task.planned_end_date)
  
  // 计算任务开始位置
  const startOffset = Math.max(0, (taskStart.getTime() - projectStart.getTime()) / (1000 * 60 * 60 * 24))
  const duration = Math.max(1, (taskEnd.getTime() - taskStart.getTime()) / (1000 * 60 * 60 * 24))
  
  const totalWidth = timeRange.value.reduce((sum, month) => sum + month.width, 0)
  const cellWidth = totalWidth / timeRange.value.length * (30 / timeRange.value.length)
  
  return {
    left: (startOffset * cellWidth) + 'px',
    width: (duration * cellWidth) + 'px'
  }
}

// 获取状态样式类
const getStatusClass = (status: string) => {
  const statusMap: Record<string, string> = {
    '进行中': 'status-in-progress',
    '已完成': 'status-completed',
    '延期': 'status-delayed',
    '规划中': 'status-planning',
    '暂停': 'status-paused'
  }
  return statusMap[status] || 'status-unknown'
}

const getTaskStatusClass = (status: string) => {
  const statusMap: Record<string, string> = {
    '已完成': 'task-completed',
    '进行中': 'task-in-progress',
    '延期': 'task-delayed',
    '待开始': 'task-pending',
    '未开始': 'task-pending'
  }
  return statusMap[status] || 'task-unknown'
}
</script>

<style scoped>
.project-gantt-chart {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.gantt-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.project-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.project-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #666;
}

.project-meta .status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.reports-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  font-size: 12px;
  color: #666;
}

.timeline-header {
  display: flex;
  border-bottom: 1px solid #e8e8e8;
  margin-bottom: 8px;
}

.task-column {
  width: 200px;
  padding: 8px 12px;
  font-weight: 600;
  color: #262626;
  background: #fafafa;
  border-right: 1px solid #e8e8e8;
}

.timeline-column {
  flex: 1;
  position: relative;
}

.time-grid {
  display: flex;
  height: 32px;
}

.time-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: #666;
  border-right: 1px solid #f0f0f0;
  background: #fafafa;
}

.task-rows {
  max-height: 300px;
  overflow-y: auto;
}

.task-row {
  display: flex;
  border-bottom: 1px solid #f5f5f5;
  min-height: 48px;
  align-items: center;
}

.task-row:hover {
  background: #fafafa;
}

.task-info {
  width: 200px;
  padding: 8px 12px;
  border-right: 1px solid #e8e8e8;
}

.task-name {
  font-weight: 500;
  color: #262626;
  margin-bottom: 4px;
  font-size: 13px;
}

.task-assignee {
  font-size: 11px;
  color: #999;
}

.task-timeline {
  flex: 1;
  padding: 8px 12px;
  position: relative;
  min-height: 32px;
  display: flex;
  align-items: center;
}

.task-bar-container {
  position: relative;
  width: 100%;
  height: 24px;
}

.task-bar {
  position: absolute;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  font-size: 10px;
  color: white;
  font-weight: 500;
  overflow: hidden;
}

.task-completed {
  background: #52c41a;
}

.task-in-progress {
  background: #1890ff;
}

.task-delayed {
  background: #faad14;
}

.task-pending {
  background: #d9d9d9;
  color: #666;
}

.task-progress {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
}

.task-label {
  position: relative;
  z-index: 1;
}

.risk-marker {
  position: absolute;
  right: -15px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  cursor: pointer;
  z-index: 2;
}

.high-risk {
  color: #ff4d4f;
}

.medium-risk {
  color: #faad14;
}

.no-tasks {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 14px;
}

/* 状态样式 */
.status-in-progress {
  background: #e6f7ff;
  color: #1890ff;
}

.status-completed {
  background: #f6ffed;
  color: #52c41a;
}

.status-delayed {
  background: #fff2e8;
  color: #fa8c16;
}

.status-planning {
  background: #f0f5ff;
  color: #597ef7;
}

.status-paused {
  background: #fff1f0;
  color: #ff4d4f;
}

.status-unknown {
  background: #f5f5f5;
  color: #8c8c8c;
}

/* 滚动条样式 */
.task-rows::-webkit-scrollbar {
  width: 6px;
}

.task-rows::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.task-rows::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.task-rows::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>