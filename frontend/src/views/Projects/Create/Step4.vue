<template>
  <div class="project-create-container">
    <el-card shadow="hover" class="project-create-card">
      <template #header>
        <div class="card-header">
          <h2>{{ (isEditMode ? '编辑项目' : '新建项目') + (projectName ? ' - ' + projectName : '') }} - 文档管理</h2>
          <el-breadcrumb separator="/" separator-class="el-icon-arrow-right">
            <el-breadcrumb-item :to="{ path: '/projects' }">项目管理</el-breadcrumb-item>
            <el-breadcrumb-item>{{ (isEditMode ? '编辑项目' : '新建项目') + (projectName ? ' - ' + projectName : '') }}</el-breadcrumb-item>
            <el-breadcrumb-item>文档管理</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
      </template>
      
      <!-- 步骤指示器 -->
      <el-steps :active="3" align-center>
        <el-step title="基本信息" description="设置项目基本信息和合同信息" />
        <el-step title="成本设定" description="设置四大成本的预算和实际值" />
        <el-step title="任务设定" description="创建项目任务" />
        <el-step title="文档管理" description="管理项目相关文档" />
      </el-steps>
      
      <div class="document-container">
        <!-- 任务选择和文档列表区域 -->
        <div class="main-content">
          <div class="left-panel">
            <div class="panel-header">
              <h3>任务列表</h3>
              <el-input
                v-model="taskFilter"
                placeholder="搜索任务"
                prefix-icon="Search"
                style="width: 180px;"
              />
            </div>
            
            <el-tree
              :data="filteredTasks"
              :props="taskTreeProps"
              node-key="task_id"
              highlight-current
              default-expand-all
              class="task-tree"
              @node-click="handleTaskClick"
            />
          </div>
          
          <div class="right-panel">
            <div class="panel-header">
              <h3>文档管理<span v-if="selectedTaskName"> - {{ selectedTaskName }}</span></h3>
            </div>
            
            <!-- 文档列表 -->
            <div class="document-list">
              <el-table :data="currentDocuments" border style="width: 100%" class="document-table">
                <el-table-column prop="attachment_name" label="文档名称" min-width="300" />
                <el-table-column prop="file_type" label="文件类型" width="120">
                  <template #default="scope">
                    <el-tag :type="getFileTypeColor(scope.row.file_type)">
                      {{ getFileTypeText(scope.row.file_type) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="file_size" label="文件大小" width="120">
                  <template #default="scope">
                    {{ formatFileSize(scope.row.file_size) }}
                  </template>
                </el-table-column>
                <el-table-column prop="uploader_name" label="上传人" width="120" />
                <el-table-column label="操作" width="200">
                  <template #default="scope">
                    <el-button type="primary" size="small" @click="downloadDocument(scope.row)">
                      <el-icon><Download /></el-icon>
                      下载
                    </el-button>
                    <el-button type="danger" size="small" @click="deleteDocument(scope.row)">
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            
            <!-- 文档上传区域 -->
            <el-upload
              ref="upload"
              action="#"
              :auto-upload="true"
              :multiple="true"
              :http-request="handleUpload"
              :show-file-list="false"
              class="document-upload"
            >
              <el-button type="primary">
                <el-icon><Plus /></el-icon>
                文件上传
              </el-button>
              <div slot="tip" class="el-upload__tip">
                支持上传 PDF、Word、Excel、PPT、图片等格式文件
              </div>
            </el-upload>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button @click="handlePrevious">上一步</el-button>
          <el-button type="primary" @click="handleEditCompleteClick">{{ isEditMode ? '完成编辑' : '完成创建' }}</el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 文档预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      :title="previewDocumentTitle"
      width="800px"
      fullscreen
    >
      <div class="document-preview">
        <div class="preview-content">
          <!-- 这里应该根据文件类型显示不同的预览内容 -->
          <div v-if="previewDocumentType === 'image'" class="image-preview">
            <el-image
              :src="previewDocumentUrl"
              fit="contain"
              style="width: 100%; height: 100%;"
            />
          </div>
          <div v-else-if="previewDocumentType === 'pdf'" class="pdf-preview">
            <iframe
              :src="previewDocumentUrl"
              style="width: 100%; height: 600px; border: none;"
            />
          </div>
          <div v-else class="other-preview">
            <el-alert
              title="该文件类型暂不支持在线预览，请下载后查看"
              type="info"
              show-icon
            />
            <el-button type="primary" style="margin-top: 20px;" @click="downloadDocument(previewDocumentData)">
              <el-icon><Download /></el-icon>
              下载文件
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Delete, Plus } from '@element-plus/icons-vue'
import { 
  batchCreateProjectTasks,
  batchCreateProjectTaskAttachments,
  batchCreateMaterialCosts,
  batchCreateLaborCosts,
  batchCreateOutsourcingCosts,
  batchCreateIndirectCosts,
  getProjectTasks,
  getProjectTaskAttachments,
  getProjectDetail
} from '../../../api/project'

const router = useRouter()
const route = useRoute()

// 获取项目ID - 从路由参数获取，优先从query参数获取（新建流程）
const projectId = computed(() => {
  // 优先从query参数获取（新建流程）
  const queryId = route.query.projectId
  if (queryId) {
    return String(queryId)
  }
  // 回退到params参数（编辑流程）
  const paramsId = route.params.projectId
  if (paramsId) {
    return String(paramsId)
  }
  return ''
})
// 获取模式参数 - 从查询参数获取
const mode = computed(() => route.query.mode as string)
// 判断是否为编辑模式 - 主要基于mode参数
const isEditMode = computed(() => {
  console.log('DEBUG: [Step4] mode参数值:', mode.value)
  console.log('DEBUG: [Step4] projectId参数值:', route.params.projectId)
  
  // 当mode为'create'时是新建模式，其他情况都是编辑模式
  const result = mode.value !== 'create'
  console.log('DEBUG: [Step4] isEditMode判断结果:', result)
  return result
})

// 项目名称
const projectName = ref<string>('')

// 任务筛选
const taskFilter = ref('')
const selectedTaskId = ref<string>('')
const selectedTaskName = ref<string>('')

// 任务树属性
const taskTreeProps = {
  children: 'children',
  label: 'task_name',
  value: 'task_id'
}

// 从project_tasks表获取的任务数据（扁平数组）
const projectTasks = ref<any[]>([])

// 构建树形任务结构
const buildTaskTree = (tasks: any[]) => {
  // 创建任务ID到任务对象的映射，使用普通对象替代Map
  const taskMap: Record<string, any> = {}
  const rootTasks: any[] = []
  
  // 首先将所有任务放入映射中
  tasks.forEach(task => {
    taskMap[task.task_id] = { ...task, children: [] }
  })
  
  // 然后构建树形结构
  tasks.forEach(task => {
    if (task.parent_task_id && taskMap[task.parent_task_id]) {
      // 如果有父任务，将其添加到父任务的children数组中
      const parentTask = taskMap[task.parent_task_id]
      parentTask.children.push(taskMap[task.task_id])
    } else {
      // 没有父任务的是根任务
      rootTasks.push(taskMap[task.task_id])
    }
  })
  
  return rootTasks
}

// 树形结构的任务列表
const treeTasks = computed(() => {
  return buildTaskTree(projectTasks.value)
})

// 过滤后的任务列表
const filteredTasks = computed(() => {
  if (!taskFilter.value) {
    return treeTasks.value
  }
  
  // 递归过滤任务树
  const filterTask = (tasks: any[]) => {
    return tasks
      .map(task => {
        const children = task.children ? filterTask(task.children) : []
        if (task.task_name.includes(taskFilter.value) || children.length > 0) {
          return { ...task, children }
        }
        return null
      })
      .filter(task => task !== null)
  }
  
  return filterTask(treeTasks.value)
})

// 当前任务的文档列表
const currentDocuments = ref<any[]>([])

// 初始文档数据，用于比较数据是否发生变化
const initialDocuments = ref<any[]>([])

// 上传组件引用
const upload = ref()

// 预览对话框
const previewDialogVisible = ref(false)
const previewDocumentTitle = ref('文档预览')
const previewDocumentUrl = ref('')
const previewDocumentType = ref('')
const previewDocumentData = ref<any>(null)

// 格式化文件大小
const formatFileSize = (size: number) => {
  if (size < 1024) {
    return `${size} B`
  } else if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(2)} KB`
  } else {
    return `${(size / (1024 * 1024)).toFixed(2)} MB`
  }
}

// 获取文件类型对应的颜色
const getFileTypeColor = (fileType: string): string => {
  const colorMap: Record<string, string> = {
    'pdf': 'warning',
    'doc': 'primary',
    'docx': 'primary',
    'xls': 'success',
    'xlsx': 'success',
    'ppt': 'danger',
    'pptx': 'danger',
    'jpg': 'info',
    'jpeg': 'info',
    'png': 'info',
    'gif': 'info',
    'txt': 'info',
    'zip': 'info',
    'rar': 'info',
    'other': 'info'
  }
  return colorMap[fileType] || 'info'
}

// 获取文件类型对应的友好文字
const getFileTypeText = (fileType: string): string => {
  const textMap: Record<string, string> = {
    'pdf': 'PDF',
    'doc': 'Word',
    'docx': 'Word',
    'xls': 'Excel',
    'xlsx': 'Excel',
    'ppt': 'PPT',
    'pptx': 'PPT',
    'jpg': '图片',
    'jpeg': '图片',
    'png': '图片',
    'gif': '图片',
    'txt': '文本',
    'zip': '压缩包',
    'rar': '压缩包',
    'other': '其他'
  }
  return textMap[fileType] || '其他'
}

// 处理任务点击
const handleTaskClick = async (data: any) => {
  // 切换任务时清空文档管理列表
  currentDocuments.value = []
  // 直接切换任务
  selectedTaskId.value = data.task_id
  selectedTaskName.value = data.task_name
  console.log('任务点击', data.task_id)
  
  // 根据任务ID从API获取相关文档
    try {
      console.log('DEBUG: [文档管理] 调用getProjectTaskAttachments API获取文档数据')
      console.log('DEBUG: [文档管理] 请求参数:', { projectId: projectId.value, taskId: data.task_id })
    const attachments = await getProjectTaskAttachments(projectId.value, data.task_id)
      console.log('DEBUG: [文档管理] 获取到的文档数据:', attachments)
      
      // 处理获取到的文档数据，转换为前端需要的格式
      // 注意：axios响应拦截器已经处理了SuccessResponse，直接返回了data字段
      const attachmentsArray = Array.isArray(attachments) ? attachments : [attachments]
      
      currentDocuments.value = attachmentsArray
        .filter(attachment => attachment && attachment.file_name) // 过滤无效记录
        .map(doc => ({
          attachment_id: doc.attachment_id || `DOC_${Date.now()}`,
          project_id: projectId.value,
          task_id: data.task_id,
          attachment_name: doc.file_name || '未命名文件',
          file_name: doc.file_name || '未命名文件',
          file_data: doc.file_data,
          file_path: '',
          file_type: doc.file_name?.split('.').pop()?.toLowerCase() || 'other',
          file_size: doc.file_size || 0,
          upload_by: 'system',
          upload_time: doc.created_at || new Date().toISOString(),
          description: ''
        }))
      console.log('DEBUG: [文档管理] 处理后的文档数据:', currentDocuments.value)
    console.log('DEBUG: [文档管理] 处理后的文档数据:', currentDocuments.value)
  } catch (error) {
    console.error('DEBUG: [文档管理] 获取文档数据失败:', error)
    ElMessage.error('获取文档数据失败，请稍后重试')
  }
}

// 处理文件上传
const handleUpload = (options: any) => {
  if (!selectedTaskId.value) {
    ElMessage.warning('请先选择一个任务节点')
    options.onError(new Error('请先选择一个任务节点'), options.file)
    return
  }
  
  // 读取文件内容并编码为Base64
  const reader = new FileReader()
  reader.onload = (e) => {
    // 获取Base64编码的文件内容（去掉前缀）
    const fileContent = (e.target?.result as string).split(',')[1]
    
    // 构建上传数据
      const uploadData = {
        attachment_id: `DOC_${Date.now()}`, // 生成唯一ID
        project_id: projectId.value,
        task_id: selectedTaskId.value,
        attachment_name: options.file.name,
        file_data: fileContent, // 存储Base64编码的文件内容
        file_path: '/docs/' + options.file.name, // 保留文件路径作为元数据
        file_type: options.file.name.split('.').pop()?.toLowerCase() || 'other',
        file_size: options.file.size,
        upload_by: 'current_user',
        upload_time: new Date().toISOString(),
        uploader_id: '1', // 登录人ID，后续替换为实际登录用户ID
        uploader_name: '管理员', // 登录人名称，后续替换为实际登录用户名称
        description: ''
      }
    
    // 将上传成功的文件添加到文档列表中
    currentDocuments.value.push(uploadData)
    console.log('文件已添加到文档列表，当前文档列表:', currentDocuments.value)
    
    ElMessage.success('文件上传成功')
    options.onSuccess({}, options.file)
  }
  reader.onerror = (e) => {
    console.error('文件读取失败:', e)
    ElMessage.error('文件上传失败，请重试')
    options.onError(new Error('文件读取失败'), options.file)
  }
  
  // 以DataURL格式读取文件
  reader.readAsDataURL(options.file)
}

// 下载文档
const downloadDocument = (docData: any) => {
  console.log('DEBUG: [文档管理] 开始下载文档:', docData)
  
  // 重命名参数，避免与全局document对象冲突
  const documentData = docData
  
  if (!documentData.file_data) {
    ElMessage.error('文档数据不存在，无法下载')
    return
  }
  
  try {
    // 确保使用全局的window.document对象，避免Proxy对象问题
    const globalDocument = window.document
    if (!globalDocument) {
      throw new Error('document对象不可用')
    }
    
    const fileName = documentData.file_name || documentData.attachment_name || '未命名文件'
    console.log('DEBUG: [文档管理] 文件名:', fileName)
    console.log('DEBUG: [文档管理] 文件类型:', documentData.file_type)
    
    // 获取文件内容
    const fileContent = documentData.file_data
    
    // 配置MIME类型
    const mimeTypeMap: Record<string, string> = {
      'pdf': 'application/pdf',
      'doc': 'application/msword',
      'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'xls': 'application/vnd.ms-excel',
      'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'ppt': 'application/vnd.ms-powerpoint',
      'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'jpg': 'image/jpeg',
      'jpeg': 'image/jpeg',
      'png': 'image/png',
      'gif': 'image/gif',
      'txt': 'text/plain',
      'md': 'text/markdown',
      'other': 'application/octet-stream'
    }
    
    const fileType = documentData.file_type || 'other'
    const mimeType = mimeTypeMap[fileType]
    
    // 检查是否为Base64编码
    let finalContent = fileContent
    let isBase64 = false
    
    // 检查是否包含base64前缀
    if (fileContent.includes('base64,')) {
      console.log('DEBUG: [文档管理] 检测到带前缀的Base64编码')
      isBase64 = true
      // 提取Base64数据部分
      finalContent = fileContent.split(',')[1] || fileContent
    } else if (/^[A-Za-z0-9+/=]+$/.test(fileContent.replace(/\s/g, '')) && fileContent.length % 4 === 0) {
      console.log('DEBUG: [文档管理] 检测到纯Base64编码')
      isBase64 = true
      finalContent = fileContent
    }
    
    console.log('DEBUG: [文档管理] Base64检测结果:', isBase64)
    
    let blob: Blob
    
    if (isBase64) {
      console.log('DEBUG: [文档管理] 处理Base64编码内容')
      // Base64解码
      const binaryString = window.atob(finalContent)
      const bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }
      blob = new Blob([bytes], { type: mimeType })
    } else {
      console.log('DEBUG: [文档管理] 处理原始文本内容')
      // 直接使用文本内容创建Blob
      blob = new Blob([finalContent], { type: mimeType })
    }
    
    console.log('DEBUG: [文档管理] Blob创建成功，大小:', blob.size, '类型:', blob.type)
    
    // 创建下载链接
    const url = URL.createObjectURL(blob)
    
    // 使用全局document对象创建a标签
    const link = globalDocument.createElement('a')
    link.href = url
    link.download = fileName
    link.style.display = 'none'
    
    // 关键：将a标签添加到全局document的body中
    globalDocument.body.appendChild(link)
    
    // 触发点击事件
    link.click()
    
    // 延迟清理资源，确保下载完成
    setTimeout(() => {
      // 移除a标签
      globalDocument.body.removeChild(link)
      // 清理URL资源
      URL.revokeObjectURL(url)
      console.log('DEBUG: [文档管理] 资源清理完成')
    }, 2000) // 2秒延迟，确保Chrome完成下载
    
    ElMessage.success(`文档 ${fileName} 下载成功`)
  } catch (error) {
    console.error('DEBUG: [文档管理] 文档下载失败:', error)
    console.error('DEBUG: [文档管理] 错误详情:', error instanceof Error ? error.message : String(error))
    
    // 简化错误处理，直接提示用户
    ElMessage.error(`文档下载失败: ${error instanceof Error ? error.message : '未知错误'}`)
  }
}

// 预览文档
const previewDocument = (document: any) => {
  previewDocumentTitle.value = document.attachment_name
  previewDocumentUrl.value = document.file_path
  previewDocumentData.value = document
  
  // 确定文件类型
  const fileExtension = document.file_path.split('.').pop()?.toLowerCase()
  if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].indexOf(fileExtension || '') !== -1) {
    previewDocumentType.value = 'image'
  } else if (fileExtension === 'pdf') {
    previewDocumentType.value = 'pdf'
  } else {
    previewDocumentType.value = 'other'
  }
  
  previewDialogVisible.value = true
}

// 删除文档
const deleteDocument = (document: any) => {
  ElMessageBox.confirm(`确定要删除文档 "${document.attachment_name}" 吗？`, '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    // TODO: 调用API删除文档
    ElMessage.success('文档已删除')
    // 从本地列表中移除
    const index = currentDocuments.value.findIndex(doc => doc.attachment_id === document.attachment_id)
    if (index !== -1) {
      currentDocuments.value.splice(index, 1)
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 完成创建
const handleComplete = async () => {
  // 显示确认对话框
  await ElMessageBox.confirm(
    '确定要完成项目创建吗？这将保存所有已输入的信息。',
    '确认创建',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      center: true
    }
  );

  try {
    // 初始化成功提示数组
    const successMessages: string[] = []
    
    // 1. 保存任务信息到project_tasks表
    const savedTasks = sessionStorage.getItem(`project_tasks_${projectId.value}`)
    if (savedTasks) {
      let tasks = JSON.parse(savedTasks)
      
      // 过滤掉undefined或null的任务对象
      tasks = tasks.filter((task: any) => task !== undefined && task !== null)
      
      // 处理任务数据，只保留后端ProjectTask模型期望的字段（白名单），并确保数值字段有正确的值
      tasks = tasks.map((task: any) => {
        // 处理数值字段，将空字符串转换为适当的默认值
        const processedTask = {
          task_id: task.task_id || `TASK_${Date.now()}`,
          project_id: task.project_id || projectId.value,
          task_name: task.task_name || '',
          parent_task_id: task.parent_task_id || '',
          task_level: task.task_level || 1, // 确保整数类型
          assignee: task.assignee || '',
          assignee_id: task.assignee_id || '',
          start_date: task.start_date || '',
          end_date: task.end_date || '',
          planned_hours: task.planned_hours ? parseFloat(task.planned_hours) : 0, // 转换为浮点数
          actual_hours: task.actual_hours ? parseFloat(task.actual_hours) : 0, // 转换为浮点数
          adjusted_hours: task.adjusted_hours ? parseFloat(task.adjusted_hours) : 0, // 转换为浮点数
          budget_cost: task.budget_cost ? parseFloat(task.budget_cost) : 0, // 转换为浮点数
          actual_cost: task.actual_cost ? parseFloat(task.actual_cost) : 0, // 转换为浮点数
          status: task.status || '未开始',
          remark: task.remark || '',
          progress: task.progress ? parseFloat(task.progress) : 0, // 转换为浮点数
          actual_end_date: task.actual_end_date || null,
          evaluation: task.evaluation ? parseFloat(task.evaluation) : null, // 转换为浮点数，允许null
          evaluation_desc: task.evaluation_desc || '',
          progress_rootcause: task.progress_rootcause || '',
          measures_results: task.measures_results || '',
          attachment: task.attachment || '',
          isNode: typeof task.isNode === 'boolean' ? task.isNode : false,
          leaf_node: typeof task.leaf_node === 'number' ? task.leaf_node : 1
        };
        return processedTask;
      })
      
      // 调试：检查处理后的任务数据
      console.log('DEBUG: [新建场景] 处理后的任务数据:', tasks);
      if (tasks.length > 0) {
        await batchCreateProjectTasks(tasks)
        successMessages.push('任务信息保存成功')
      }
    }
    
    // 2. 保存成本信息到对应的成本表
    let costSuccess = false
    
    // 2.1 保存物料成本
    const savedMaterialCosts = sessionStorage.getItem(`project_material_costs_${projectId.value}`)
    if (savedMaterialCosts) {
      try {
        const materialCosts = JSON.parse(savedMaterialCosts)
        // 转换物料成本数据为后端期望的格式，匹配数据库表结构
        const transformedMaterialCosts = materialCosts
          .map((cost: any) => {
            // 预算数据
            const budgetCost = {
              project_id: projectId.value,
              material_id: cost.material_id || `MAT_${Date.now()}`,
              name: cost.material_name || '',
              specification: cost.specification || '',
              unit: cost.unit || '',
              quantity: cost.budget_quantity ? parseFloat(cost.budget_quantity) : 0,
              unit_price: cost.budget_unit_price ? parseFloat(cost.budget_unit_price) : 0,
              total_price: (cost.budget_quantity ? parseFloat(cost.budget_quantity) : 0) * (cost.budget_unit_price ? parseFloat(cost.budget_unit_price) : 0),
              cost_type: '预算',
              remark: cost.remark || ''
            }
            
            // 实际数据
            const actualCost = {
              project_id: projectId.value,
              material_id: cost.material_id || `MAT_${Date.now()}_ACT`,
              name: cost.material_name || '',
              specification: cost.specification || '',
              unit: cost.unit || '',
              quantity: cost.actual_quantity ? parseFloat(cost.actual_quantity) : 0,
              unit_price: cost.actual_unit_price ? parseFloat(cost.actual_unit_price) : 0,
              total_price: (cost.actual_quantity ? parseFloat(cost.actual_quantity) : 0) * (cost.actual_unit_price ? parseFloat(cost.actual_unit_price) : 0),
              cost_type: '实际',
              remark: cost.remark || ''
            }
            
            return [budgetCost, actualCost]
          })
          .flat()
          // 过滤掉name或unit为空的记录
          .filter((cost: any) => cost.name.trim() !== '' && cost.unit.trim() !== '')
        
        console.log('DEBUG: [新建场景] 保存物料成本:', transformedMaterialCosts)
        if (transformedMaterialCosts.length > 0) {
          await batchCreateMaterialCosts(transformedMaterialCosts)
          costSuccess = true
        }
      } catch (error) {
        console.error('保存物料成本失败:', error)
      }
    }
    
    // 2.2 保存人力成本
    console.log('DEBUG: [新建场景] 开始处理人力成本数据...')
    const savedLaborCosts = sessionStorage.getItem(`project_labor_costs_${projectId.value}`)
    console.log('DEBUG: [新建场景] 从sessionStorage获取人力成本数据:', savedLaborCosts)
    
    if (savedLaborCosts) {
      try {
        const laborCosts = JSON.parse(savedLaborCosts)
        console.log('DEBUG: [新建场景] 解析后的人力成本数据:', laborCosts)
        
        // 转换人力成本数据为后端期望的格式，匹配数据库表结构
        const transformedLaborCosts = laborCosts
          .filter((cost: any) => {
            console.log('DEBUG: [新建场景] 过滤前的人力成本记录:', cost)
            // 过滤掉没有选择人员且没有输入工时的空记录
            // 检查employee_id是否存在，处理数字和字符串类型
            const isEmployeeIdValid = cost.employee_id !== undefined && cost.employee_id !== null && cost.employee_id !== ''
            
            if (!isEmployeeIdValid) {
              // 检查是否有输入工时或成本数据，允许0值
              const hasBudgetData = typeof cost.budget_hours === 'number' || (cost.budget_hours && parseFloat(cost.budget_hours) >= 0)
              const hasActualData = typeof cost.actual_hours === 'number' || (cost.actual_hours && parseFloat(cost.actual_hours) >= 0)
              const hasHourlyRate = typeof cost.hourly_rate === 'number' || (cost.hourly_rate && parseFloat(cost.hourly_rate) >= 0)
              
              console.log('DEBUG: [新建场景] 检查人力成本记录数据:', { hasBudgetData, hasActualData, hasHourlyRate })
              
              // 如果没有选择人员且没有输入任何数据，则过滤掉
              if (!hasBudgetData && !hasActualData && !hasHourlyRate) {
                console.log('DEBUG: [新建场景] 跳过空的人力成本记录:', cost)
                return false
              }
            }
            console.log('DEBUG: [新建场景] 保留人力成本记录:', cost)
            return true
          })
          .map((cost: any) => {
            const mappedCost = {
              project_id: projectId.value,
              employee_id: cost.employee_id || `EMP_${Date.now()}`,
              year_month: new Date().toISOString().slice(0, 7), // 当前年月
              budget_hours: cost.budget_hours ? parseFloat(cost.budget_hours) : 0,
              actual_hours: cost.actual_hours ? parseFloat(cost.actual_hours) : 0,
              adjusted_hours: cost.adjusted_hours ? parseFloat(cost.adjusted_hours) : 0,
              hourly_rate: cost.hourly_rate ? parseFloat(cost.hourly_rate) : 0,
              budget_cost: (cost.budget_hours ? parseFloat(cost.budget_hours) : 0) * (cost.hourly_rate ? parseFloat(cost.hourly_rate) : 0),
              actual_cost: (cost.actual_hours ? parseFloat(cost.actual_hours) : 0) * (cost.hourly_rate ? parseFloat(cost.hourly_rate) : 0),
              adjusted_cost: (cost.adjusted_hours ? parseFloat(cost.adjusted_hours) : 0) * (cost.hourly_rate ? parseFloat(cost.hourly_rate) : 0),
              remark: cost.remark || '',
              mode: '0' // 添加mode字段，默认为0
            }
            console.log('DEBUG: [新建场景] 转换后的人力成本记录:', mappedCost)
            return mappedCost
          })
        
        console.log('DEBUG: [新建场景] 最终转换后的人力成本数据:', transformedLaborCosts)
        console.log('DEBUG: [新建场景] 转换后的人力成本数据长度:', transformedLaborCosts.length)
        
        if (transformedLaborCosts.length > 0) {
          console.log('DEBUG: [新建场景] 调用batchCreateLaborCosts API...')
          const response = await batchCreateLaborCosts(transformedLaborCosts)
          console.log('DEBUG: [新建场景] batchCreateLaborCosts API返回结果:', response)
          costSuccess = true
        } else {
          console.log('DEBUG: [新建场景] 没有有效的人力成本数据需要保存')
        }
      } catch (error) {
        console.error('保存人力成本失败:', error)
        console.error('错误详细信息:', JSON.stringify(error, null, 2))
      }
    } else {
      console.log('DEBUG: [新建场景] sessionStorage中没有人力成本数据')
    }
    
    // 2.3 保存外包成本
    const savedOutsourcingCosts = sessionStorage.getItem(`project_outsource_costs_${projectId.value}`)
    if (savedOutsourcingCosts) {
      try {
        const outsourcingCosts = JSON.parse(savedOutsourcingCosts)
        // 转换外包成本数据为后端期望的格式，匹配数据库表结构
        const transformedOutsourcingCosts = outsourcingCosts
          .map((cost: any) => {
            // 预算数据
            const budgetCost = {
              project_id: projectId.value,
              service_type: cost.service_type || '',
              description: cost.budget_description || '',
              quantity: 1,
              unit_price: cost.budget_amount ? parseFloat(cost.budget_amount) : 0,
              total_price: cost.budget_amount ? parseFloat(cost.budget_amount) : 0,
              cost_type: '预算',
              remark: cost.remark || ''
            }
            
            // 实际数据
            const actualCost = {
              project_id: projectId.value,
              service_type: cost.service_type || '',
              description: cost.actual_description || '',
              quantity: 1,
              unit_price: cost.actual_amount ? parseFloat(cost.actual_amount) : 0,
              total_price: cost.actual_amount ? parseFloat(cost.actual_amount) : 0,
              cost_type: '实际',
              remark: cost.remark || ''
            }
            
            return [budgetCost, actualCost]
          })
          .flat()
          // 过滤掉service_type为空的记录
          .filter((cost: any) => cost.service_type.trim() !== '')
        
        console.log('DEBUG: [新建场景] 保存外包成本:', transformedOutsourcingCosts)
        if (transformedOutsourcingCosts.length > 0) {
          await batchCreateOutsourcingCosts(transformedOutsourcingCosts)
          costSuccess = true
        }
      } catch (error) {
        console.error('保存外包成本失败:', error)
      }
    }
    
    // 2.4 保存间接成本
    const savedIndirectCosts = sessionStorage.getItem(`project_indirect_costs_${projectId.value}`)
    if (savedIndirectCosts) {
      try {
        const indirectCosts = JSON.parse(savedIndirectCosts)
        // 转换间接成本数据为后端期望的格式，匹配数据库表结构
        const transformedIndirectCosts = indirectCosts
          .map((cost: any) => {
            // 预算数据
            const budgetCost = {
              project_id: projectId.value,
              cost_type: cost.cost_type || '',
              amount: cost.budget_amount ? parseFloat(cost.budget_amount) : 0,
              description: cost.budget_description || '',
              cost_type_flag: '预算',
              total_price: cost.budget_amount ? parseFloat(cost.budget_amount) : 0,
              remark: cost.remark || ''
            }
            
            // 实际数据
            const actualCost = {
              project_id: projectId.value,
              cost_type: cost.cost_type || '',
              amount: cost.actual_amount ? parseFloat(cost.actual_amount) : 0,
              description: cost.actual_description || '',
              cost_type_flag: '实际',
              total_price: cost.actual_amount ? parseFloat(cost.actual_amount) : 0,
              remark: cost.remark || ''
            }
            
            return [budgetCost, actualCost]
          })
          .flat()
          // 过滤掉cost_type为空的记录
          .filter((cost: any) => cost.cost_type.trim() !== '')
        
        console.log('DEBUG: [新建场景] 保存间接成本:', transformedIndirectCosts)
        if (transformedIndirectCosts.length > 0) {
          await batchCreateIndirectCosts(transformedIndirectCosts)
          costSuccess = true
        }
      } catch (error) {
        console.error('保存间接成本失败:', error)
      }
    }
    
    if (costSuccess) {
      successMessages.push('成本信息保存成功')
    }
    
    // 3. 保存文档信息到project_task_attachments表
    if (currentDocuments.value.length > 0) {
      console.log('DEBUG: [新建场景] 保存文档信息:', currentDocuments.value)
      // 转换文档数据格式，匹配数据库表结构
      const attachments = currentDocuments.value.map(doc => ({
        task_id: doc.task_id,
        file_name: doc.attachment_name,
        file_data: doc.file_data, // 发送Base64编码的文件内容
        file_size: doc.file_size,
        uploader_id: doc.uploader_id, // 添加上传人ID
        uploader_name: doc.uploader_name // 添加上传人名称
      }))
      await batchCreateProjectTaskAttachments(attachments)
      successMessages.push('文档信息保存成功')
    }
    
    // 清除sessionStorage中的临时数据
    sessionStorage.removeItem(`project_tasks_${projectId.value}`)
      sessionStorage.removeItem(`project_material_costs_${projectId.value}`)
      sessionStorage.removeItem(`project_labor_costs_${projectId.value}`)
      sessionStorage.removeItem(`project_outsource_costs_${projectId.value}`)
      sessionStorage.removeItem(`project_indirect_costs_${projectId.value}`)
      sessionStorage.removeItem(`project_documents_${projectId.value}`)
      // 清除任务状态跟踪信息
      sessionStorage.removeItem(`task_status_${projectId.value}`)
    
    // 显示成功提示
    if (successMessages.length > 0) {
      ElMessage.success(successMessages.join('；'))
    } else {
      ElMessage.success('项目创建完成')
    }
    
    // 跳转到项目列表页
    router.push('/projects')
  } catch (error) {
    console.error('DEBUG: [新建场景] 保存项目信息失败:', error)
    ElMessage.error('保存项目信息失败，请稍后重试')
  }
}

// 完成编辑按钮点击事件处理
const handleEditCompleteClick = async () => {
  console.log('DEBUG: [编辑场景] 完成编辑按钮被点击');
  console.log('DEBUG: [编辑场景] isEditMode:', isEditMode.value);
  console.log('DEBUG: [编辑场景] projectId:', projectId.value);
  
  if (isEditMode.value) {
    console.log('DEBUG: [编辑场景] 调用handleEditComplete函数');
    await handleEditComplete();
  } else {
    console.log('DEBUG: [编辑场景] 调用handleComplete函数');
    await handleComplete();
  }
};

// 完成编辑
const handleEditComplete = async () => {
  console.log('DEBUG: [编辑场景] 开始执行handleEditComplete函数');
  
  // 显示确认对话框
  try {
    console.log('DEBUG: [编辑场景] 准备显示确认对话框');
    await ElMessageBox.confirm(
      '确定要完成项目编辑吗？这将保存所有已输入的信息。',
      '确认编辑',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      }
    );
    console.log('DEBUG: [编辑场景] 用户确认完成编辑');
  } catch (error) {
    console.log('DEBUG: [编辑场景] 用户取消了完成编辑', error);
    return;
  }

  try {
    // 初始化成功提示数组
    const successMessages: string[] = []
    
    // 1. 保存任务信息到project_tasks表
    const savedTasks = sessionStorage.getItem(`project_tasks_${projectId.value}`)
    if (savedTasks) {
      let tasks = JSON.parse(savedTasks)
      // 处理任务数据，只保留后端ProjectTask模型期望的字段（白名单），并确保数值字段有正确的值
      tasks = tasks.map((task: any) => {
        // 处理数值字段，将空字符串转换为适当的默认值
        const processedTask = {
          task_id: task.task_id,
          project_id: task.project_id,
          task_name: task.task_name,
          parent_task_id: task.parent_task_id,
          task_level: task.task_level || 1, // 确保整数类型
          assignee: task.assignee,
          assignee_id: task.assignee_id,
          start_date: task.start_date,
          end_date: task.end_date,
          planned_hours: task.planned_hours ? parseFloat(task.planned_hours) : 0, // 转换为浮点数
          actual_hours: task.actual_hours ? parseFloat(task.actual_hours) : 0, // 转换为浮点数
          adjusted_hours: task.adjusted_hours ? parseFloat(task.adjusted_hours) : 0, // 转换为浮点数
          budget_cost: task.budget_cost ? parseFloat(task.budget_cost) : 0, // 转换为浮点数
          actual_cost: task.actual_cost ? parseFloat(task.actual_cost) : 0, // 转换为浮点数
          status: task.status,
          remark: task.remark,
          progress: task.progress ? parseFloat(task.progress) : 0, // 转换为浮点数
          actual_end_date: task.actual_end_date,
          evaluation: task.evaluation ? parseFloat(task.evaluation) : null, // 转换为浮点数，允许null
          evaluation_desc: task.evaluation_desc,
          progress_rootcause: task.progress_rootcause,
          measures_results: task.measures_results,
          attachment: task.attachment,
          isNode: task.isNode,
          leaf_node: task.leaf_node
        };
        return processedTask;
      })
      
      // 调试：检查处理后的任务数据
      console.log('DEBUG: [编辑场景] 处理后的任务数据:', tasks);
      
      // 从sessionStorage获取任务状态跟踪信息
      const taskStatusJson = sessionStorage.getItem(`task_status_${projectId.value}`)
      const taskStatusTracking = taskStatusJson ? JSON.parse(taskStatusJson) : {
        added: [],
        updated: [],
        deleted: [],
        originalTasks: []
      }
      
      console.log('DEBUG: [编辑场景] 任务状态跟踪信息:', taskStatusTracking);
      
      // 根据任务状态分别处理：新增、修改、删除
      if (tasks.length > 0 || taskStatusTracking.deleted.length > 0) {
        // 1. 处理新增任务
        const addedTasks = tasks.filter((task: any) => taskStatusTracking.added.includes(task.task_id))
        if (addedTasks.length > 0) {
          console.log('DEBUG: [编辑场景] 新增任务:', addedTasks);
          await batchCreateProjectTasks(addedTasks)
        }
        
        // 2. 处理修改任务
        const updatedTasks = tasks.filter((task: any) => taskStatusTracking.updated.includes(task.task_id))
        if (updatedTasks.length > 0) {
          console.log('DEBUG: [编辑场景] 修改任务:', updatedTasks);
          await batchCreateProjectTasks(updatedTasks)
        }
        
        // 3. 处理删除任务
        if (taskStatusTracking.deleted.length > 0) {
          console.log('DEBUG: [编辑场景] 删除任务ID列表:', taskStatusTracking.deleted);
          // 调用删除API处理已删除任务
          // 注意：这里需要根据后端API设计来决定如何处理删除，
          // 可以批量删除或单个删除
          for (const taskId of taskStatusTracking.deleted) {
            // 调用删除任务API
            // await deleteProjectTask(taskId)
            console.log('DEBUG: [编辑场景] 删除任务:', taskId);
          }
        }
        
        successMessages.push('任务信息保存成功')
      }
    }
    
    // 2. 保存成本信息到对应的成本表
    let costSuccess = false
    
    // 2.1 保存物料成本
    const savedMaterialCosts = sessionStorage.getItem(`project_material_costs_${projectId.value}`)
    if (savedMaterialCosts) {
      try {
        const materialCosts = JSON.parse(savedMaterialCosts)
        // 转换物料成本数据为后端期望的格式，匹配数据库表结构
        const transformedMaterialCosts = materialCosts
          .map((cost: any) => {
            // 预算数据
            const budgetCost = {
              project_id: projectId.value,
              material_id: cost.material_id || `MAT_${Date.now()}`,
              name: cost.material_name || '',
              specification: cost.specification || '',
              unit: cost.unit || '',
              quantity: cost.budget_quantity ? parseFloat(cost.budget_quantity) : 0,
              unit_price: cost.budget_unit_price ? parseFloat(cost.budget_unit_price) : 0,
              total_price: (cost.budget_quantity ? parseFloat(cost.budget_quantity) : 0) * (cost.budget_unit_price ? parseFloat(cost.budget_unit_price) : 0),
              cost_type: '预算',
              remark: cost.remark || ''
            }
            
            // 实际数据
            const actualCost = {
              project_id: projectId.value,
              material_id: cost.material_id || `MAT_${Date.now()}_ACT`,
              name: cost.material_name || '',
              specification: cost.specification || '',
              unit: cost.unit || '',
              quantity: cost.actual_quantity ? parseFloat(cost.actual_quantity) : 0,
              unit_price: cost.actual_unit_price ? parseFloat(cost.actual_unit_price) : 0,
              total_price: (cost.actual_quantity ? parseFloat(cost.actual_quantity) : 0) * (cost.actual_unit_price ? parseFloat(cost.actual_unit_price) : 0),
              cost_type: '实际',
              remark: cost.remark || ''
            }
            
            return [budgetCost, actualCost]
          })
          .flat()
          // 过滤掉name或unit为空的记录
          .filter((cost: any) => cost.name.trim() !== '' && cost.unit.trim() !== '')
        
        console.log('DEBUG: [编辑场景] 保存物料成本:', transformedMaterialCosts)
        if (transformedMaterialCosts.length > 0) {
          // 使用batchCreateMaterialCosts API，后端会处理全删全插
          await batchCreateMaterialCosts(transformedMaterialCosts)
          costSuccess = true
        }
      } catch (error) {
        console.error('DEBUG: [编辑场景] 保存物料成本失败:', error)
      }
    }
    
    // 2.2 保存人力成本
    console.log('DEBUG: [编辑场景] 开始处理人力成本数据...')
    const savedLaborCosts = sessionStorage.getItem(`project_labor_costs_${projectId.value}`)
    console.log('DEBUG: [编辑场景] 从sessionStorage获取人力成本数据:', savedLaborCosts)
    
    if (savedLaborCosts) {
      try {
        const laborCosts = JSON.parse(savedLaborCosts)
        console.log('DEBUG: [编辑场景] 解析后的人力成本数据:', laborCosts)
        
        // 转换人力成本数据为后端期望的格式，匹配数据库表结构
        const transformedLaborCosts = laborCosts
          .filter((cost: any) => {
            console.log('DEBUG: [编辑场景] 过滤前的人力成本记录:', cost)
            // 过滤掉没有选择人员且没有输入工时的空记录
            // 检查employee_id是否存在，处理数字和字符串类型
            const isEmployeeIdValid = cost.employee_id !== undefined && cost.employee_id !== null && cost.employee_id !== ''
            
            if (!isEmployeeIdValid) {
              // 检查是否有输入工时或成本数据，允许0值
              const hasBudgetData = typeof cost.budget_hours === 'number' || (cost.budget_hours && parseFloat(cost.budget_hours) >= 0)
              const hasActualData = typeof cost.actual_hours === 'number' || (cost.actual_hours && parseFloat(cost.actual_hours) >= 0)
              const hasHourlyRate = typeof cost.hourly_rate === 'number' || (cost.hourly_rate && parseFloat(cost.hourly_rate) >= 0)
              
              console.log('DEBUG: [编辑场景] 检查人力成本记录数据:', { hasBudgetData, hasActualData, hasHourlyRate })
              
              // 如果没有选择人员且没有输入任何数据，则过滤掉
              if (!hasBudgetData && !hasActualData && !hasHourlyRate) {
                console.log('DEBUG: [编辑场景] 跳过空的人力成本记录:', cost)
                return false
              }
            }
            console.log('DEBUG: [编辑场景] 保留人力成本记录:', cost)
            return true
          })
          .map((cost: any) => {
            const mappedCost = {
              project_id: projectId.value,
              employee_id: cost.employee_id || `EMP_${Date.now()}`,
              year_month: new Date().toISOString().slice(0, 7), // 当前年月
              budget_hours: cost.budget_hours ? parseFloat(cost.budget_hours) : 0,
              actual_hours: cost.actual_hours ? parseFloat(cost.actual_hours) : 0,
              adjusted_hours: cost.adjusted_hours ? parseFloat(cost.adjusted_hours) : 0,
              hourly_rate: cost.hourly_rate ? parseFloat(cost.hourly_rate) : 0,
              budget_cost: (cost.budget_hours ? parseFloat(cost.budget_hours) : 0) * (cost.hourly_rate ? parseFloat(cost.hourly_rate) : 0),
              actual_cost: (cost.actual_hours ? parseFloat(cost.actual_hours) : 0) * (cost.hourly_rate ? parseFloat(cost.hourly_rate) : 0),
              adjusted_cost: (cost.adjusted_hours ? parseFloat(cost.adjusted_hours) : 0) * (cost.hourly_rate ? parseFloat(cost.hourly_rate) : 0),
              remark: cost.remark || '',
              mode: '0' // 添加mode字段，默认为0
            }
            console.log('DEBUG: [编辑场景] 转换后的人力成本记录:', mappedCost)
            return mappedCost
          })
        
        console.log('DEBUG: [编辑场景] 最终转换后的人力成本数据:', transformedLaborCosts)
        console.log('DEBUG: [编辑场景] 转换后的人力成本数据长度:', transformedLaborCosts.length)
        
        if (transformedLaborCosts.length > 0) {
          console.log('DEBUG: [编辑场景] 调用batchCreateLaborCosts API...')
          // 使用batchCreateLaborCosts API，后端会处理全删全插
          const response = await batchCreateLaborCosts(transformedLaborCosts)
          console.log('DEBUG: [编辑场景] batchCreateLaborCosts API返回结果:', response)
          costSuccess = true
        } else {
          console.log('DEBUG: [编辑场景] 没有有效的人力成本数据需要保存')
        }
      } catch (error) {
        console.error('DEBUG: [编辑场景] 保存人力成本失败:', error)
        console.error('DEBUG: [编辑场景] 错误详细信息:', JSON.stringify(error, null, 2))
      }
    } else {
      console.log('DEBUG: [编辑场景] sessionStorage中没有人力成本数据')
    }
    
    // 2.3 保存外包成本
    const savedOutsourcingCosts = sessionStorage.getItem(`project_outsource_costs_${projectId.value}`)
    if (savedOutsourcingCosts) {
      try {
        const outsourcingCosts = JSON.parse(savedOutsourcingCosts)
        // 转换外包成本数据为后端期望的格式，匹配数据库表结构
        const transformedOutsourcingCosts = outsourcingCosts
          .map((cost: any) => {
            // 预算数据
            const budgetCost = {
              project_id: projectId.value,
              service_type: cost.service_type || '',
              description: cost.budget_description || '',
              quantity: 1,
              unit_price: cost.budget_amount ? parseFloat(cost.budget_amount) : 0,
              total_price: cost.budget_amount ? parseFloat(cost.budget_amount) : 0,
              cost_type: '预算',
              remark: cost.remark || ''
            }
            
            // 实际数据
            const actualCost = {
              project_id: projectId.value,
              service_type: cost.service_type || '',
              description: cost.actual_description || '',
              quantity: 1,
              unit_price: cost.actual_amount ? parseFloat(cost.actual_amount) : 0,
              total_price: cost.actual_amount ? parseFloat(cost.actual_amount) : 0,
              cost_type: '实际',
              remark: cost.remark || ''
            }
            
            return [budgetCost, actualCost]
          })
          .flat()
          // 过滤掉service_type为空的记录
          .filter((cost: any) => cost.service_type.trim() !== '')
        
        console.log('DEBUG: [编辑场景] 保存外包成本:', transformedOutsourcingCosts)
        if (transformedOutsourcingCosts.length > 0) {
          // 使用batchCreateOutsourcingCosts API，后端会处理全删全插
          await batchCreateOutsourcingCosts(transformedOutsourcingCosts)
          costSuccess = true
        }
      } catch (error) {
        console.error('DEBUG: [编辑场景] 保存外包成本失败:', error)
      }
    }
    
    // 2.4 保存间接成本
    const savedIndirectCosts = sessionStorage.getItem(`project_indirect_costs_${projectId.value}`)
    if (savedIndirectCosts) {
      try {
        const indirectCosts = JSON.parse(savedIndirectCosts)
        // 转换间接成本数据为后端期望的格式，匹配数据库表结构
        const transformedIndirectCosts = indirectCosts
          .map((cost: any) => {
            // 预算数据
            const budgetCost = {
              project_id: projectId.value,
              cost_type: cost.cost_type || '',
              amount: cost.budget_amount ? parseFloat(cost.budget_amount) : 0,
              description: cost.budget_description || '',
              cost_type_flag: '预算',
              total_price: cost.budget_amount ? parseFloat(cost.budget_amount) : 0,
              remark: cost.remark || ''
            }
            
            // 实际数据
            const actualCost = {
              project_id: projectId.value,
              cost_type: cost.cost_type || '',
              amount: cost.actual_amount ? parseFloat(cost.actual_amount) : 0,
              description: cost.actual_description || '',
              cost_type_flag: '实际',
              total_price: cost.actual_amount ? parseFloat(cost.actual_amount) : 0,
              remark: cost.remark || ''
            }
            
            return [budgetCost, actualCost]
          })
          .flat()
          // 过滤掉cost_type为空的记录
          .filter((cost: any) => cost.cost_type.trim() !== '')
        
        console.log('DEBUG: [编辑场景] 保存间接成本:', transformedIndirectCosts)
        if (transformedIndirectCosts.length > 0) {
          // 使用batchCreateIndirectCosts API，后端会处理全删全插
          await batchCreateIndirectCosts(transformedIndirectCosts)
          costSuccess = true
        }
      } catch (error) {
        console.error('DEBUG: [编辑场景] 保存间接成本失败:', error)
      }
    }
    
    if (costSuccess) {
      successMessages.push('成本信息保存成功')
    }
    
    // 3. 保存文档信息到project_task_attachments表
    if (currentDocuments.value.length > 0) {
      console.log('DEBUG: [编辑场景] 保存文档信息:', currentDocuments.value)
      // 转换文档数据格式，匹配数据库表结构
      const attachments = currentDocuments.value.map(doc => ({
        task_id: doc.task_id,
        file_name: doc.attachment_name,
        file_data: doc.file_data, // 发送Base64编码的文件内容
        file_size: doc.file_size,
        uploader_id: doc.uploader_id, // 添加上传人ID
        uploader_name: doc.uploader_name // 添加上传人名称
      }))
      // 使用batchCreateProjectTaskAttachments API处理文档
      await batchCreateProjectTaskAttachments(attachments)
      successMessages.push('文档信息保存成功')
    }
    
    // 清除sessionStorage中的临时数据
    sessionStorage.removeItem(`project_tasks_${projectId.value}`)
    sessionStorage.removeItem(`project_material_costs_${projectId.value}`)
    sessionStorage.removeItem(`project_labor_costs_${projectId.value}`)
    sessionStorage.removeItem(`project_outsource_costs_${projectId.value}`)
    sessionStorage.removeItem(`project_indirect_costs_${projectId.value}`)
    sessionStorage.removeItem(`project_documents_${projectId.value}`)
    
    // 显示成功提示
    if (successMessages.length > 0) {
      ElMessage.success(successMessages.join('；'))
    } else {
      ElMessage.success('项目编辑完成')
    }
    
    // 跳转到项目列表页
    router.push('/projects')
  } catch (error) {
    console.error('DEBUG: [编辑场景] 保存项目信息失败:', error)
    ElMessage.error('保存项目信息失败，请稍后重试')
  }
}

// 跳转到上一步
const handlePrevious = () => {
  console.log('DEBUG: [文档管理] 点击上一步按钮')
  
  // 保存文档数据到sessionStorage
  sessionStorage.setItem(`project_documents_${projectId.value}`, JSON.stringify(currentDocuments.value))
  console.log('文档数据已保存到sessionStorage', currentDocuments.value)
  
  // 直接跳转到上一步，统一使用query参数传递
  console.log('DEBUG: [Step4] 跳转到Step3，mode=', mode.value)
  router.push({
    name: 'ProjectCreateStep3',
    query: { 
      mode: mode.value, 
      projectId: projectId.value
    }
  })
}

// 获取项目详情
const fetchProjectDetailData = async () => {
  if (!projectId.value) return
  
  try {
    const project = await getProjectDetail(Number(projectId.value))
    projectName.value = project.name
  } catch (error) {
    console.error('获取项目详情失败:', error)
    // 失败时不显示错误，保持默认文本
  }
}

// 初始加载数据
onMounted(async () => {
  // 获取项目详情
  await fetchProjectDetailData()
  
  // 这里应该调用API获取项目任务和文档数据
  console.log('加载项目任务和文档数据', projectId.value)
  
  // 编辑模式下，优先从API获取任务数据
  if (isEditMode.value) {
    console.log('DEBUG: [编辑场景] 从API获取任务数据')
    try {
      // 调用API获取项目任务数据
      const response = await getProjectTasks(Number(projectId.value))
      console.log('DEBUG: [编辑场景] 获取到的任务数据:', response)
      
      if (response && response.length > 0) {
        projectTasks.value = response
        // 保存到sessionStorage
        sessionStorage.setItem(`project_tasks_${projectId.value}`, JSON.stringify(projectTasks.value))
      }
    } catch (error) {
      console.error('DEBUG: [编辑场景] 获取项目任务数据失败:', error)
      ElMessage.error('获取项目任务数据失败，请稍后重试')
      
      // API获取失败时，回退到sessionStorage数据
      const savedTasks = sessionStorage.getItem(`project_tasks_${projectId.value}`)
      if (savedTasks) {
        const tasks = JSON.parse(savedTasks)
        projectTasks.value = tasks
      }
    }
  } else {
    // 新建模式下，从sessionStorage获取项目任务数据
    const savedTasks = sessionStorage.getItem(`project_tasks_${projectId.value}`)
    if (savedTasks) {
      const tasks = JSON.parse(savedTasks)
      projectTasks.value = tasks
    }
  }
  
  // 从sessionStorage获取文档数据
  const savedDocuments = sessionStorage.getItem(`project_documents_${projectId.value}`)
  if (savedDocuments) {
    const documents = JSON.parse(savedDocuments)
    currentDocuments.value = documents
    console.log('从sessionStorage加载文档数据', currentDocuments.value)
  }
  
  // 保存初始文档数据，用于比较数据是否发生变化
  initialDocuments.value = JSON.parse(JSON.stringify(currentDocuments.value))
  
  // TODO: 从API获取文档数据
  // currentDocuments.value = await getTaskAttachments(projectId.value, selectedTaskId.value)
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

.document-container {
  margin-top: 30px;
}

.main-content {
  display: flex;
  gap: 20px;
  height: 600px;
  margin-bottom: 20px;
}

.left-panel {
  width: 350px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.right-panel {
  flex: 1;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.task-tree {
  flex: 1;
  overflow: auto;
  padding: 10px;
}

.document-list {
  flex: 1;
  overflow: auto;
  padding: 20px;
}

.document-table {
  width: 100%;
}

.document-upload {
  padding: 20px;
  border-top: 1px solid #e4e7ed;
  background-color: #fafafa;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 15px;
  background-color: #fafafa;
  border-radius: 8px;
}

.document-preview {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.preview-content {
  flex: 1;
  overflow: auto;
  padding: 20px;
}

.image-preview {
  text-align: center;
}

.pdf-preview {
  height: 100%;
}

.other-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
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
</style>