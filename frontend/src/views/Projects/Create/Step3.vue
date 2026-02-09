<template>
  <div class="project-create-container">
    <el-card shadow="hover" class="project-create-card">
      <template #header>
        <div class="card-header">
          <h2>{{ (isEditMode ? '编辑项目' : '新建项目') + (projectName ? ' - ' + projectName : '') }} - 任务设定</h2>
          <el-breadcrumb separator="/" separator-class="el-icon-arrow-right">
            <el-breadcrumb-item :to="{ path: '/projects' }">项目管理</el-breadcrumb-item>
            <el-breadcrumb-item>{{ (isEditMode ? '编辑项目' : '新建项目') + (projectName ? ' - ' + projectName : '') }}</el-breadcrumb-item>
            <el-breadcrumb-item>任务设定</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
      </template>
      
      <!-- 步骤指示器 -->
      <el-steps :active="2" align-center>
        <el-step title="基本信息" description="设置项目基本信息和合同信息" />
        <el-step title="成本设定" description="设置四大成本的预算和实际值" />
        <el-step title="任务设定" description="创建项目任务" />
        <el-step title="文档管理" description="管理项目相关文档" />
      </el-steps>
      
      <div class="gantt-container">
        <!-- 任务管理标题和操作 -->
        <div class="panel-header">
          <h3>任务管理</h3>
          <div class="panel-actions">
                <el-button type="info" @click="openGanttDialog">
                  <el-icon><DataAnalysis /></el-icon>
                  甘特图展示
                </el-button>
                <el-button type="success" @click="openCaseReference">
                  <el-icon><Document /></el-icon>
                  案例参照
                </el-button>
                <el-button type="primary" @click="openTaskDialog">
                  <el-icon><Plus /></el-icon>
                  新增任务
                </el-button>
                <el-button @click="isEditMode ? importTasksInEditMode() : importTasks()">
                  <el-icon><Upload /></el-icon>
                  导入任务
                </el-button>
              </div>
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

          <el-table-column label="操作" width="260" fixed="right">
            <template #default="scope">
              <el-button type="primary" size="small" @click="editTask(scope.row)">
                <el-icon><EditPen /></el-icon>
                编辑
              </el-button>
              <el-button type="success" size="small" @click="addSubTask(scope.row)">
                <el-icon><Plus /></el-icon>
                子任务
              </el-button>
              <el-button type="danger" size="small" @click="deleteTask(scope.row)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button @click="handlePrevious">上一步</el-button>
          <el-button type="primary" @click="handleNext">进入下一步</el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 任务对话框 -->
    <el-dialog
      v-model="taskDialogVisible"
      :title="taskDialogTitle"
      width="800px"
    >
      <el-form ref="taskForm" :model="taskFormData" label-width="120px" :rules="taskRules">
        <!-- 第一部分：基本信息组 -->
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="任务名称" prop="task_name">
              <el-input v-model="taskFormData.task_name" placeholder="请输入任务名称" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="当前状态" prop="status">
              <el-select v-model="taskFormData.status" placeholder="请选择状态" disabled>
                <el-option label="未开始" value="未开始" />
                <el-option label="进行中" value="进行中" />
                <el-option label="已完成" value="已完成" />
                <el-option label="已暂停" value="已暂停" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="资源分配" prop="assignee">
              <el-select 
                v-model="taskFormData.assignee" 
                placeholder="请选择人员（可多选）"
                multiple
                collapse-tags
              >
                <el-option
                  v-for="personnel in personnelList"
                  :key="personnel.id"
                  :label="personnel.name"
                  :value="personnel.name"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="实际结束日期" prop="actual_end_date">
              <el-date-picker
                v-model="taskFormData.actual_end_date"
                type="date"
                placeholder="选择实际结束日期"
                style="width: 100%;"
                disabled
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期" prop="start_date">
              <el-date-picker
                v-model="taskFormData.start_date"
                type="date"
                placeholder="选择开始日期"
                style="width: 100%;"
                @change="calculatePlannedHours"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计划结束日期" prop="end_date">
              <el-date-picker
                v-model="taskFormData.end_date"
                type="date"
                placeholder="选择计划结束日期"
                style="width: 100%;"
                @change="calculatePlannedHours"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 第二部分：进度信息组 -->
        <el-divider content-position="left">进度信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="计划工时（小时）" prop="planned_hours">
              <el-input v-model="taskFormData.planned_hours" placeholder="自动计算" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实际工时（小时）" prop="actual_hours">
              <el-input v-model="taskFormData.actual_hours" placeholder="自动计算" readonly />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 第三部分：说明信息组 -->
        <el-divider content-position="left">说明信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="考评" prop="evaluation">
              <el-input 
                v-model="taskFormData.evaluation" 
                placeholder="请输入考评分数"
                type="number"
                :step="0.1"
                :min="0"
                :max="100"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="考评说明" prop="evaluation_desc">
              <el-input 
                v-model="taskFormData.evaluation_desc" 
                placeholder="请输入考评说明"
                type="textarea"
                :rows="2"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="进展/根因" prop="progress_rootcause">
              <el-input 
                v-model="taskFormData.progress_rootcause" 
                placeholder="请输入进展/根因"
                type="textarea"
                :rows="2"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="措施/结果" prop="measures_results">
              <el-input 
                v-model="taskFormData.measures_results" 
                placeholder="请输入措施/结果"
                type="textarea"
                :rows="2"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="备注" prop="remark">
              <el-input 
                v-model="taskFormData.remark" 
                placeholder="请输入备注"
                type="textarea"
                :rows="2"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="taskDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveTask">保存</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 甘特图展示对话框 -->
    <el-dialog
      v-model="ganttDialogVisible"
      title="甘特图展示"
      width="90%"
      fullscreen
    >
      <div class="gantt-dialog-content">
        <!-- 甘特图内容将在这里展示 -->
        <div class="gantt-table-container">
          <!-- 使用新的甘特图组件 -->
          <gantt-chart :tasks="treeTasks" />
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="ganttDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 案例参照对话框 -->
    <el-dialog
      v-model="caseDialogVisible"
      title="某厂脱硫系统浆液循环泵节能研发项目案例"
      width="90%"
      top="20px"
    >
      <div class="case-dialog-content">
        <!-- 案例说明 -->
        <div class="case-introduction">
          <h4>案例介绍</h4>
          <p>这是一个脱硫系统浆液循环泵节能技术研发项目的完整案例，展示了标准的项目任务分解结构和管理流程。</p>
          
          <h5>角色化与精细化</h5>
          <p>此表实现了角色负责制和工作精细化管理。每个任务都明确了职能角色，且最底层工作包持续时间基本控制在1周（5个工作日）左右，最长不超过2周，合用于周报跟踪和进度协调会。</p>
          
          <h5>逻辑清晰</h5>
          <p>通过"前置任务"列，明确了工作流的依赖关系，可以用于生成关键路径，识别瓶颈。</p>
          
          <h5>直接可用</h5>
          <p>此表格可直接复制到Excel中，作为项目计划的主数据表。您可以使用Excel的筛选、排序和条件格式功能进行管理，也可以将其导入MS Project等专业工具生成甘特图。</p>
          
          <h5>动态管理</h5>
          <p>在实际使用中，只需定期更新"状态"、"实际完成时间"、"进展/根因"、"措施/结果"等列，即可动态反映项目状况。</p>
          
          <div class="case-stats">
            <div class="stat-item">
              <span class="stat-label">项目周期:</span>
              <span class="stat-value">6个月</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">任务数量:</span>
              <span class="stat-value">148个任务</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">项目复杂度:</span>
              <span class="stat-value">高</span>
            </div>
          </div>
        </div>
        
        <!-- 案例任务列表展示 -->
        <div class="case-tasks-section">
          <h4>案例任务分解</h4>
          <div class="case-tasks-container">
            <el-table 
              :data="caseTasks" 
              border 
              style="width: 100%"
              class="case-tasks-table"
              height="500"
              :row-class-name="getRowClassName"
            >
              <!-- 项目名称/结果/过程/要素 -->
              <el-table-column label="项目名称/结果/过程/要素" min-width="300" show-overflow-tooltip>
                <template #default="scope">
                  <span :class="getTaskNameClass(scope.row['项目名称/结果/过程/要素'])">
                    {{ formatTaskName(scope.row['项目名称/结果/过程/要素']) }}
                  </span>
                </template>
              </el-table-column>
              
              <!-- 负责人(角色) -->
              <el-table-column prop="负责人(角色)" label="负责人(角色)" width="120" />
              
              <!-- 状态 -->
              <el-table-column prop="状态" label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="getStatusType(scope.row['状态'])" size="small">
                    {{ scope.row['状态'] }}
                  </el-tag>
                </template>
              </el-table-column>
              
              <!-- 开始日期 -->
              <el-table-column prop="开始日期" label="开始日期" width="120" />
              
              <!-- 持续时间(天) -->
              <el-table-column prop="持续时间(天)" label="持续时间(天)" width="100" />
              
              <!-- 计划完成时间 -->
              <el-table-column prop="计划完成时间" label="计划完成时间" width="120" />
              
              <!-- 实际完成时间 -->
              <el-table-column prop="实际完成时间" label="实际完成时间" width="120" />
              
              <!-- 前置任务 -->
              <el-table-column prop="前置任务" label="前置任务" width="100" />
              
              <!-- 详细工作说明/交付物 -->
              <el-table-column prop="详细工作说明/交付物" label="详细工作说明/交付物" min-width="400" show-overflow-tooltip />
            </el-table>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="downloadCaseExcel">
            <el-icon><Download /></el-icon>
            下载案例Excel
          </el-button>
          <el-button @click="caseDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, EditPen, Delete, DataAnalysis, Document, Download } from '@element-plus/icons-vue'
