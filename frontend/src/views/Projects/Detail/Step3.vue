<template>
  <div class="project-create-container">
    <el-card shadow="hover" class="project-create-card">
      <template #header>
        <div class="card-header">
          <h2>项目详情 - 任务设定</h2>
          <el-breadcrumb separator="/" separator-class="el-icon-arrow-right">
            <el-breadcrumb-item :to="{ path: '/projects' }">项目管理</el-breadcrumb-item>
            <el-breadcrumb-item>项目详情</el-breadcrumb-item>
            <el-breadcrumb-item>任务设定</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
      </template>
      
      <!-- 步骤指示器 -->
      <el-steps :active="2" align-center>
        <el-step title="基本信息" description="查看项目基本信息和合同信息" />
        <el-step title="成本设定" description="查看四大成本设置" />
        <el-step title="任务设定" description="查看项目任务设置" />
        <el-step title="文档管理" description="查看项目文档" />
      </el-steps>
      
      <div class="gantt-container">
        <!-- 任务管理标题和操作 -->
        <div class="panel-header">
          <h3>任务管理</h3>
        </div>
        
        <!-- 任务管理和甘特图合并表格 -->
        <!-- 使用Element Plus的树形表格功能，通过tree-props配置 -->
        <el-table 
          :data="treeTasks" 
          border 
          fit
          style="width: 100%" 
          class="task-gantt-table"
          :key="treeDataKey"
          row-key="task_id"
        >

          <!-- 序号列（第一列） -->
          <el-table-column label="序号" width="100">
            <template #default="scope">
              {{ scope.row.task_id.replace(`${projectId}_`, '') }}
            </template>
          </el-table-column>
          <!-- 任务名称列（第二列自动显示缩进和展开/折叠图标） -->
          <el-table-column prop="task_name" label="任务名称" min-width="160" show-overflow-tooltip :tree-props="{ children: 'children', hasChildren: 'hasChildren' }" />
          <el-table-column label="状态" width="120">
            <template #default="scope">
              <el-tag :type="getProgressStatusType(getProgressStatus(scope.row))">
                {{ getProgressStatus(scope.row) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="assignee" label="资源分配" min-width="90" show-overflow-tooltip />
          <el-table-column label="开始日期" width="120">
            <template #default="scope">
              {{ formatDate(scope.row.start_date) }}
            </template>
          </el-table-column>
          <el-table-column label="计划结束日期" width="120">
            <template #default="scope">
              {{ formatDate(scope.row.end_date) }}
            </template>
          </el-table-column>
          <el-table-column label="实际结束日期" width="120">
            <template #default="scope">
              {{ formatDate(scope.row.actual_end_date) }}
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button @click="goBack">返回项目列表</el-button>
          <el-button @click="handlePrevious">查看上一步</el-button>
          <el-button type="primary" @click="handleNext">查看下一步</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

// 获取项目ID
const projectId = computed(() => route.params.id as string)

// 任务数据
const tasks = ref<any[]>([])
const treeDataKey = ref(0)

// 计算属性：树形任务数据
const treeTasks = computed(() => {
  // 构建父子关系
  const taskMap = new Map()
  const rootTasks = []
  
  // 首先创建任务映射
  tasks.value.forEach(task => {
    task.children = []
    taskMap.set(task.task_id, task)
  })
  
  // 然后构建树形结构
  tasks.value.forEach(task => {
    if (task.parent_task_id) {
      const parent = taskMap.get(task.parent_task_id)
      if (parent) {
        parent.children.push(task)
      }
    } else {
      rootTasks.push(task)
    }
  })
  
  return rootTasks
})

// 获取任务进度状态
const getProgressStatus = (task: any) => {
  if (task.actual_end_date && task.actual_end_date !== '') {
    return '已完成'
  } else if (task.start_date && new Date(task.start_date) <= new Date()) {
    return '进行中'
  } else {
    return '未开始'
  }
}

// 获取进度状态对应的标签类型
const getProgressStatusType = (status: string) => {
  switch (status) {
    case '已完成':
      return 'success'
    case '进行中':
      return 'primary'
    case '已暂停':
      return 'warning'
    case '未开始':
      return 'info'
    default:
      return 'info'
  }
}

// 格式化日期
const formatDate = (date: string | null) => {
  if (!date) return '-'
  try {
    return new Date(date).toLocaleDateString('zh-CN')
  } catch {
    return '-'
  }
}

// 获取项目任务数据
const fetchProjectTasks = async () => {
  try {
    // 这里应该调用获取项目任务的API
    // 目前先使用模拟数据
    tasks.value = [
      {
        task_id: `${projectId}_1`,
        task_name: '项目规划',
        parent_task_id: null,
        start_date: '2024-01-01',
        end_date: '2024-01-15',
        actual_end_date: '2024-01-14',
        assignee: '张三',
        status: '已完成'
      },
      {
        task_id: `${projectId}_2`,
        task_name: '需求分析',
        parent_task_id: `${projectId}_1`,
        start_date: '2024-01-02',
        end_date: '2024-01-08',
        actual_end_date: '2024-01-07',
        assignee: '李四',
        status: '已完成'
      },
      {
        task_id: `${projectId}_3`,
        task_name: '系统设计',
        parent_task_id: `${projectId}_1`,
        start_date: '2024-01-09',
        end_date: '2024-01-15',
        actual_end_date: null,
        assignee: '王五',
        status: '进行中'
      },
      {
        task_id: `${projectId}_4`,
        task_name: '前端开发',
        parent_task_id: null,
        start_date: '2024-01-16',
        end_date: '2024-02-15',
        actual_end_date: null,
        assignee: '赵六',
        status: '未开始'
      }
    ]
    
    // 重新渲染树形表格
    treeDataKey.value++
  } catch (error) {
    console.error('获取项目任务数据失败:', error)
    ElMessage.error('获取项目任务数据失败')
  }
}

// 跳转到上一步
const handlePrevious = () => {
  router.push({
    name: 'ProjectDetailBasic',
    params: { id: projectId.value }
  })
}

// 跳转到下一步
const handleNext = () => {
  router.push({
    name: 'ProjectDetailDocuments',
    params: { id: projectId.value }
  })
}

// 返回项目列表
const goBack = () => {
  router.push('/projects')
}

// 初始化
onMounted(() => {
  fetchProjectTasks()
})
</script>

<style scoped>
.project-create-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.project-create-card {
  margin: 0 auto;
  max-width: 1600px;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.gantt-container {
  margin-top: 30px;
  width: 100%;
  overflow-x: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #fff;
  border-radius: 8px 8px 0 0;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 甘特图列时间轴样式 */
.gantt-column-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 5px;
}

.gantt-column-time-axis {
  display: flex;
  overflow-x: auto;
  width: 100%;
  gap: 0;
}

.gantt-column-time-item {
  min-width: 80px;
  text-align: center;
  font-size: 10px;
  font-weight: bold;
  color: #606266;
  white-space: nowrap;
  padding: 2px 0;
  border-right: 1px solid #e4e7ed;
  background-color: #f5f7fa;
}

/* 合并表格样式 */
.task-gantt-table {
  margin-bottom: 0;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  width: 100%;
  min-width: 1300px;
}

/* 表格中甘特图列样式 */
.table-gantt-bar-container {
  width: 100%;
  height: 40px;
  display: flex;
  align-items: center;
  padding: 0 10px;
  background-color: #fafafa;
}

.table-gantt-bar {
  flex: 1;
  height: 24px;
  background-color: #409eff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  position: relative;
  cursor: pointer;
  transition: all 0.3s;
  overflow: hidden;
}

.table-gantt-bar:hover {
  opacity: 0.8;
  transform: scaleY(1.1);
}

.table-gantt-progress {
  height: 100%;
  background-color: rgba(255, 255, 255, 0.3);
  transition: width 0.3s ease;
}

/* 任务状态样式 */
.task-status-已完成 {
  background-color: #67c23a !important;
}

.task-status-进行中 {
  background-color: #409eff !important;
}

.task-status-已暂停 {
  background-color: #e6a23c !important;
}

.task-status-未开始 {
  background-color: #909399 !important;
}

.progress-value {
  text-align: center;
  margin-top: 10px;
  font-weight: bold;
  color: #409EFF;
}

/* 任务名称缩进样式 */
.task-name-wrapper {
  display: flex;
  align-items: center;
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-indent {
  display: inline-block;
}

.task-child-icon {
  margin-right: 5px;
  color: #909399;
  font-weight: bold;
}

.task-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
  padding: 20px 0;
  border-top: 1px solid #e4e7ed;
  background-color: #fafafa;
}

:deep(.el-steps) {
  margin: 30px 0;
}

/* 修改非当前步骤的文字颜色为蓝色 */
:deep(.el-step__title) {
  color: #409EFF !important;
}

:deep(.el-step__description) {
  color: #409EFF !important;
}

/* 当前步骤使用默认颜色 */
:deep(.el-step.is-success .el-step__title),
:deep(.el-step.is-success .el-step__description),
:deep(.el-step.is-active .el-step__title),
:deep(.el-step.is-active .el-step__description) {
  color: inherit !important;
}

/* 甘特图对话框样式 */
.gantt-dialog-content {
  height: calc(100vh - 150px);
  overflow: auto;
}

.gantt-table-container {
  margin: 20px 0;
  width: 100%;
}
</style>