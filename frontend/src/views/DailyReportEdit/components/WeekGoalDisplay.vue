<template>
  <div class="week-goal-display">
    <div class="goal-header">
      <el-icon><Flag /></el-icon>
      <span>月度目标概览</span>
      <el-tag size="small" type="primary">{{ month }}</el-tag>
    </div>

    <div class="month-title-section" v-if="monthTitle">
      <h4 class="month-title-text">{{ monthTitle }}</h4>
    </div>

    <div class="weekly-goals-list">
      <div
        v-for="(week, index) in weeklyGoals"
        :key="index"
        :class="['week-item', { 'current-week': week.week_number === currentWeekNumber }]"
      >
        <div class="week-header">
          <span class="week-number">第{{ week.week_number }}周</span>
          <el-tag v-if="week.week_number === currentWeekNumber" size="small" type="danger" effect="dark">当前</el-tag>
        </div>
        <div class="week-content">
          <p class="week-title">{{ week.title || '暂无目标' }}</p>
          <p v-if="week.content" class="week-desc">{{ week.content }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Flag } from '@element-plus/icons-vue'

interface WeeklyGoal {
  week_number: number
  title: string
  content?: string
}

interface Props {
  weeklyGoals: WeeklyGoal[]
  currentWeekNumber: number
  month?: string
  monthTitle?: string
}

defineProps<Props>()
</script>

<style scoped lang="scss">
.week-goal-display {
  background: linear-gradient(135deg, #f6ffed 0%, #f0f9ff 100%);
  border: 1px solid #b7eb8f;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.goal-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #52c41a;
  font-weight: 500;

  .el-icon {
    font-size: 18px;
  }
}

.month-title-section {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #d9d9d9;

  .month-title-text {
    margin: 0;
    font-size: 15px;
    color: #262626;
    font-weight: 600;
  }
}

.weekly-goals-list {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.week-item {
  background: #fafafa;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  padding: 12px;
  transition: all 0.3s;

  &.current-week {
    background: linear-gradient(135deg, #fff2f0 0%, #fff7e6 100%);
    border: 2px solid #ff4d4f;
    box-shadow: 0 2px 8px rgba(255, 77, 79, 0.15);
    transform: scale(1.02);
  }

  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
}

.week-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;

  .week-number {
    font-size: 13px;
    font-weight: 600;
    color: #595959;
  }
}

.week-content {
  .week-title {
    margin: 0 0 6px 0;
    font-size: 13px;
    color: #262626;
    font-weight: 500;
    line-height: 1.4;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }

  .week-desc {
    margin: 0;
    font-size: 12px;
    color: #8c8c8c;
    line-height: 1.4;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }
}

// 响应式布局
@media (max-width: 1200px) {
  .weekly-goals-list {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .weekly-goals-list {
    grid-template-columns: 1fr;
  }
}
</style>