// 不再需要甘特图组件
import { getPersonnel, type Personnel } from '../../../api/resource'
import { getProjectTasks, getProjectDetail } from '../../../api/project'

const router = useRouter()
const route = useRoute()

// 项目ID计算属性
const projectId = computed(() => {
  // 优先从query参数获取（新建流程）
  const queryId = route.query.projectId
  if (queryId) {
    const parsed = parseInt(String(queryId), 10)
    return isNaN(parsed) ? 0 : parsed
  }
  // 回退到params参数（编辑流程）
  const paramsId = route.params.projectId
  if (paramsId) {
    const parsed = parseInt(String(paramsId), 10)
    return isNaN(parsed) ? 0 : parsed
  }
  return 0
})

// 获取模式参数 - 从查询参数获取，优先从query参数获取（新建流程）
const mode = computed(() => {
  // 优先从query参数获取（新建流程）
  const queryMode = route.query.mode
  if (queryMode) {
    return String(queryMode)
  }
  // 回退到params参数（编辑流程）
  const paramsMode = route.params.mode
  if (paramsMode) {
    return String(paramsMode)
  }
  return ''
})

// 判断是否为编辑模式
const isEditMode = computed(() => {
  return mode.value === 'edit'
})

// 项目名称
const projectName = ref<string>('')

// 人员列表数据
const personnelList = ref<Personnel[]>([])

// 项目任务数据
const projectTasks = ref<any[]>([])



// 用于触发表格重新渲染的key
const treeDataKey = ref(0)

// 甘特图对话框
const ganttDialogVisible = ref(false)

// 案例参照对话框
const caseDialogVisible = ref(false)

// 案例任务数据
const caseTasks = ref<any[]>([])

// 案例Excel文件路径
const caseExcelUrl = '/data/case-reference/项目进度案例.xlsx'

// 树形结构的任务列表，用于展开/折叠功能
const treeTasks = computed(() => {
  // 创建任务ID到任务对象的映射
  const taskMap = new Map<string, any>()
  const rootTasks: any[] = []
  
  // 首先将所有任务放入映射中，确保每个任务都有children数组
  projectTasks.value.forEach(task => {
    const taskWithChildren = {
      ...task,
      children: [] as any[],
      hasChildren: false
    }
    // 检查任务是否有子任务
    taskWithChildren.hasChildren = projectTasks.value.some(t => t.parent_task_id === task.task_id)
    taskMap.set(task.task_id, taskWithChildren)
  })
  
  // 然后构建树形结构
  projectTasks.value.forEach(task => {
    if (task.parent_task_id && taskMap.has(task.parent_task_id)) {
      // 如果有父任务，将其添加到父任务的children数组中
      const parentTask = taskMap.get(task.parent_task_id)
      const childTask = taskMap.get(task.task_id)
      parentTask.children.push(childTask)
      // 确保父任务的hasChildren属性为true
      parentTask.hasChildren = true
    } else {
      // 没有父任务的是根任务
      rootTasks.push(taskMap.get(task.task_id))
    }
  })
  
  return rootTasks
})



// 任务对话框
const taskDialogVisible = ref(false)
const taskDialogTitle = ref('新增任务')
const taskForm = ref()
// 任务表单数据
const taskFormData = ref({
  task_id: '',
  project_id: projectId.value,
  task_name: '',
  parent_task_id: '',
  task_level: 1,
  assignee: [] as string[],
  assignee_id: '',
  start_date: '',
  end_date: '',
  actual_end_date: null,
  status: '未开始',
  progress: 0,
  planned_hours: 0,
  actual_hours: 0,
  evaluation: '',
  evaluation_desc: '',
  progress_rootcause: '',
  measures_results: '',
  remark: '',
  leaf_node: 1,
  hasChildren: false,
  created_by: 'current_user'
})

// 任务状态跟踪，用于编辑场景
// 记录哪些任务是新增的、修改的、删除的
const taskStatusTracking = ref({
  // 新增的任务ID列表
  added: [] as string[],
  // 修改的任务ID列表
  updated: [] as string[],
  // 删除的任务ID列表
  deleted: [] as string[],
  // 原始任务列表，用于比较差异
  originalTasks: [] as any[]
})

// 确保taskStatusTracking的数组属性不为undefined
const ensureTaskStatusArrays = () => {
  if (!taskStatusTracking.value.added) taskStatusTracking.value.added = []
  if (!taskStatusTracking.value.updated) taskStatusTracking.value.updated = []
  if (!taskStatusTracking.value.deleted) taskStatusTracking.value.deleted = []
  if (!taskStatusTracking.value.originalTasks) taskStatusTracking.value.originalTasks = []
}

// 任务验证规则
const taskRules = ref({
  task_name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  assignee: [{ required: true, message: '请选择资源分配', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'blur' }],
  end_date: [{ required: true, message: '请选择计划结束日期', trigger: 'blur' }]
})

// 根据开始日期、计划结束日期、实际完成日期获取任务进度状态
const getProgressStatus = (task: any) => {
  const today = new Date()
  const startDate = new Date(task.start_date)
  const plannedEndDate = new Date(task.end_date)
  const actualEndDate = task.actual_end_date ? new Date(task.actual_end_date) : null
  
  // 未开始
  if (today < startDate) {
    return '未开始'
  }
  
  // 已完成
  if (actualEndDate) {
    // 已完成：实际完成日期 = 计划结束日期
    if (actualEndDate.toDateString() === plannedEndDate.toDateString()) {
      return '已完成'
    }
    // 提前完成：实际完成日期 < 计划结束日期
    else if (actualEndDate < plannedEndDate) {
      return '提前完成'
    }
    // 延期完成：实际完成日期 > 计划结束日期
    else {
      return '延期完成'
    }
  }
  
  // 进行中：当前日期 <= 计划结束日期
  if (today <= plannedEndDate) {
    return '进行中'
  }
  
  // 已延期：当前日期 > 计划结束日期
  return '已延期'
}

// 根据进度状态获取标签类型
const getProgressStatusType = (status: string) => {
  const statusMap: any = {
    '未开始': 'info',
    '进行中': 'primary',
    '已完成': 'success',
    '已延期': 'danger',
    '提前完成': 'success',
    '延期完成': 'warning'
  }
  return statusMap[status] || 'default'
}

// 计算两个日期之间的工作日数量（不包括周末）
const calculateWorkingDays = (startDateStr: string, endDateStr: string) => {
  // 使用字符串直接比较，避免Date构造函数的TypeScript错误
  const start = new Date(startDateStr)
  const end = new Date(endDateStr)
  let workingDays = 0
  
  const current = new Date(start)
  while (current <= end) {
    const day = current.getDay()
    // 排除周六和周日
    if (day !== 0 && day !== 6) {
      workingDays++
    }
    current.setDate(current.getDate() + 1)
  }
  
  return workingDays
}



// 日期格式化函数
const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}





