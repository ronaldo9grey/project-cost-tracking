<template>
  <!-- 日报编辑页面模板保持不变 -->
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  getMyTasks,
  getMyReports,
  getDailyReport,
  createDailyReport,
  updateDailyReport,
  submitDailyReport,
  deleteDailyReport,
  type WorkItem,
  type DailyReportWithItems,
  type DailyReportCreate
} from '@/api/dailyReport'

// 页面状态
const router = useRouter()
const route = useRoute()
const saving = ref(false)
const loading = ref(false)
const isEdit = computed(() => !!route.params.id)
const reportId = computed(() => route.params.id as string)

// 工作事项数据
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
    evaluation: ''
  }
])

// 任务列表
const allTasks = ref<any[]>([])

// 表单数据
const reportForm = ref({
  work_target: '',
  key_work_tracking: '',
  tomorrow_plan: ''
})

// 保存方法
const saveDraft = async () => {
  saving.value = true
  try {
    // 获取用户信息
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
    const employeeId = currentUser.id || currentUser.employee_id || '5'
    const employeeName = currentUser.employee_name || currentUser.name || '陆宏东'
    
    // 转换工作事项为结构化数据
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
    
    // 计算总工时
    const totalHours = workItemsData.reduce((sum, item) => sum + (item.hours_spent || 0), 0)
    
    // 主表数据（只包含汇总信息）
    const reportData = {
      report_date: new Date().toISOString().split('T')[0], // 使用今天的日期
      employee_id: employeeId,
      employee_name: employeeName,
      tomorrow_plan: reportForm.value.tomorrow_plan || '',
      planned_hours: Math.round(totalHours * 100) / 100
    }
    
    // 如果有工作事项数据，使用新的接口
    if (workItemsData.length > 0) {
      const reportWithItems: DailyReportWithItems = {
        report: reportData,
        work_items: workItemsData
      }
      
      if (isEdit.value) {
        await updateDailyReport(parseInt(reportId.value), reportData)
        // 更新工作事项
        await updateWorkItems(parseInt(reportId.value), workItemsData)
      } else {
        const response = await createDailyReportWithItems(reportWithItems)
        console.log('创建成功:', response)
      }
    } else {
      // 如果没有工作事项，使用旧的保存方式
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
</script>

<style scoped>
/* 样式保持不变 */
</style>