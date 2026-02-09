<template>
  <div class="task-flow-display">
    <div class="task-sequence">
      <!-- 前一个任务 -->
      <div v-if="prevTaskName" class="task-item prev-task">
        <div class="task-node" :class="getStatusClass(prevTaskStatus)">
          <div class="task-name">{{ prevTaskName }}</div>
          <div class="task-status">{{ getStatusText(prevTaskStatus) }}</div>
          <div v-if="taskAssignee" class="task-assignee">负责人：{{ taskAssignee }}</div>
        </div>
        <div class="task-connector">
          <el-icon class="connector-icon"><Right /></el-icon>
        </div>
      </div>
      
      <!-- 当前任务 -->
      <div v-if="currentTaskName" class="task-item current-task" :class="{'current-highlight': isCurrentTask}">
        <div class="task-node" :class="getCurrentTaskClass()">
          <div class="task-name">{{ currentTaskName }}</div>
          <div class="task-status">{{ getStatusText(currentTaskStatus) }}</div>
          <div v-if="taskAssignee" class="task-assignee">负责人：{{ taskAssignee }}</div>
          <div v-if="currentTaskProgress > 0" class="task-progress">
            <el-progress 
              :percentage="currentTaskProgress" 
              :stroke-width="3"
              :show-text="false"
              :color="getProgressColor(currentTaskProgress)"
            />
          </div>
          <div v-if="isCurrentTask" class="current-indicator">
            <el-icon class="pulse-icon"><MoreFilled /></el-icon>
            <span class="current-text">进行中</span>
          </div>
        </div>
      </div>
      
      <!-- 如果没有当前任务，显示最近完成的两个任务 -->
      <div v-else-if="!isCurrentTask && !currentTaskName" class="no-current-task">
        <div class="task-item completed-task">
          <div class="task-node completed">
            <div class="task-name">已完成任务</div>
            <div class="task-status">已完成</div>
            <div v-if="taskAssignee" class="task-assignee">负责人：{{ taskAssignee }}</div>
          </div>
        </div>
      </div>
      
      <!-- 后一个任务 -->
      <div v-if="nextTaskName" class="task-item next-task">
        <div class="task-connector">
          <el-icon class="connector-icon"><Right /></el-icon>
        </div>
        <div class="task-node" :class="getStatusClass(nextTaskStatus)">
          <div class="task-name">{{ nextTaskName }}</div>
          <div class="task-status">{{ getStatusText(nextTaskStatus) }}</div>
          <div v-if="taskAssignee" class="task-assignee">负责人：{{ taskAssignee }}</div>
        </div>
      </div>
      
      <!-- 如果没有任务流程，显示友好的提示信息 -->
      <div v-if="!prevTaskName && !currentTaskName && !nextTaskName" class="no-tasks-section">
        <div class="no-task-badge">
          <el-icon><DocumentRemove /></el-icon>
          <span>无任务分解</span>
        </div>
        <div class="task-node no-task-simple">
          <div class="task-status">项目尚未创建详细任务</div>
          <div v-if="taskAssignee" class="task-assignee">项目负责人：{{ taskAssignee }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Right, MoreFilled, User, DocumentRemove } from '@element-plus/icons-vue'

interface Props {
  prevTaskName?: string
  prevTaskStatus?: string
  currentTaskName?: string
  currentTaskStatus?: string
  currentTaskProgress?: number
  isCurrentTask?: boolean
  nextTaskName?: string
  nextTaskStatus?: string
  taskAssignee?: string
}

const props = withDefaults(defineProps<Props>(), {
  currentTaskProgress: 0,
  isCurrentTask: false
})

// 获取状态样式类
const getStatusClass = (status?: string) => {
  if (!status) return ''
  
  switch (status.toLowerCase()) {
    case '已完成':
    case 'completed':
      return 'completed'
    case '进行中':
    case 'in_progress':
      return 'in-progress'
    case '待开始':
    case 'pending':
      return 'pending'
    case '暂停':
    case 'paused':
      return 'paused'
    case '已取消':
    case 'cancelled':
      return 'cancelled'
    default:
      return 'unknown'
  }
}