// 生成任务ID
const generateTaskId = () => {
  // 如果有父任务，生成子任务ID
  if (taskFormData.value.parent_task_id) {
    // 查找所有同级任务（包括已存在的和正在编辑的）
    let siblingTasks = projectTasks.value.filter(task => 
      task.parent_task_id === taskFormData.value.parent_task_id
    )
    
    // 如果是编辑任务，排除当前任务本身
    if (taskFormData.value.task_id) {
      siblingTasks = siblingTasks.filter(task => task.task_id !== taskFormData.value.task_id)
    }
    
    // 生成新的子任务ID，使用下划线分隔
    return `${taskFormData.value.parent_task_id}_${siblingTasks.length + 1}`
  } else {
    // 查找所有顶级任务（包括已存在的和正在编辑的）
    let topLevelTasks = projectTasks.value.filter(task => 
      !task.parent_task_id || task.parent_task_id === ''
    )
    
    // 如果是编辑任务，排除当前任务本身
    if (taskFormData.value.task_id) {
      topLevelTasks = topLevelTasks.filter(task => task.task_id !== taskFormData.value.task_id)
    }
    
    // 生成新的顶级任务ID
    return `${projectId.value}_${topLevelTasks.length + 1}`
  }
}

// 打开任务对话框
const openTaskDialog = () => {
  taskDialogTitle.value = '新增任务'
  taskFormData.value = {
    task_id: '',
    project_id: projectId.value,
    task_name: '',
    parent_task_id: '',
    task_level: 1,
    assignee: [] as string[],
    assignee_id: '',
    start_date: '',
    end_date: '',
    actual_end_date: null,
    status: '未开始',
    progress: 0,
    planned_hours: 0,
    actual_hours: 0,
    evaluation: '',
    evaluation_desc: '',
    progress_rootcause: '',
    measures_results: '',
    remark: '',
    leaf_node: 1,
    hasChildren: false,
    created_by: 'current_user'
  }
  taskDialogVisible.value = true
}

// 编辑任务
const editTask = (row: any) => {
  taskDialogTitle.value = '编辑任务'
  // 转换assignee为数组格式
  const assigneeArray = row.assignee ? 
    (typeof row.assignee === 'string' ? row.assignee.split(',') : row.assignee) : []
  
  taskFormData.value = {
    ...row,
    assignee: assigneeArray as string[],
    hasChildren: row.hasChildren || false
  }
  taskDialogVisible.value = true
}

// 新增子任务
const addSubTask = (parentTask: any) => {
  taskDialogTitle.value = '新增子任务'
  
  // 初始化子任务表单数据
  taskFormData.value = {
    task_id: '',
    project_id: parentTask.project_id,
    task_name: '',
    parent_task_id: parentTask.task_id, // 设置父任务ID
    task_level: parentTask.task_level + 1,
    assignee: [] as string[],
    assignee_id: '',
    start_date: '',
    end_date: '',
    actual_end_date: null,
    status: '未开始',
    progress: 0,
    planned_hours: 0,
    actual_hours: 0,
    evaluation: '',
    evaluation_desc: '',
    progress_rootcause: '',
    measures_results: '',
    remark: '',
    leaf_node: 1,
    hasChildren: false,
    created_by: 'current_user'
  }
  
  console.log('新增子任务，父任务ID:', parentTask.task_id)
  console.log('子任务表单数据:', taskFormData.value)
  
  taskDialogVisible.value = true
}

// 保存任务
const saveTask = () => {
  if (taskForm.value) {
    taskForm.value.validate(async (valid: boolean) => {
      if (valid) {
        try {
          // 生成任务ID
          if (!taskFormData.value.task_id) {
            taskFormData.value.task_id = generateTaskId()
          }
          
          // 处理资源分配
          const assigneeStr = Array.isArray(taskFormData.value.assignee) ? 
            taskFormData.value.assignee.join(',') : 
            taskFormData.value.assignee
          
          // TODO: 处理assignee_id，这里需要根据人员名称获取对应的id
          // 暂时使用模拟数据
          taskFormData.value.assignee_id = '1,2,3'
          
          // 计算任务层级
          taskFormData.value.task_level = taskFormData.value.task_id.split('_').length
          
          // 自动判断是否为叶子节点
          // 如果没有子任务，则为叶子节点
          const hasChildren = projectTasks.value.some(task => 
            task.parent_task_id === taskFormData.value.task_id
          )
          taskFormData.value.leaf_node = hasChildren ? 0 : 1
          // 设置hasChildren属性，用于树形表格的展开/折叠图标
          taskFormData.value.hasChildren = hasChildren
          
          // TODO: 调用API保存任务
          console.log('保存任务', taskFormData.value)
          
          // 更新本地任务列表
          const index = projectTasks.value.findIndex(task => task.task_id === taskFormData.value.task_id)
          let updatedTasks = [...projectTasks.value]
          
          // 准备保存到任务列表的任务数据
          const taskToSave = {
            ...taskFormData.value,
            // 保存时将assignee数组转换为字符串，与后端期望的格式一致
            assignee: assigneeStr
          }
          
          if (index !== -1) {
            // 更新现有任务
            updatedTasks[index] = taskToSave
            
            // 任务状态跟踪 - 编辑场景
            ensureTaskStatusArrays()
            // 检查是否是原始任务列表中的任务
            const isOriginalTask = taskStatusTracking.value.originalTasks.some(
              (task: any) => task.task_id === taskFormData.value.task_id
            )
            
            if (isOriginalTask) {
              // 检查任务是否发生了变化
              const originalTask = taskStatusTracking.value.originalTasks.find(
                (task: any) => task.task_id === taskFormData.value.task_id
              )
              
              // 比较任务是否发生了变化
              const isChanged = JSON.stringify(originalTask) !== JSON.stringify(taskToSave)
              
              if (isChanged && !taskStatusTracking.value.updated.includes(taskFormData.value.task_id)) {
                // 添加到已更新任务列表
                taskStatusTracking.value.updated.push(taskFormData.value.task_id)
              }
            } else {
              // 如果不是原始任务，说明是在编辑过程中新增的
              if (!taskStatusTracking.value.added.includes(taskFormData.value.task_id)) {
                // 添加到已新增任务列表
                taskStatusTracking.value.added.push(taskFormData.value.task_id)
              }
            }
            
            ElMessage.success('任务已更新')
          } else {
            // 添加新任务
            updatedTasks.push(taskToSave)
            
            // 任务状态跟踪 - 编辑场景
            // 添加到已新增任务列表
            if (!taskStatusTracking.value.added.includes(taskFormData.value.task_id)) {
              taskStatusTracking.value.added.push(taskFormData.value.task_id)
            }
            
            ElMessage.success('任务已创建')
            
            // 如果是子任务，更新父任务的hasChildren属性为true
            if (taskFormData.value.parent_task_id) {
              const parentIndex = updatedTasks.findIndex(task => task.task_id === taskFormData.value.parent_task_id)
              if (parentIndex !== -1) {
                updatedTasks[parentIndex] = {
                  ...updatedTasks[parentIndex],
                  hasChildren: true,
                  leaf_node: 0 // 父任务不再是叶子节点
                }
              }
            }
          }
          
          // 使用新数组替换原数组，确保Vue的响应式系统检测到变化
          projectTasks.value = updatedTasks
          console.log('✅ 任务列表已更新:', projectTasks.value)
          
          // 更新treeDataKey，触发表格重新渲染
          treeDataKey.value++
          console.log('🔄 更新treeDataKey:', treeDataKey.value)
          
          taskDialogVisible.value = false
} catch (error) {
          console.error('保存任务失败:', error)
          ElMessage.error('保存任务失败，请稍后重试')
        }
      }
    })
  }
}

