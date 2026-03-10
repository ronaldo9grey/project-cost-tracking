<template>
  <div class="weekly-goal-panel">
    <!-- 本周目标卡片 -->
    <el-card v-if="weeklyGoal" shadow="hover" class="weekly-goal-card">
      <div class="goal-header">
        <div class="goal-title">
          <el-icon><Target /></el-icon>
          <span>本周目标</span>
        </div>
        <el-tag :type="getStatusType(weeklyGoal.status)" size="small">
          {{ getStatusText(weeklyGoal.status) }}
        </el-tag>
      </div>
      
      <div class="goal-content">
        <div class="monthly-goal-title">{{ monthlyGoal?.title }}</div>
        <div class="weekly-goal-title">第{{ weeklyGoal.week_number }}周：{{ weeklyGoal.title }}</div>
        <div class="goal-desc">{{ weeklyGoal.description || '暂无描述' }}</div>
      </div>
      
      <div class="goal-progress">
        <div class="progress-header">
          <span>当前进度</span>
          <span class="progress-value">{{ weeklyGoal.progress }}%</span>
        </div>
        <el-progress 
          :percentage="weeklyGoal.progress" 
          :status="weeklyGoal.progress === 100 ? 'success' : ''"
        />
      </div>
      
      <div class="goal-dates">
        <el-icon><Calendar /></el-icon>
        <span>{{ formatDate(weeklyGoal.start_date) }} 至 {{ formatDate(weeklyGoal.end_date) }}</span>
      </div>
    </el-card>
    
    <!-- 无本周目标时显示 -->
    <el-card v-else shadow="hover" class="weekly-goal-card empty">
      <el-empty description="暂无本周目标">
        <template #description>
          <p>暂无本周目标</p>
          <p class="sub-text">请在目标管理页面创建月度目标和周目标</p>
        </template>
        <el-button type="primary" size="small" @click="goToGoalManagement">
          前往创建
        </el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Target, Calendar } from '@element-plus/icons-vue'
import { getCurrentWeeklyGoal, type WeeklyGoalCurrent } from '@/api/goal'

const router = useRouter()

// 数据
const loading = ref(false)
const monthlyGoal = ref<WeeklyGoalCurrent['monthly_goal'] | null>(null)
const weeklyGoal = ref<WeeklyGoalCurrent['weekly_goal'] | null>(null)

// 状态显示
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    'pending': 'info',
    'in_progress': 'primary',
    'completed': 'success'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    'pending': '待开始',
    'in_progress': '进行中',
    'completed': '已完成'
  }
  return map[status] || status
}

// 格式化日期
const formatDate = (date: string) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

// 前往目标管理
const goToGoalManagement = () => {
  router.push('/monthly-goals')
}

// 加载本周目标
const loadCurrentWeeklyGoal = async () => {
  loading.value = true
  try {
    const res = await getCurrentWeeklyGoal()
    if (res && typeof res === 'object') {
      if ('monthly_goal' in res) {
        monthlyGoal.value = res.monthly_goal
        weeklyGoal.value = res.weekly_goal
      } else if ('data' in res) {
        monthlyGoal.value = res.data?.monthly_goal
        weeklyGoal.value = res.data?.weekly_goal
      }
    }
  } catch (error: any) {
    // 静默处理错误，不打扰用户
    console.log('加载本周目标失败:', error.message)
  } finally {
    loading.value = false
  }
}

// 初始化
onMounted(() => {
  loadCurrentWeeklyGoal()
})

// 暴露方法供父组件调用
defineExpose({
  loadCurrentWeeklyGoal,
  weeklyGoal
})
</script>

<style scoped lang="scss">
.weekly-goal-panel {
  width: 100%;
}

.weekly-goal-card {
  border-radius: 8px;
  
  :deep(.el-card__body) {
    padding: 16px;
  }
  
  &.empty {
    :deep(.el-card__body) {
      padding: 24px;
    }
    
    .sub-text {
      font-size: 12px;
      color: #909399;
      margin-top: 4px;
    }
  }
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  
  .goal-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 600;
    color: #1f2f3d;
    
    .el-icon {
      color: #1890ff;
      font-size: 18px;
    }
  }
}

.goal-content {
  margin-bottom: 12px;
  
  .monthly-goal-title {
    font-size: 14px;
    color: #1890ff;
    font-weight: 500;
    margin-bottom: 4px;
  }
  
  .weekly-goal-title {
    font-size: 15px;
    font-weight: 600;
    color: #1f2f3d;
    margin-bottom: 8px;
  }
  
  .goal-desc {
    font-size: 13px;
    color: #606266;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}

.goal-progress {
  margin-bottom: 12px;
  
  .progress-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
    font-size: 13px;
    color: #606266;
    
    .progress-value {
      font-weight: 600;
      color: #1890ff;
    }
  }
}

.goal-dates {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  
  .el-icon {
    font-size: 14px;
  }
}
</style>