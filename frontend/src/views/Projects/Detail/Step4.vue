<template>
  <div class="project-create-container">
    <el-card shadow="hover" class="project-create-card">
      <template #header>
        <div class="card-header">
          <h2>项目详情 - 文档管理</h2>
          <el-breadcrumb separator="/" separator-class="el-icon-arrow-right">
            <el-breadcrumb-item :to="{ path: '/projects' }">项目管理</el-breadcrumb-item>
            <el-breadcrumb-item>项目详情</el-breadcrumb-item>
            <el-breadcrumb-item>文档管理</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
      </template>
      
      <!-- 步骤指示器 -->
      <el-steps :active="3" align-center>
        <el-step title="基本信息" description="查看项目基本信息和合同信息" />
        <el-step title="成本设定" description="查看四大成本设置" />
        <el-step title="任务设定" description="查看项目任务设置" />
        <el-step title="文档管理" description="查看项目文档" />
      </el-steps>
      
      <div class="document-container">
        <!-- 任务选择和文档列表区域 -->
        <div class="main-content">
          <div class="left-panel">
            <div class="panel-header">
              <h3>任务列表</h3>
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
                <el-table-column label="操作" width="150">
                  <template #default="scope">
                    <el-button type="primary" size="small" @click="downloadDocument(scope.row)">
                      <el-icon><Download /></el-icon>
                      下载
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              
              <!-- 空状态提示 -->
              <div v-if="currentDocuments.length === 0" class="empty-state">
                <el-empty description="该任务暂无文档" />
              </div>
            </div>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button @click="goBack">返回项目列表</el-button>
          <el-button @click="handlePrevious">查看上一步</el-button>
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
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { getProjectTasks, getProjectTaskAttachments, getProjectDetail } from '../../../api/project'

const router = useRouter()
const route = useRoute()

// 获取项目ID
const projectId = computed(() => route.params.id as string)

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
    console.log('DEBUG: [文档管理] 请求参数:', { projectId: Number(projectId), taskId: data.task_id })
    const attachments = await getProjectTaskAttachments(Number(projectId), data.task_id)
    console.log('DEBUG: [文档管理] 获取到的文档数据:', attachments)
    
    // 处理获取到的文档数据，转换为前端需要的格式
    // 注意：axios响应拦截器已经处理了SuccessResponse，直接返回了data字段
    const attachmentsArray = Array.isArray(attachments) ? attachments : [attachments]
    
    currentDocuments.value = attachmentsArray
      .filter(attachment => attachment && attachment.file_name) // 过滤无效记录
      .map(doc => ({
        attachment_id: doc.attachment_id || `DOC_${Date.now()}`,
        project_id: projectId,
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
  } catch (error) {
    console.error('DEBUG: [文档管理] 获取文档数据失败:', error)
    ElMessage.error('获取文档数据失败，请稍后重试')
  }
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

// 跳转到上一步
const handlePrevious = () => {
  router.push({
    name: 'ProjectDetailGantt',
    params: { id: projectId.value }
  })
}

// 返回项目列表
const goBack = () => {
  router.push('/projects')
}

// 获取项目详情
const fetchProjectDetail = async () => {
  try {
    const detail = await getProjectDetail(Number(projectId))
    projectName.value = detail.project_name || ''
  } catch (error) {
    console.error('获取项目详情失败:', error)
  }
}

// 获取项目任务数据
const fetchProjectTasks = async () => {
  try {
    const tasks = await getProjectTasks(Number(projectId))
    projectTasks.value = tasks || []
  } catch (error) {
    console.error('获取项目任务数据失败:', error)
    ElMessage.error('获取项目任务数据失败')
  }
}

// 初始化
onMounted(() => {
  fetchProjectDetail()
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

.document-container {
  margin-top: 30px;
}

.main-content {
  display: flex;
  gap: 20px;
  min-height: 600px;
}

.left-panel {
  width: 300px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.right-panel {
  flex: 1;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #fff;
  border-radius: 8px 8px 0 0;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.task-tree {
  padding: 20px;
  max-height: 560px;
  overflow-y: auto;
}

.document-list {
  padding: 20px;
}

.document-table {
  margin-bottom: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 0;
}

.document-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  padding: 20px;
  text-align: center;
  background-color: #fafafa;
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

.document-preview {
  height: calc(100vh - 100px);
  overflow: auto;
}

.preview-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.image-preview {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.pdf-preview {
  width: 100%;
  height: 100%;
}

.other-preview {
  text-align: center;
  padding: 40px;
}
</style>