// 删除任务
const deleteTask = (row: any) => {
  // 检查该任务是否有子任务
  const hasSubTasks = projectTasks.value.some(task => task.parent_task_id === row.task_id)
  
  if (hasSubTasks) {
    ElMessage.warning('该任务下存在子任务，无法直接删除，请先删除子任务或转移子任务')
    return
  }
  
  ElMessageBox.confirm('确定要删除这条任务吗？', '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      // TODO: 调用API删除任务
      console.log('删除任务', row.task_id)
      
      // 从本地任务列表中删除
      const taskToDelete = row
      const updatedTasks = projectTasks.value.filter(task => task.task_id !== row.task_id)
      
      // 检查删除的任务是否有父任务，如果有，更新父任务的hasChildren属性
      if (taskToDelete.parent_task_id) {
        const parentTask = updatedTasks.find(task => task.task_id === taskToDelete.parent_task_id)
        if (parentTask) {
          // 检查父任务是否还有其他子任务
          const hasRemainingChildren = updatedTasks.some(task => task.parent_task_id === parentTask.task_id)
          parentTask.hasChildren = hasRemainingChildren
          parentTask.leaf_node = hasRemainingChildren ? 0 : 1
        }
      }
      
      // 任务状态跟踪 - 编辑场景
      ensureTaskStatusArrays()
      // 检查是否是原始任务列表中的任务
      const isOriginalTask = taskStatusTracking.value.originalTasks.some(
        (task: any) => task.task_id === row.task_id
      )
      
      if (isOriginalTask) {
        // 添加到已删除任务列表
        if (!taskStatusTracking.value.deleted.includes(row.task_id)) {
          taskStatusTracking.value.deleted.push(row.task_id)
        }
      } else {
        // 如果不是原始任务，说明是在编辑过程中新增的，需要从已新增列表中移除
        const addedIndex = taskStatusTracking.value.added.indexOf(row.task_id)
        if (addedIndex !== -1) {
          taskStatusTracking.value.added.splice(addedIndex, 1)
        }
        
        // 也需要从已更新列表中移除，以防万一
        const updatedIndex = taskStatusTracking.value.updated.indexOf(row.task_id)
        if (updatedIndex !== -1) {
          taskStatusTracking.value.updated.splice(updatedIndex, 1)
        }
      }
      
      // 更新任务列表
      projectTasks.value = updatedTasks
      ElMessage.success('任务已删除')
      
      // 更新treeDataKey，触发表格重新渲染
      treeDataKey.value++
      console.log('🔄 删除任务后更新treeDataKey:', treeDataKey.value)

    } catch (error) {
      console.error('删除任务失败:', error)
      ElMessage.error('删除任务失败')
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 导入任务 - 新建场景
const importTasks = () => {
  // 导入前提示用户，确认是否导入，会清空现有数据
  ElMessageBox.confirm('导入任务会清空现有数据，确定要导入吗？', '导入确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    // 创建文件输入元素
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.xlsx, .xls'
    
    // 监听文件选择事件
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (!file) return
      
      try {
        // 导入xlsx库
        const XLSX = await import('xlsx')
        
        // 读取文件
        const reader = new FileReader()
        reader.onload = (event) => {
          const data = new Uint8Array(event.target?.result as ArrayBuffer)
          const workbook = XLSX.read(data, { type: 'array' })
          
          // 获取第一个工作表
          const worksheet = workbook.Sheets[workbook.SheetNames[0]]
          
          // 转换为JSON数据
          const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 })
          
          // 解析Excel数据 - 新建场景
          parseExcelData(jsonData)
        }
        reader.readAsArrayBuffer(file)
      } catch (error) {
        console.error('[新建场景] 导入任务失败:', error)
        ElMessage.error('导入任务失败，请稍后重试')
      }
    }
    
    // 触发文件选择
    input.click()
  }).catch(() => {
    ElMessage.info('已取消导入')
  })
}

// 导入任务 - 编辑场景
const importTasksInEditMode = () => {
  // 导入前提示用户，确认是否导入，会清空现有数据
  ElMessageBox.confirm('导入任务会清空现有数据，确定要导入吗？', '导入确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    // 创建文件输入元素
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.xlsx, .xls'
    
    // 监听文件选择事件
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (!file) return
      
      try {
        // 导入xlsx库
        const XLSX = await import('xlsx')
        
        // 读取文件
        const reader = new FileReader()
        reader.onload = (event) => {
          const data = new Uint8Array(event.target?.result as ArrayBuffer)
          const workbook = XLSX.read(data, { type: 'array' })
          
          // 获取第一个工作表
          const worksheet = workbook.Sheets[workbook.SheetNames[0]]
          
          // 转换为JSON数据
          const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 })
          
          // 解析Excel数据 - 编辑场景
          parseExcelDataInEditMode(jsonData)
        }
        reader.readAsArrayBuffer(file)
      } catch (error) {
        console.error('[编辑场景] 导入任务失败:', error)
        ElMessage.error('导入任务失败，请稍后重试')
      }
    }
    
    // 触发文件选择
    input.click()
  }).catch(() => {
    ElMessage.info('已取消导入')
  })
}

