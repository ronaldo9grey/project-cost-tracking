<template>
  <div class="gantt-chart-container">
    <!-- 甘特图表格 -->
    <el-table 
      :data="tasks" 
      border 
      style="width: 100%"
      class="gantt-table"
      :row-key="task => task.task_id"
      :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
    >
      <!-- 序号列 -->
      <el-table-column label="序号" width="80">
        <template #default="scope">
          {{ scope.$index + 1 }}
        </template>
      </el-table-column>
      
      <!-- 任务名称列 -->
      <el-table-column prop="task_name" label="任务名称" min-width="200" show-overflow-tooltip />
      
      <!-- 开始日期列 -->
      <el-table-column label="开始日期" width="150">
        <template #default="scope">
          {{ formatDate(scope.row.start_date) }}
        </template>
      </el-table-column>
      
      <!-- 计划结束日期列 -->
      <el-table-column label="计划结束日期" width="150">
        <template #default="scope">
          {{ formatDate(scope.row.end_date) }}
        </template>
      </el-table-column>
      
      <!-- 实际结束日期列 -->
      <el-table-column label="实际结束日期" width="150">
        <template #default="scope">
          {{ formatDate(scope.row.actual_end_date) }}
        </template>
      </el-table-column>
      
      <!-- 甘特图列 -->
      <el-table-column label="甘特图" min-width="800">
        <template #header>
          <!-- 甘特图列头显示时间轴 -->
          <div class="gantt-column-header">
            <div class="gantt-column-title">甘特图</div>
            <div 
              class="gantt-timeline-container"
              ref="timelineContainer"
              @scroll="syncScroll"
            >
              <div class="gantt-timeline">
                <div 
                  v-for="month in timelineMonths" 
                  :key="month.month" 
                  class="timeline-month"
                >
                  {{ month.month }}
                </div>
              </div>
            </div>
          </div>
        </template>
        <template #default="scope">
          <!-- 甘特图条 -->
          <div class="gantt-bars-container">
            <!-- 差异天数显示 -->
            <div 
              class="gantt-diff"
              :class="{
                'diff-normal': calculateDaysDifference(scope.row) === 0,
                'diff-positive': calculateDaysDifference(scope.row) < 0,
                'diff-negative': calculateDaysDifference(scope.row) > 0
              }"
            >
              <span class="diff-value">
                {{ `${calculateDaysDifference(scope.row) > 0 ? '+' : ''}${calculateDaysDifference(scope.row)}天` }}
              </span>
            </div>
            <div class="gantt-bar planned" :style="getGanttBarStyle(scope.row, true)"></div>
            <div 
              class="gantt-bar actual" 
              :style="getGanttBarStyle(scope.row, false)"
            ></div>
          </div>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 甘特图滚动同步容器 -->
    <div 
      class="gantt-sync-container"
      ref="syncContainer"
      @scroll="syncScroll"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'

// 任务数据类型
interface Task {
  task_id: string
  task_name: string
  start_date: string
  end_date: string
  actual_end_date?: string | null
  parent_task_id?: string
  hasChildren?: boolean
  children?: Task[]
}

// 时间线月份类型
interface TimelineMonth {
  month: string
  startDate: Date
  endDate: Date
}

// 属性定义
const props = defineProps<{
  tasks: Task[]
}>()

// 引用用于同步滚动的DOM元素
const timelineContainer = ref<HTMLElement | null>(null)
const syncContainer = ref<HTMLElement | null>(null)

// 同步滚动函数
const syncScroll = (event: Event) => {
  const target = event.target as HTMLElement
  const scrollLeft = target.scrollLeft
  
  // 获取表格的滚动容器
  const tableContainer = document.querySelector('.el-table__body-wrapper') as HTMLElement
  if (!tableContainer) return
  
  // 同步滚动位置
  if (target === timelineContainer.value) {
    // 滚动时间轴时，同步表格内容
    tableContainer.scrollLeft = scrollLeft
  } else if (target === tableContainer) {
    // 滚动表格内容时，同步时间轴
    if (timelineContainer.value) {
      timelineContainer.value.scrollLeft = scrollLeft
    }
  }
}

// 递归获取所有任务（包括子任务）
const getAllTasks = (tasks: Task[]): Task[] => {
  return tasks.flatMap(task => {
    return [task, ...(task.children ? getAllTasks(task.children) : [])]
  })
}

// 计算项目的开始和结束日期
const projectStartDate = computed(() => {
  const allTasks = getAllTasks(props.tasks)
  if (allTasks.length === 0) return new Date()
  return new Date(Math.min(...allTasks.map(task => new Date(task.start_date).getTime())))
})

const projectEndDate = computed(() => {
  const allTasks = getAllTasks(props.tasks)
  if (allTasks.length === 0) return new Date()
  
  // 同时考虑计划结束日期和实际结束日期
  return new Date(Math.max(...allTasks.flatMap(task => {
    const dates = [new Date(task.end_date).getTime()]
    if (task.actual_end_date) {
      dates.push(new Date(task.actual_end_date).getTime())
    }
    return dates
  })))
})

// 生成时间线月份
const timelineMonths = ref<TimelineMonth[]>([])

// 初始化时间线
onMounted(() => {
  generateTimeline()
})