// 获取当前任务样式类
const getCurrentTaskClass = () => {
  const baseClass = getStatusClass(props.currentTaskStatus)
  if (props.isCurrentTask) {
    return `${baseClass} current-active`
  }
  return baseClass
}

// 获取状态文本
const getStatusText = (status?: string) => {
  if (!status) return '未知'
  
  switch (status.toLowerCase()) {
    case '已完成':
    case 'completed':
      return '已完成'
    case '进行中':
    case 'in_progress':
      return '进行中'
    case '待开始':
    case 'pending':
      return '待开始'
    case '暂停':
    case 'paused':
      return '暂停'
    case '已取消':
    case 'cancelled':
      return '已取消'
    default:
      return status
  }
}

// 获取进度颜色
const getProgressColor = (progress: number) => {
  if (progress >= 80) return '#67c23a'
  if (progress >= 50) return '#e6a23c'
  if (progress >= 20) return '#f56c6c'
  return '#909399'
}
</script>

<style scoped>
.task-flow-display {
  width: 100%;
  padding: 8px 0;
}

.task-sequence {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.task-node {
  position: relative;
  min-width: 120px;
  max-width: 140px;
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  background: #fff;
  transition: all 0.3s ease;
}

.task-name {
  font-size: 12px;
  font-weight: 500;
  color: #303133;
  line-height: 1.2;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-status {
  font-size: 10px;
  color: #606266;
  line-height: 1.2;
}

.task-progress {
  margin-top: 4px;
}

.current-task {
  position: relative;
}

.current-task.current-highlight {
  animation: pulse 2s infinite;
}

.current-task.current-highlight .task-node.current-active {
  border-color: #409eff;
  background: linear-gradient(135deg, #e6f7ff 0%, #ffffff 100%);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.current-indicator {
  position: absolute;
  top: -8px;
  right: -8px;
  display: flex;
  align-items: center;
  gap: 2px;
  background: #409eff;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.3);
}

.pulse-icon {
  animation: spin 2s linear infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.8;
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 任务状态样式 */
.task-node.completed {
  background: #f0f9ff;
  border-color: #67c23a;
  color: #67c23a;
}

.task-node.in-progress {
  background: #fff7e6;
  border-color: #e6a23c;
  color: #e6a23c;
}

.task-node.pending {
  background: #f4f4f5;
  border-color: #909399;
  color: #909399;
}

.task-node.paused {
  background: #fef0f0;
  border-color: #f56c6c;
  color: #f56c6c;
}

.task-node.cancelled {
  background: #f5f5f5;
  border-color: #c0c4cc;
  color: #c0c4cc;
}

.task-node.unknown {
  background: #fafafa;
  border-color: #dcdfe6;
  color: #606266;
}

/* 连接器 */
.task-connector {
  display: flex;
  align-items: center;
  color: #c0c4cc;
}

.connector-icon {
  font-size: 14px;
}

/* 任务负责人信息 */
.task-assignee {
  font-size: 10px;
  color: #909399;
  margin-top: 2px;
  line-height: 1.2;
}

/* 无当前任务状态 */
.no-current-task {
  display: flex;
  align-items: center;
  gap: 8px;
}

.completed-task .task-node.completed {
  background: #f0f9ff;
  border-color: #67c23a;
  color: #67c23a;
}

/* 无任务状态 */
.no-tasks-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.no-task-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  background: #fdf6ec;
  border: 1px solid #f4b84a;
  border-radius: 12px;
  color: #d79b45;
  font-size: 10px;
  font-weight: 500;
  margin-bottom: 4px;
}

.no-task-badge .el-icon {
  color: #d79b45;
  font-size: 10px;
}

.task-node.no-task-simple {
  background: #f9f9f9;
  border: 1px dashed #e4e7ed;
  border-radius: 4px;
  padding: 4px 8px;
  text-align: center;
  width: 100%;
}

.task-node.no-task-simple .task-status {
  font-size: 11px;
  color: #c0c4cc;
  margin-bottom: 2px;
}

.task-node.no-task-simple .task-assignee {
  font-size: 10px;
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .task-node {
    min-width: 100px;
    max-width: 120px;
    padding: 6px 8px;
  }
  
  .task-name {
    font-size: 11px;
  }
  
  .task-status {
    font-size: 9px;
  }
}
</style>