// 解析Excel数据 - 新建场景
const parseExcelData = (jsonData: any[]) => {
  if (jsonData.length < 2) {
    ElMessage.warning('Excel文件为空或格式不正确')
    return
  }
  
  console.log('[新建场景] DEBUG: Excel数据行数:', jsonData.length)
  console.log('[新建场景] DEBUG: 表头行:', jsonData[0])
  
  // 列头映射关系 - 支持用户Excel文件中的具体列名
  const headerMap: Record<string, string[]> = {
    'task_name': ['任务名称', '项目名称/结果/过程/要素', '项目名称', '结果/过程/要素'],
    'assignee': ['负责人', '执行人', '责任人', '经办人'],
    'start_date': ['开始日期', '计划开始日期', '开始时间'],
    'end_date': ['计划完成时间', '结束日期', '计划结束日期', '结束时间'],
    'actual_end_date': ['实际完成时间', '实际结束日期'],
    'evaluation': ['考评', '评分', '考核'],
    'evaluation_desc': ['考评说明', '评分说明', '考核说明'],
    'progress_rootcause': ['进展/根因', '进展', '根因'],
    'measures_results': ['措施/结果', '措施', '结果']
  }
  
  // 获取列头索引
  const headerRow = jsonData[0] as (string | number)[]
  const headerIndices: Record<string, number> = {}
  
  console.log('[新建场景] DEBUG: 处理表头行:', headerRow)
  
  // 转换表头为字符串数组，确保所有值都是字符串
  const stringHeaderRow = headerRow.map((header, index) => {
    const strHeader = String(header).trim()
    console.log(`[新建场景] DEBUG: 表头列 ${index}: '${strHeader}' (原始类型: ${typeof header})`)
    return strHeader
  })
  
  // 遍历系统需要的字段，查找匹配的列名
  Object.keys(headerMap).forEach(systemField => {
    console.log(`[新建场景] DEBUG: 查找字段 ${systemField}，可能的列名:`, headerMap[systemField])
    const possibleHeaders = headerMap[systemField]
    
    // 遍历所有表头列，查找匹配的列
    for (let i = 0; i < stringHeaderRow.length; i++) {
      const header = stringHeaderRow[i]
      if (header) {
        // 精确匹配优先
        if (possibleHeaders.includes(header)) {
          headerIndices[systemField] = i
          console.log(`[新建场景] DEBUG: 精确匹配列 ${systemField} 到索引 ${i} (列名: '${header}')`)
          break
        }
        // 包含匹配
        else if (possibleHeaders.some(possibleHeader => header.includes(possibleHeader))) {
          headerIndices[systemField] = i
          console.log(`[新建场景] DEBUG: 包含匹配列 ${systemField} 到索引 ${i} (列名: '${header}'，匹配项: ${possibleHeaders.find(p => header.includes(p))})`)
          break
        }
        // 忽略大小写匹配
        else if (possibleHeaders.some(possibleHeader => 
          header.toLowerCase().includes(possibleHeader.toLowerCase())
        )) {
          headerIndices[systemField] = i
          console.log(`[新建场景] DEBUG: 忽略大小写匹配列 ${systemField} 到索引 ${i} (列名: '${header}'，匹配项: ${possibleHeaders.find(p => header.toLowerCase().includes(p.toLowerCase()))})`)
          break
        }
      }
    }
    
    if (headerIndices[systemField] === undefined) {
      console.log(`[新建场景] DEBUG: 未找到字段 ${systemField} 的匹配列`)
    }
  })
  
  // 检查是否至少有必要的列
  console.log('[新建场景] DEBUG: 最终列匹配结果:', headerIndices)
  
  // 尝试查找最接近"任务名称"的列
  let hasTaskName = false
  if (headerIndices['task_name'] !== undefined) {
    hasTaskName = true
  } else {
    // 检查是否有包含"任务"或"项目"的列
    for (let i = 0; i < stringHeaderRow.length; i++) {
      const header = stringHeaderRow[i]
      if (header.toLowerCase().includes('任务') || header.toLowerCase().includes('项目')) {
        console.log(`[新建场景] DEBUG: 找到可能的任务名称列: '${header}' 在索引 ${i}`)
        // 直接使用这个列作为任务名称列
        headerIndices['task_name'] = i
        hasTaskName = true
        break
      }
    }
  }
  
  if (!hasTaskName) {
    ElMessage.warning(`Excel文件缺少必要的列：任务名称\n检测到的表头列：${stringHeaderRow.join(', ')}`)
    return
  }
  
  // 开始日期和结束日期是必要的
  let hasStartDate = false
  if (headerIndices['start_date'] !== undefined) {
    hasStartDate = true
  } else {
    // 检查是否有包含"开始"或"日期"的列
    for (let i = 0; i < stringHeaderRow.length; i++) {
      const header = stringHeaderRow[i]
      if (header.toLowerCase().includes('开始') || header.toLowerCase().includes('日期')) {
        console.log(`[新建场景] DEBUG: 找到可能的开始日期列: '${header}' 在索引 ${i}`)
        // 直接使用这个列作为开始日期列
        headerIndices['start_date'] = i
        hasStartDate = true
        break
      }
    }
  }
  
  if (!hasStartDate) {
    ElMessage.warning(`Excel文件缺少必要的列：开始日期\n检测到的表头列：${stringHeaderRow.join(', ')}`)
    return
  }
  
  let hasEndDate = false
  if (headerIndices['end_date'] !== undefined) {
    hasEndDate = true
  } else {
    // 检查是否有包含"结束"或"完成"的列
    for (let i = 0; i < stringHeaderRow.length; i++) {
      const header = stringHeaderRow[i]
      if (header.toLowerCase().includes('结束') || header.toLowerCase().includes('完成')) {
        console.log(`[新建场景] DEBUG: 找到可能的结束日期列: '${header}' 在索引 ${i}`)
        // 直接使用这个列作为结束日期列
        headerIndices['end_date'] = i
        hasEndDate = true
        break
      }
    }
  }
  
  if (!hasEndDate) {
    ElMessage.warning(`Excel文件缺少必要的列：计划完成时间\n检测到的表头列：${stringHeaderRow.join(', ')}`)
    return
  }
  
  console.log('[新建场景] DEBUG: 列头索引映射:', headerIndices)
  
  // 导入的任务列表
  const importedTasks: any[] = []
  
  // 解析数据行
  for (let i = 1; i < jsonData.length; i++) {
    const row = jsonData[i] as any[]
    
    console.log('[新建场景] DEBUG: 处理第', i, '行数据:', row)
    
    // 获取任务名称
    const taskName = row[headerIndices['task_name']]?.toString().trim()
    if (!taskName) {
      console.log('[新建场景] DEBUG: 跳过空任务名称行:', row)
      continue
    }
    
    // 将Excel日期转换为正确的日期字符串
    const excelDateToDateStr = (excelDate: any) => {
      if (!excelDate) return ''
      
      try {
        // 处理不同类型的日期输入
        if (typeof excelDate === 'string') {
          // 如果是字符串，尝试直接转换
          const date = new Date(excelDate)
          if (!isNaN(date.getTime())) {
            return date.toISOString().split('T')[0]
          }
        } else if (typeof excelDate === 'number') {
          // 如果是数值，使用Excel日期转换
          // 处理Excel的日期格式，从1900年1月1日开始计算
          const date = new Date((excelDate - 25569) * 86400000) // 25569是1970年1月1日到1900年1月1日的天数
          if (!isNaN(date.getTime())) {
            return date.toISOString().split('T')[0]
          }
        }
      } catch (error) {
        console.error('[新建场景] DEBUG: 日期转换错误:', error, '原始值:', excelDate)
      }
      
      // 如果转换失败，尝试其他格式
      return excelDate?.toString().trim() || ''
    }
    
    // 构建基础任务数据
    const task = {
      task_id: '', // 后续生成
      project_id: projectId.value,
      task_name: taskName,
      parent_task_id: '', // 后续匹配
      task_level: 1, // 默认一级任务
      assignee: row[headerIndices['assignee']]?.toString().trim() || '',
      assignee_id: '', // 后续处理
      start_date: excelDateToDateStr(row[headerIndices['start_date']]),
      end_date: excelDateToDateStr(row[headerIndices['end_date']]),
      actual_end_date: headerIndices['actual_end_date'] ? excelDateToDateStr(row[headerIndices['actual_end_date']]) : null,
      status: '未开始', // 后续根据日期自动判断
      progress: 0, // 后续根据日期自动判断
      planned_hours: 0,
      actual_hours: 0,
      evaluation: row[headerIndices['evaluation']]?.toString().trim() || '',
      evaluation_desc: row[headerIndices['evaluation_desc']]?.toString().trim() || '',
      progress_rootcause: row[headerIndices['progress_rootcause']]?.toString().trim() || '',
      measures_results: row[headerIndices['measures_results']]?.toString().trim() || '',
      remark: '',
      leaf_node: 0, // 初始设为叶子节点，后续更新
      hasChildren: false, // 初始设为false，后续更新
      created_by: 'current_user'
    }
    
    // 解析任务层级和父子关系 - 简化逻辑
    const trimmedTaskName = taskName.trim()
    if (trimmedTaskName.startsWith('结果')) {
      // 二级任务
      task.task_level = 2
    } else if (trimmedTaskName.startsWith('过程')) {
      // 三级任务
      task.task_level = 3
    } else {
      // 一级任务
      task.task_level = 1
    }
    
    importedTasks.push(task)
    console.log('[新建场景] DEBUG: 添加任务:', task.task_name, '层级:', task.task_level)
  }
  
  console.log('[新建场景] DEBUG: 导入任务数量:', importedTasks.length)
  
  if (importedTasks.length === 0) {
    ElMessage.warning('未解析到有效任务数据，请检查Excel文件格式')
    return
  }
  
  // 生成任务ID并匹配父任务 - 新建场景
  generateTaskIdsAndMatchParents(importedTasks)
}