// 生成时间线
const generateTimeline = () => {
  const start = new Date(projectStartDate.value)
  const end = new Date(projectEndDate.value)
  
  // 调整到月份开始
  start.setDate(1)
  start.setHours(0, 0, 0, 0)
  
  // 调整到月份结束
  end.setMonth(end.getMonth() + 1)
  end.setDate(0)
  end.setHours(23, 59, 59, 999)
  
  const months: TimelineMonth[] = []
  let currentMonth = new Date(start)
  
  while (currentMonth <= end) {
    const monthLabel = `${currentMonth.getFullYear()}-${String(currentMonth.getMonth() + 1).padStart(2, '0')}`
    
    // 记录当前月的开始和结束日期
    const monthStartDate = new Date(currentMonth)
    const monthEndDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0)
    
    months.push({
      month: monthLabel,
      startDate: monthStartDate,
      endDate: monthEndDate
    })
    
    // 移动到下一个月
    currentMonth.setMonth(currentMonth.getMonth() + 1)
  }
  
  timelineMonths.value = months
}

// 格式化日期
const formatDate = (date: Date | string | null) => {
  if (!date) return ''
  const d = typeof date === 'string' ? new Date(date) : date
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

// 计算计划和实际结束日期的差异天数
const calculateDaysDifference = (task: Task) => {
  const plannedEnd = new Date(task.end_date)
  const actualEnd = task.actual_end_date ? new Date(task.actual_end_date) : new Date() // 实际结束日期为空时用当前日期
  
  // 计算天数差异（实际 - 计划）
  const diffTime = actualEnd.getTime() - plannedEnd.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  return diffDays
}

// 计算甘特图条样式
const getGanttBarStyle = (task: Task, isPlanned: boolean) => {
  const startDate = new Date(task.start_date)
  const endDate = isPlanned 
    ? new Date(task.end_date) 
    : task.actual_end_date 
      ? new Date(task.actual_end_date) 
      : new Date() // 如果实际结束日期为空，使用当前日期
  
  // 计算项目总天数
  const totalDays = Math.ceil((projectEndDate.value.getTime() - projectStartDate.value.getTime()) / (1000 * 60 * 60 * 24)) + 1
  
  // 计算任务开始和结束日期在项目中的位置
  const taskStartOffset = Math.ceil((startDate.getTime() - projectStartDate.value.getTime()) / (1000 * 60 * 60 * 24))
  const taskDuration = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1
  
  // 计算时间轴总宽度（每个月120px）
  const timelineTotalWidth = timelineMonths.value.length * 120
  
  // 根据天数比例计算甘特图条的位置和宽度（基于像素）
  const dayWidth = timelineTotalWidth / totalDays
  const left = `${taskStartOffset * dayWidth}px`
  const width = `${taskDuration * dayWidth}px`
  
  return {
    left,
    width
  }
}
</script>

<style scoped>
.gantt-chart-container {
  width: 100%;
  background-color: #fff;
}

/* 甘特图表格样式 */
.gantt-table {
  min-width: 1200px;
}

/* 移除单元格内边距，让甘特图条占满整个单元格 */
.gantt-table .el-table__cell {
  padding: 0;
}

/* 甘特图列头样式 */
.gantt-column-header {
  display: flex;
  flex-direction: column;
  width: 100%;
  overflow: hidden;
}

.gantt-column-title {
  font-weight: bold;
  margin-bottom: 10px;
}

.gantt-timeline-container {
  overflow-x: auto;
  width: 100%;
  overflow-y: hidden;
  scrollbar-width: thin;
  scrollbar-color: #409eff #e4e7ed;
}

.gantt-timeline-container::-webkit-scrollbar {
  height: 6px;
}

.gantt-timeline-container::-webkit-scrollbar-track {
  background: #e4e7ed;
}

.gantt-timeline-container::-webkit-scrollbar-thumb {
  background: #409eff;
  border-radius: 3px;
}

.gantt-timeline-container::-webkit-scrollbar-thumb:hover {
  background: #66b1ff;
}

.gantt-timeline {
  display: flex;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  height: 30px;
  align-items: center;
  margin-bottom: 10px;
  min-width: 100%;
  width: fit-content;
}

.timeline-month {
  flex: 0 0 120px;
  text-align: center;
  font-weight: bold;
  font-size: 12px;
  border-right: 1px solid #e4e7ed;
  white-space: nowrap;
}

/* 甘特图条容器 */
.gantt-bars-container {
  position: relative;
  height: 80px;
  background-color: #fafafa;
  min-width: 800px;
  width: fit-content;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  padding: 10px 0;
  padding-left: 80px; /* 为差异天数留出空间 */
}

/* 差异天数样式 */
.gantt-diff {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px 15px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: fit-content;
  z-index: 3;
}

/* 甘特图条样式 */
.gantt-bar {
  position: relative;
  height: 25px;
  border-radius: 3px;
  transition: all 0.3s;
  opacity: 0.8;
  width: 100%;
}

.gantt-bar.planned {
  background-color: #67c23a;
  z-index: 1;
  margin-bottom: 5px;
}

.gantt-bar.actual {
  background-color: #409eff;
  z-index: 2;
}

.gantt-bar:hover {
  opacity: 1;
  transform: scaleY(1.1);
}

.gantt-diff.diff-normal {
  background-color: #ecf5ff;
  color: #409eff;
}

.gantt-diff.diff-positive {
  background-color: #f0f9eb;
  color: #67c23a;
}

.gantt-diff.diff-negative {
  background-color: #fef0f0;
  color: #f56c6c;
}

.diff-value {
  font-size: 14px;
}

/* 滚动同步容器（隐藏） */
.gantt-sync-container {
  display: none;
}
</style>