// 解析Excel数据 - 编辑场景
const parseExcelDataInEditMode = (jsonData: any[]) => {
  if (jsonData.length < 2) {
    ElMessage.warning('Excel文件为空或格式不正确')
    return
  }
  
  console.log('[编辑场景] DEBUG: Excel数据行数:', jsonData.length)
  console.log('[编辑场景] DEBUG: 表头行:', jsonData[0])
  
  // 列头映射关系 - 支持用户Excel文件中的具体列名
  const headerMap: Record<string, string[]> = {
    'task_name': ['任务名称', '项目名称/结果/过程/要素', '项目名称', '结果/过程/要素'],
    'assignee': ['负责人', '执行人', '责任人', '经办人'],
    'start_date': ['开始日期', '计划开始日期', '开始时间'],
    'end_date': ['计划完成时间', '结束日期', '计划结束日期', '结束时间'],
    'actual_end_date': ['实际完成时间', '实际结束日期'],
    'evaluation': ['考评', '评分', '考核'],
    'evaluation_desc': ['考评说明', '评分说明', '考核说明'],
    'progress_rootcause': ['进展/根因', '进展', '根因'],
    'measures_results': ['措施/结果', '措施', '结果']
  }
  
  // 获取列头索引
  const headerRow = jsonData[0] as (string | number)[]
  const headerIndices: Record<string, number> = {}
  
  console.log('[编辑场景] DEBUG: 处理表头行:', headerRow)
  
  // 转换表头为字符串数组，确保所有值都是字符串
  const stringHeaderRow = headerRow.map((header, index) => {
    const strHeader = String(header).trim()
    console.log(`[编辑场景] DEBUG: 表头列 ${index}: '${strHeader}' (原始类型: ${typeof header})`)
    return strHeader
  })
  
  // 遍历系统需要的字段，查找匹配的列名
  Object.keys(headerMap).forEach(systemField => {
    console.log(`[编辑场景] DEBUG: 查找字段 ${systemField}，可能的列名:`, headerMap[systemField])
    const possibleHeaders = headerMap[systemField]
    
    // 遍历所有表头列，查找匹配的列
    for (let i = 0; i < stringHeaderRow.length; i++) {
      const header = stringHeaderRow[i]
      if (header) {
        // 精确匹配优先
        if (possibleHeaders.includes(header)) {
          headerIndices[systemField] = i
          console.log(`[编辑场景] DEBUG: 精确匹配列 ${systemField} 到索引 ${i} (列名: '${header}')`)
          break
        }
        // 包含匹配
        else if (possibleHeaders.some(possibleHeader => header.includes(possibleHeader))) {
          headerIndices[systemField] = i
          console.log(`[编辑场景] DEBUG: 包含匹配列 ${systemField} 到索引 ${i} (列名: '${header}'，匹配项: ${possibleHeaders.find(p => header.includes(p))})`)
          break
        }
        // 忽略大小写匹配
        else if (possibleHeaders.some(possibleHeader => 
          header.toLowerCase().includes(possibleHeader.toLowerCase())
        )) {
          headerIndices[systemField] = i
          console.log(`[编辑场景] DEBUG: 忽略大小写匹配列 ${systemField} 到索引 ${i} (列名: '${header}'，匹配项: ${possibleHeaders.find(p => header.toLowerCase().includes(p.toLowerCase()))})`)
          break
        }
      }
    }
    
    if (headerIndices[systemField] === undefined) {
      console.log(`[编辑场景] DEBUG: 未找到字段 ${systemField} 的匹配列`)
    }
  })
  
  // 检查是否至少有必要的列
  console.log('[编辑场景] DEBUG: 最终列匹配结果:', headerIndices)
  
  // 尝试查找最接近"任务名称"的列
  let hasTaskName = false
  if (headerIndices['task_name'] !== undefined) {
    hasTaskName = true
  } else {
    // 检查是否有包含"任务"或"项目"的列
    for (let i = 0; i < stringHeaderRow.length; i++) {
      const header = stringHeaderRow[i]
      if (header.toLowerCase().includes('任务') || header.toLowerCase().includes('项目')) {
        console.log(`[编辑场景] DEBUG: 找到可能的任务名称列: '${header}' 在索引 ${i}`)
        // 直接使用这个列作为任务名称列
        headerIndices['task_name'] = i
        hasTaskName = true
        break
      }
    }
  }
  
  if (!hasTaskName) {
    ElMessage.warning(`Excel文件缺少必要的列：任务名称\n检测到的表头列：${stringHeaderRow.join(', ')}`)
    return
  }
  
  // 开始日期和结束日期是必要的
  let hasStartDate = false
  if (headerIndices['start_date'] !== undefined) {
    hasStartDate = true
  } else {
    // 检查是否有包含"开始"或"日期"的列
    for (let i = 0; i < stringHeaderRow.length; i++) {
      const header = stringHeaderRow[i]
      if (header.toLowerCase().includes('开始') || header.toLowerCase().includes('日期')) {
        console.log(`[编辑场景] DEBUG: 找到可能的开始日期列: '${header}' 在索引 ${i}`)
        // 直接使用这个列作为开始日期列
        headerIndices['start_date'] = i
        hasStartDate = true
        break
      }
    }
  }
  
  if (!hasStartDate) {
    ElMessage.warning(`Excel文件缺少必要的列：开始日期\n检测到的表头列：${stringHeaderRow.join(', ')}`)
    return
  }
  
  let hasEndDate = false
  if (headerIndices['end_date'] !== undefined) {
    hasEndDate = true
  } else {
    // 检查是否有包含"结束"或"完成"的列
    for (let i = 0; i < stringHeaderRow.length; i++) {
      const header = stringHeaderRow[i]
      if (header.toLowerCase().includes('结束') || header.toLowerCase().includes('完成')) {
        console.log(`[编辑场景] DEBUG: 找到可能的结束日期列: '${header}' 在索引 ${i}`)
        // 直接使用这个列作为结束日期列
        headerIndices['end_date'] = i
        hasEndDate = true
        break
      }
    }
  }
  
  if (!hasEndDate) {
    ElMessage.warning(`Excel文件缺少必要的列：计划完成时间\n检测到的表头列：${stringHeaderRow.join(', ')}`)
    return
  }
  
  console.log('[编辑场景] DEBUG: 列头索引映射:', headerIndices)
  
  // 导入的任务列表
  const importedTasks: any[] = []
  
  // 解析数据行
  for (let i = 1; i < jsonData.length; i++) {
    const row = jsonData[i] as any[]
    
    console.log('[编辑场景] DEBUG: 处理第', i, '行数据:', row)
    
    // 获取任务名称
    const taskName = row[headerIndices['task_name']]?.toString().trim()
    if (!taskName) {
      console.log('[编辑场景] DEBUG: 跳过空任务名称行:', row)
      continue
    }
    
    // 将Excel日期转换为正确的日期字符串
    const excelDateToDateStr = (excelDate: any) => {
      if (!excelDate) return ''
      
      try {
        // 处理不同类型的日期输入
        if (typeof excelDate === 'string') {
          // 如果是字符串，尝试直接转换
          const date = new Date(excelDate)
          if (!isNaN(date.getTime())) {
            return date.toISOString().split('T')[0]
          }
        } else if (typeof excelDate === 'number') {
          // 如果是数值，使用Excel日期转换
          // 处理Excel的日期格式，从1900年1月1日开始计算
          const date = new Date((excelDate - 25569) * 86400000) // 25569是1970年1月1日到1900年1月1日的天数
          if (!isNaN(date.getTime())) {
            return date.toISOString().split('T')[0]
          }
        }
      } catch (error) {
        console.error('[编辑场景] DEBUG: 日期转换错误:', error, '原始值:', excelDate)
      }
      
      // 如果转换失败，尝试其他格式
      return excelDate?.toString().trim() || ''
    }
    
    // 构建基础任务数据
    const task = {
      task_id: '', // 后续生成
      project_id: projectId.value,
      task_name: taskName,
      parent_task_id: '', // 后续匹配
      task_level: 1, // 默认一级任务
      assignee: row[headerIndices['assignee']]?.toString().trim() || '',
      assignee_id: '', // 后续处理
      start_date: excelDateToDateStr(row[headerIndices['start_date']]),
      end_date: excelDateToDateStr(row[headerIndices['end_date']]),
      actual_end_date: headerIndices['actual_end_date'] ? excelDateToDateStr(row[headerIndices['actual_end_date']]) : null,
      status: '未开始', // 后续根据日期自动判断
      progress: 0, // 后续根据日期自动判断
      planned_hours: 0,
      actual_hours: 0,
      evaluation: row[headerIndices['evaluation']]?.toString().trim() || '',
      evaluation_desc: row[headerIndices['evaluation_desc']]?.toString().trim() || '',
      progress_rootcause: row[headerIndices['progress_rootcause']]?.toString().trim() || '',
      measures_results: row[headerIndices['measures_results']]?.toString().trim() || '',
      remark: '',
      leaf_node: 0, // 初始设为叶子节点，后续更新
      hasChildren: false, // 初始设为false，后续更新
      created_by: 'current_user'
    }
    
    // 解析任务层级和父子关系 - 简化逻辑
    const trimmedTaskName = taskName.trim()
    if (trimmedTaskName.startsWith('结果')) {
      // 二级任务
      task.task_level = 2
    } else if (trimmedTaskName.startsWith('过程')) {
      // 三级任务
      task.task_level = 3
    } else {
      // 一级任务
      task.task_level = 1
    }
    
    importedTasks.push(task)
    console.log('[编辑场景] DEBUG: 添加任务:', task.task_name, '层级:', task.task_level)
  }
  
  console.log('[编辑场景] DEBUG: 导入任务数量:', importedTasks.length)
  
  if (importedTasks.length === 0) {
    ElMessage.warning('未解析到有效任务数据，请检查Excel文件格式')
    return
  }
  
  // 生成任务ID并匹配父任务 - 编辑场景
  generateTaskIdsAndMatchParentsInEditMode(importedTasks)
}

// 生成任务ID并匹配父任务 - 新建场景
const generateTaskIdsAndMatchParents = (tasks: any[]) => {
  // 一级任务列表
  const level1Tasks = tasks.filter(task => task.task_level === 1)
  
  // 二级任务列表
  const level2Tasks = tasks.filter(task => task.task_level === 2)
  
  // 三级任务列表
  const level3Tasks = tasks.filter(task => task.task_level === 3)
  
  // 生成一级任务ID
  level1Tasks.forEach((task, index) => {
    task.task_id = `${projectId.value}_${index + 1}`
  })
  
  // 生成二级任务ID并匹配父任务
  level2Tasks.forEach((task, index) => {
    // 匹配父任务（一级任务）
    const parentTask = level1Tasks[0] // 假设只有一个一级任务
    if (parentTask) {
      task.parent_task_id = parentTask.task_id
      task.task_id = `${parentTask.task_id}_${index + 1}`
      parentTask.hasChildren = true
      parentTask.leaf_node = 1 // 非叶子节点
    }
  })
  
  // 生成三级任务ID并匹配父任务
  // 遍历所有任务，按顺序处理，确保三级任务匹配到正确的二级任务
  let currentLevel2Task: any = null
  // 记录每个二级任务下的三级任务数量
  const level3TaskCounts: Record<string, number> = {}
  
  tasks.forEach(task => {
    if (task.task_level === 2) {
      // 遇到二级任务，更新当前二级任务
      currentLevel2Task = task
      // 初始化当前二级任务下的三级任务数量
      level3TaskCounts[task.task_id] = 0
    } else if (task.task_level === 3 && currentLevel2Task) {
      // 遇到三级任务，使用当前二级任务作为父任务
      task.parent_task_id = currentLevel2Task.task_id
      // 计算当前父任务下的三级任务数量，从1开始
      const childCount = ++level3TaskCounts[currentLevel2Task.task_id]
      task.task_id = `${currentLevel2Task.task_id}_${childCount}`
      currentLevel2Task.hasChildren = true
      currentLevel2Task.leaf_node = 1 // 非叶子节点
    }
  })
  
  // 生成三级任务ID（如果之前没有生成）
  level3Tasks.forEach((task, index) => {
    if (!task.task_id) {
      // 这种情况不应该发生
      task.task_id = `${projectId.value}_0_${index + 1}`
    }
  })
  
  // 更新所有任务的叶子节点标识
  tasks.forEach(task => {
    // 叶子节点：没有子任务的任务
    const hasChildren = tasks.some(t => t.parent_task_id === task.task_id)
    task.hasChildren = hasChildren
    task.leaf_node = hasChildren ? 1 : 0
  })
  
  // 清空现有任务数据
  projectTasks.value = tasks
  
  // 更新treeDataKey，触发表格重新渲染
  treeDataKey.value++
  
  ElMessage.success(`成功导入 ${tasks.length} 个任务`)
}

// 生成任务ID并匹配父任务 - 编辑场景
const generateTaskIdsAndMatchParentsInEditMode = (tasks: any[]) => {
  // 一级任务列表
  const level1Tasks = tasks.filter(task => task.task_level === 1)
  
  // 二级任务列表
  const level2Tasks = tasks.filter(task => task.task_level === 2)
  
  // 三级任务列表
  const level3Tasks = tasks.filter(task => task.task_level === 3)
  
  // 生成一级任务ID - 编辑场景
  level1Tasks.forEach((task, index) => {
    task.task_id = `${projectId.value}_${index + 1}`
  })
  
  // 生成二级任务ID并匹配父任务 - 编辑场景
  level2Tasks.forEach((task, index) => {
    // 匹配父任务（一级任务）
    const parentTask = level1Tasks[0] // 假设只有一个一级任务
    if (parentTask) {
      task.parent_task_id = parentTask.task_id
      task.task_id = `${parentTask.task_id}_${index + 1}`
      parentTask.hasChildren = true
      parentTask.leaf_node = 1 // 非叶子节点
    }
  })
  
  // 生成三级任务ID并匹配父任务 - 编辑场景
  // 遍历所有任务，按顺序处理，确保三级任务匹配到正确的二级任务
  let currentLevel2Task: any = null
  // 记录每个二级任务下的三级任务数量
  const level3TaskCounts: Record<string, number> = {}
  
  tasks.forEach(task => {
    if (task.task_level === 2) {
      // 遇到二级任务，更新当前二级任务
      currentLevel2Task = task
      // 初始化当前二级任务下的三级任务数量
      level3TaskCounts[task.task_id] = 0
    } else if (task.task_level === 3 && currentLevel2Task) {
      // 遇到三级任务，使用当前二级任务作为父任务
      task.parent_task_id = currentLevel2Task.task_id
      // 计算当前父任务下的三级任务数量，从1开始
      const childCount = ++level3TaskCounts[currentLevel2Task.task_id]
      task.task_id = `${currentLevel2Task.task_id}_${childCount}`
      currentLevel2Task.hasChildren = true
      currentLevel2Task.leaf_node = 1 // 非叶子节点
    }
  })
  
  // 生成三级任务ID（如果之前没有生成）
  level3Tasks.forEach((task, index) => {
    if (!task.task_id) {
      // 这种情况不应该发生
      task.task_id = `${projectId.value}_0_${index + 1}`
    }
  })
  
  // 更新所有任务的叶子节点标识
  tasks.forEach(task => {
    // 叶子节点：没有子任务的任务
    const hasChildren = tasks.some(t => t.parent_task_id === task.task_id)
    task.hasChildren = hasChildren
    task.leaf_node = hasChildren ? 1 : 0
  })
  
  // 清空现有任务数据 - 编辑场景
  projectTasks.value = tasks
  
  // 更新任务状态跟踪 - 编辑场景
  // 重置任务状态跟踪，因为导入会替换所有现有任务
  taskStatusTracking.value = {
    added: tasks.map(task => task.task_id), // 所有导入的任务都是新增的
    updated: [],
    deleted: [],
    originalTasks: [...tasks] // 原始任务列表是导入的任务列表
  }
  
  // 更新treeDataKey，触发表格重新渲染 - 编辑场景
  treeDataKey.value++
  
  ElMessage.success(`成功导入 ${tasks.length} 个任务`)
}

// 计算计划工时
const calculatePlannedHours = () => {
  if (!taskFormData.value.start_date || !taskFormData.value.end_date) {
    return
  }
  
  const workingDays = calculateWorkingDays(
    taskFormData.value.start_date,
    taskFormData.value.end_date
  )
  // 工作日按8小时计算
  taskFormData.value.planned_hours = workingDays * 8
}



// 下一步按钮处理
const handleNext = () => {
  // 处理任务数据，移除前端专用的hasChildren属性，只保留后端需要的字段
  const tasksToSave = projectTasks.value.map(task => {
    // 移除后端模型没有的字段
    const { hasChildren, created_by, ...taskWithoutHasChildren } = task;
    return taskWithoutHasChildren;
  });
  
  // 保存当前任务设置到sessionStorage
  sessionStorage.setItem(`project_tasks_${projectId.value}`, JSON.stringify(tasksToSave))
  console.log('DEBUG: [Step3] 跳转到Step4，mode=', mode.value)
  router.push({
    name: 'ProjectCreateStep4',
    query: { 
      mode: mode.value, 
      projectId: projectId.value 
    }
  })
}

// 打开甘特图对话框
const openGanttDialog = () => {
  ganttDialogVisible.value = true
}

// 跳转到上一步
const handlePrevious = () => {
  console.log('DEBUG: [任务管理] 点击上一步按钮')
  
  // 处理任务数据，移除后端模型没有的字段
  const tasksToSave = projectTasks.value.map(task => {
    // 移除后端模型没有的字段
    const { hasChildren, created_by, ...taskWithoutHasChildren } = task;
    return taskWithoutHasChildren;
  });
  
  // 保存当前任务设置到sessionStorage
  sessionStorage.setItem(`project_tasks_${projectId.value}`, JSON.stringify(tasksToSave))
  
  // 直接跳转到上一步
  console.log('DEBUG: [Step3] 跳转到Step2，mode=', mode.value)
  router.push({
    name: 'ProjectCreateStep2',
    query: { 
      mode: mode.value, 
      projectId: projectId.value 
    }
  })
}

// 获取人员列表
const fetchPersonnel = async () => {
  try {
    const response = await getPersonnel({ limit: 1000 })
    // 检查响应格式，根据实际API返回调整
    personnelList.value = Array.isArray(response) ? response : (response.data || [])
  } catch (error) {
    console.error('获取人员列表失败:', error)
    ElMessage.error('获取人员列表失败')
  }
}

// 监听projectTasks的变化，确保表格重新渲染
watch(
  () => projectTasks.value,
  () => {
    console.log('👀 projectTasks变化，更新treeDataKey')
    treeDataKey.value++
    
    // 保存任务列表到sessionStorage，移除后端不需要的字段
    const tasksToSave = projectTasks.value.map(task => {
      // 移除后端模型没有的字段
      const { hasChildren, created_by, ...taskWithoutHasChildren } = task;
      return taskWithoutHasChildren;
    });
    sessionStorage.setItem(`project_tasks_${projectId.value}`, JSON.stringify(tasksToSave))
  },
  { deep: true }
)

// 监听任务状态跟踪的变化，保存到sessionStorage
watch(
  () => taskStatusTracking.value,
  () => {
    console.log('👀 taskStatusTracking变化，保存到sessionStorage')
    sessionStorage.setItem(`task_status_${projectId.value}`, JSON.stringify(taskStatusTracking.value))
  },
  { deep: true }
)

// 获取项目详情
const fetchProjectDetailData = async () => {
  if (!projectId.value) return
  
  try {
    const project = await getProjectDetail(projectId.value)
    projectName.value = project.name
  } catch (error) {
    console.error('获取项目详情失败:', error)
    // 失败时不显示错误，保持默认文本
  }
}

// 初始加载数据
onMounted(async () => {
  // 先加载人员列表和项目详情，确保对话框打开时能使用
  await Promise.all([
    fetchPersonnel(),
    fetchProjectDetailData()
  ])
  
  // 编辑模式下，优先检查sessionStorage是否有用户修改后的数据
  if (isEditMode.value) {
    // 检查sessionStorage中是否有用户修改后的数据
    const savedTasks = sessionStorage.getItem(`project_tasks_${projectId.value}`)
    
    if (savedTasks) {
      console.log('DEBUG: [编辑场景] 从sessionStorage获取用户修改后的任务数据')
      projectTasks.value = JSON.parse(savedTasks)
      // 保存原始任务列表，用于编辑场景的任务状态跟踪
      taskStatusTracking.value.originalTasks = JSON.parse(JSON.stringify(projectTasks.value))
    } else {
      // 如果sessionStorage中没有数据，从API获取
      console.log('DEBUG: [编辑场景] 从API获取任务数据')
      try {
        // 调用API获取项目任务数据
        const response = await getProjectTasks(projectId.value)
        console.log('DEBUG: [编辑场景] 获取到的任务数据:', response)
        
        if (response && response.length > 0) {
          projectTasks.value = response
          // 保存原始任务列表，用于编辑场景的任务状态跟踪
          taskStatusTracking.value.originalTasks = JSON.parse(JSON.stringify(projectTasks.value))
          // 保存到sessionStorage
          sessionStorage.setItem(`project_tasks_${projectId.value}`, JSON.stringify(projectTasks.value))
        }
      } catch (error) {
        console.error('DEBUG: [编辑场景] 获取项目任务数据失败:', error)
        ElMessage.error('获取项目任务数据失败，请稍后重试')
      }
    }
  } else {
    // 新建模式下，从sessionStorage获取之前保存的任务数据
    const savedTasks = sessionStorage.getItem(`project_tasks_${projectId.value}`)
    if (savedTasks) {
      projectTasks.value = JSON.parse(savedTasks)
      // 保存原始任务列表，用于编辑场景的任务状态跟踪
      taskStatusTracking.value.originalTasks = JSON.parse(JSON.stringify(projectTasks.value))
    }
  }
  
  // 从sessionStorage获取之前保存的任务状态跟踪信息
  const savedTaskStatus = sessionStorage.getItem(`task_status_${projectId.value}`)
  if (savedTaskStatus) {
    taskStatusTracking.value = JSON.parse(savedTaskStatus)
  }
})

// 打开案例参照对话框
const openCaseReference = async () => {
  try {
    // 使用fetch API加载清理后的案例数据
    const response = await fetch('/data/case-reference/clean_case_data.json')
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const caseData = await response.json()
    console.log('加载的案例数据:', caseData)
    console.log('数据行数:', caseData.length)
    
    // 确保数据是数组格式
    if (Array.isArray(caseData)) {
      caseTasks.value = caseData
    } else {
      caseTasks.value = []
      console.warn('数据格式不正确，应该为数组')
    }
    
    caseDialogVisible.value = true
  } catch (error) {
    console.error('加载案例数据失败:', error)
    ElMessage.error('加载案例数据失败')
  }
}

// 下载案例Excel
const downloadCaseExcel = () => {
  try {
    // 创建一个临时下载链接
    const link = document.createElement('a')
    link.href = caseExcelUrl
    link.download = '某厂脱硫系统浆液循环泵节能研发项目案例.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    ElMessage.success('案例Excel下载开始')
  } catch (error) {
    console.error('下载案例Excel失败:', error)
    ElMessage.error('下载案例Excel失败')
  }
}

// 获取状态标签类型
const getStatusType = (status) => {
  switch (status) {
    case '已完成':
      return 'success'
    case '进行中':
      return 'primary'
    case '未开始':
      return 'info'
    case '已暂停':
      return 'warning'
    case '已取消':
      return 'danger'
    default:
      return 'info'
  }
}

// 获取任务层级
const getTaskLevel = (taskName) => {
  if (!taskName) return 'root'
  
  // 根任务：如 "一、 项目前期准备阶段"
  if (taskName.includes('、')) {
    return 'root'
  }
  
  // 获取任务编号部分（去掉空格后的第一部分）
  const taskCode = taskName.split(' ')[0]
  
  // 一级任务：如 "1.1 现场勘查与数据收集"
  if (/^\d+\.\d+$/.test(taskCode)) {
    return 'level1'
  }
  
  // 二级任务：如 "1.2.1 方案初稿编写"
  else if (/^\d+\.\d+\.\d+$/.test(taskCode)) {
    return 'level2'
  }
  
  // 三级任务：如 "1.2.1.1 详细编写"
  else if (/^\d+\.\d+\.\d+\.\d+$/.test(taskCode)) {
    return 'level3'
  }
  
  return 'other'
}

// 设置表格行的样式类
const getRowClassName = ({ row, rowIndex }) => {
  const level = getTaskLevel(row['项目名称/结果/过程/要素'])
  return `task-level-${level}`
}

// 格式化任务名称，为不同层级添加缩进
const formatTaskName = (taskName) => {
  const level = getTaskLevel(taskName)
  const indent = level === 'level1' ? '├─ ' : level === 'level2' ? '│  ├─ ' : level === 'level3' ? '│  │  ├─ ' : ''
  return indent + taskName
}

// 获取任务名称的样式类
const getTaskNameClass = (taskName) => {
  const level = getTaskLevel(taskName)
  if (level === 'root' || level === 'level1') {
    return 'task-name-bold'
  }
  return 'task-name-normal'
}
</script>

<style scoped>
.project-create-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.project-create-card {
  margin: 0 auto;
  max-width: 1400px;
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
  justify-content: flex-end;
  gap: 10px;
  padding: 15px;
  background-color: #fafafa;
  border-radius: 8px;
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

/* 案例参照对话框样式 */
.case-dialog-content {
  height: calc(100vh - 200px);
  overflow: auto;
  padding: 20px;
}

.case-introduction {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.case-introduction h4 {
  margin: 0 0 15px 0;
  color: #495057;
  font-size: 16px;
  font-weight: 600;
}

.case-introduction p {
  margin: 0 0 15px 0;
  color: #6c757d;
  line-height: 1.6;
}

.case-stats {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-label {
  color: #6c757d;
  font-weight: 500;
}

.stat-value {
  color: #495057;
  font-weight: 600;
}

.case-tasks-section {
  margin-top: 20px;
}

.case-tasks-section h4 {
  margin: 0 0 15px 0;
  color: #495057;
  font-size: 16px;
  font-weight: 600;
}

.case-tasks-container {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  overflow: auto;
}

.case-tasks-table {
  font-size: 14px;
}

.case-tasks-table .el-table__header {
  background-color: #f8f9fa;
}

/* 案例表格层级样式 */
.case-tasks-table .task-level-root {
  background-color: #e3f2fd !important;
  font-weight: bold !important;
}

.case-tasks-table .task-level-level1 {
  background-color: #f1f8e9 !important;
  padding-left: 20px !important;
}

.case-tasks-table .task-level-level2 {
  background-color: #fff8e1 !important;
  padding-left: 40px !important;
}

.case-tasks-table .task-level-level3 {
  background-color: #fce4ec !important;
  padding-left: 60px !important;
}

.case-tasks-table .task-level-other {
  background-color: #f5f5f5 !important;
  padding-left: 80px !important;
}

/* 任务名称列的字体样式 */
.case-tasks-table .el-table__cell {
  font-family: 'Courier New', monospace;
}

/* 任务名称字体样式 */
.task-name-bold {
  font-weight: bold !important;
  color: #2c3e50 !important;
}

.task-name-normal {
  font-weight: normal !important;
  color: #34495e !important;
}
</style>