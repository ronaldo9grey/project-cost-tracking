<template>
  <div class="daily-report-attachment-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <el-button 
            type="default" 
            size="large" 
            @click="handleGoBack"
            class="back-btn"
          >
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <div class="title-section">
            <h1 class="page-title">
              <el-icon><Paperclip /></el-icon>
              附件管理
            </h1>
            <p class="page-subtitle">{{ reportTitle }}</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button 
            type="primary" 
            size="large" 
            @click="handleUpload"
            :loading="uploading"
            class="upload-btn"
          >
            <el-icon><UploadFilled /></el-icon>
            上传文件
          </el-button>
        </div>
      </div>
    </div>

    <!-- 上传区域 -->
    <div class="upload-section" v-if="!reportId">
      <el-empty description="请先保存日报后再上传附件" />
    </div>

    <div v-else>
      <!-- 文件上传区域 -->
      <div class="upload-area" v-if="showUploadArea">
        <div class="upload-card">
          <div class="upload-header">
            <h3>
              <el-icon><UploadFilled /></el-icon>
              上传文件
            </h3>
            <el-button 
              type="text" 
              @click="showUploadArea = false"
              class="close-btn"
            >
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
          <div class="upload-content">
            <el-upload
              class="upload-dragger"
              drag
              multiple
              :before-upload="beforeUpload"
              :on-success="handleUploadSuccess"
              :on-error="handleUploadError"
              :show-file-list="false"
              :disabled="uploading"
              action=""
            >
              <div class="upload-icon">
                <el-icon size="64" color="#409EFF">
                  <UploadFilled />
                </el-icon>
              </div>
              <div class="upload-text">
                <p class="upload-title">拖拽文件到此处，或点击上传</p>
                <p class="upload-subtitle">支持所有常用格式，单个文件不超过50MB</p>
              </div>
            </el-upload>
          </div>
        </div>
      </div>

      <!-- 附件列表 -->
      <div class="attachments-section">
        <div class="section-header">
          <h3>
            <el-icon><Folder /></el-icon>
            附件列表
            <span class="count">({{ attachments.length }})</span>
          </h3>
        </div>

        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>

        <div v-else-if="attachments.length === 0" class="empty-container">
          <el-empty description="暂无附件">
            <template #image>
              <div class="empty-icon">
                <el-icon size="80" color="#C0C4CC">
                  <Document />
                </el-icon>
              </div>
            </template>
            <el-button type="primary" @click="handleUpload">
              <el-icon><Plus /></el-icon>
              上传第一个文件
            </el-button>
          </el-empty>
        </div>

        <div v-else class="attachments-grid">
          <div 
            v-for="attachment in attachments" 
            :key="attachment.id"
            class="attachment-card"
            :class="{ 'uploading': attachment.uploading }"
          >
            <div class="file-icon">
              <el-icon 
                :size="40" 
                :color="getFileIconColor(attachment.file_type)"
              >
                <component :is="getFileIcon(attachment.file_type)" />
              </el-icon>
            </div>
            
            <div class="file-info">
              <div class="file-name" :title="attachment.file_name">
                {{ attachment.file_name }}
              </div>
              <div class="file-meta">
                <span class="file-size">{{ formatFileSize(attachment.file_size) }}</span>
                <span class="file-date">{{ formatDate(attachment.uploaded_at) }}</span>
              </div>
              <div class="file-uploader">
                <el-icon><User /></el-icon>
                {{ attachment.uploader_name }}
              </div>
            </div>

            <div class="file-actions">
              <el-tooltip 
                :content="isPreviewSupported(attachment.file_type) ? '预览' : '该文件格式不支持预览'" 
                placement="top"
              >
                <el-button 
                  type="text" 
                  size="small"
                  @click="handlePreview(attachment)"
                  :disabled="!isPreviewSupported(attachment.file_type)"
                  class="action-btn"
                  :class="{ 'preview-disabled': !isPreviewSupported(attachment.file_type) }"
                >
                  <el-icon :size="20"><View /></el-icon>
                </el-button>
              </el-tooltip>
              
              <el-tooltip content="下载" placement="top">
                <el-button 
                  type="text" 
                  size="small"
                  @click="handleDownload(attachment)"
                  class="action-btn"
                >
                  <el-icon :size="20"><Download /></el-icon>
                </el-button>
              </el-tooltip>
              
              <el-tooltip content="删除" placement="top">
                <el-button 
                  type="text" 
                  size="small"
                  @click="handleDelete(attachment)"
                  class="action-btn danger"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 隐藏的文件输入 -->
    <input 
      ref="fileInput" 
      type="file" 
      multiple 
      style="display: none"
      @change="handleFileSelect"
      accept="*/*"
    >

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="删除附件"
      width="400px"
      center
    >
      <div class="delete-content">
        <div class="delete-icon">
          <el-icon size="48" color="#F56C6C">
            <WarningFilled />
          </el-icon>
        </div>
        <div class="delete-text">
          <p>确定要删除这个附件吗？</p>
          <p class="file-name-highlight">{{ deleteTarget?.file_name }}</p>
          <p class="warning-text">删除后无法恢复，请谨慎操作！</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button 
          type="danger" 
          @click="confirmDelete"
          :loading="deleteLoading"
        >
          确定删除
        </el-button>
      </template>
    </el-dialog>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      :title="previewTarget?.file_name"
      width="90%"
      height="80vh"
      top="10vh"
      center
    >
      <div class="preview-content" style="height: 70vh; overflow: auto;">
        <div v-if="previewLoading" class="preview-loading">
          <el-skeleton :rows="10" animated />
        </div>
        <div v-else-if="previewContent" class="preview-container" style="height: 100%;">
          <iframe 
            v-if="isPreviewSupported(previewTarget?.file_type)"
            :src="previewContent"
            class="preview-iframe"
            style="width: 100%; height: 65vh; border: none;"
            frameborder="0"
          ></iframe>
          <div v-else class="preview-not-supported">
            <el-icon size="64" color="#909399">
              <Document />
            </el-icon>
            <p>该文件类型不支持在线预览</p>
            <el-button type="primary" @click="handleDownload(previewTarget)">
              <el-icon><Download /></el-icon>
              下载文件
            </el-button>
          </div>
        </div>
        <div v-else class="preview-error">
          <el-icon size="48" color="#F56C6C">
            <CircleClose />
          </el-icon>
          <p>预览加载失败</p>
          <el-button @click="loadPreviewContent">重试</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewDialogVisible = false">关闭</el-button>
        <el-button 
          v-if="previewTarget" 
          type="primary" 
          @click="handleDownload(previewTarget)"
        >
          <el-icon><Download /></el-icon>
          下载
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Paperclip,
  UploadFilled,
  Close,
  Folder,
  Document,
  Plus,
  User,
  View,
  Download,
  Delete,
  WarningFilled,
  CircleClose,
  Picture,
  VideoPlay,
  Service,
  Files,
  FolderOpened
} from '@element-plus/icons-vue'
import {
  getDailyReportAttachments,
  getDailyReport,
  getDailyReportAttachment,
  uploadDailyReportAttachment,
  deleteDailyReportAttachment,
  downloadDailyReportAttachment,
  previewDailyReportAttachment,
  type DailyReportAttachment
} from '../../api/dailyReport'

const router = useRouter()
const route = useRoute()

// 状态变量
const reportId = ref<number | null>(null)
const reportData = ref<any>(null)
const attachments = ref<DailyReportAttachment[]>([])
const loading = ref(false)
const uploading = ref(false)
const showUploadArea = ref(false)
const deleteDialogVisible = ref(false)
const deleteLoading = ref(false)
const deleteTarget = ref<DailyReportAttachment | null>(null)
const previewDialogVisible = ref(false)
const previewTarget = ref<DailyReportAttachment | null>(null)
const previewLoading = ref(false)
const previewContent = ref<string | null>(null)

// 文件输入引用
const fileInput = ref<HTMLInputElement>()

// 计算属性
const reportTitle = computed(() => {
  if (reportData.value && reportData.value.report_date) {
    return `日报附件管理 (${reportData.value.report_date})`
  }
  if (reportId.value) {
    return `日报附件管理 (ID: ${reportId.value})`
  }
  return '附件管理'
})

// 工具函数
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateStr: string): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getFileIcon = (fileType: string) => {
  if (!fileType) return Document
  
  const type = fileType.toLowerCase()
  if (type.includes('image')) return Picture
  if (type.includes('video')) return VideoPlay
  if (type.includes('audio')) return Service
  if (type.includes('text') || type.includes('document')) return Document
  if (type.includes('zip') || type.includes('rar') || type.includes('7z')) return Files
  return Document
}

const getFileIconColor = (fileType: string): string => {
  if (!fileType) return '#909399'
  
  const type = fileType.toLowerCase()
  if (type.includes('image')) return '#67C23A'
  if (type.includes('video')) return '#E6A23C'
  if (type.includes('audio')) return '#F56C6C'
  if (type.includes('text') || type.includes('document')) return '#409EFF'
  if (type.includes('zip') || type.includes('rar') || type.includes('7z')) return '#909399'
  return '#C0C4CC'
}

const isPreviewSupported = (fileType: string): boolean => {
  if (!fileType) return false
  
  const type = fileType.toLowerCase()
  // 只支持图片、PDF和文本文件的预览
  return type.includes('image') || 
         type.includes('pdf') ||
         type.includes('text/plain')
}

// 事件处理函数
const handleGoBack = () => {
  router.push(`/daily-report/${reportId.value}/edit`)
}

const handleUpload = () => {
  if (!reportId.value) {
    ElMessage.warning('请先保存日报后再上传附件')
    return
  }
  showUploadArea.value = true
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    uploadFiles(Array.from(files))
  }
  // 清空输入，允许重复选择同一文件
  target.value = ''
}

const beforeUpload = (file: File) => {
  const maxSize = 50 * 1024 * 1024 // 50MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过50MB')
    return false
  }
  return true
}

const uploadFiles = async (files: File[]) => {
  if (!reportId.value) return
  
  uploading.value = true
  
  for (const file of files) {
    try {
      // 调用API上传文件
      const response = await uploadDailyReportAttachment(reportId.value, file)
      
      // 添加到附件列表
      attachments.value.unshift(response)
      
      ElMessage.success(`文件 ${file.name} 上传成功`)
      
    } catch (error) {
      console.error('文件上传失败:', error)
      ElMessage.error(`文件 ${file.name} 上传失败: ${error.message || '未知错误'}`)
    }
  }
  
  uploading.value = false
  showUploadArea.value = false
}

const handleUploadSuccess = () => {
  ElMessage.success('文件上传成功')
  showUploadArea.value = false
}

const handleUploadError = () => {
  ElMessage.error('文件上传失败')
  uploading.value = false
}

const handleDelete = (attachment: DailyReportAttachment) => {
  deleteTarget.value = attachment
  deleteDialogVisible.value = true
}

const confirmDelete = async () => {
  if (!deleteTarget.value) return
  
  deleteLoading.value = true
  
  try {
    await deleteDailyReportAttachment(deleteTarget.value.id)
    
    attachments.value = attachments.value.filter(a => a.id !== deleteTarget.value!.id)
    ElMessage.success('文件删除成功')
    
    deleteDialogVisible.value = false
    deleteTarget.value = null
  } catch (error) {
    console.error('文件删除失败:', error)
    ElMessage.error('文件删除失败')
  } finally {
    deleteLoading.value = false
  }
}

const handleDownload = async (attachment: DailyReportAttachment) => {
  try {
    const response = await downloadDailyReportAttachment(attachment.id)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    link.download = attachment.file_name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('文件下载开始')
  } catch (error) {
    console.error('文件下载失败:', error)
    ElMessage.error('文件下载失败')
  }
}

const handlePreview = async (attachment: DailyReportAttachment) => {
  // 检查文件是否支持预览
  if (!isPreviewSupported(attachment.file_type)) {
    ElMessage.warning('该文件格式不支持预览，请下载查看')
    return
  }
  
  // 跳转到预览页面
  router.push(`/daily-report/attachment/preview/${attachment.id}`)
}

const loadPreviewContent = async () => {
  if (!previewTarget.value) return
  
  previewLoading.value = true
  
  try {
    const response = await previewDailyReportAttachment(previewTarget.value.id)
    
    if (previewTarget.value.file_type.includes('image')) {
      previewContent.value = response
    } else {
      previewContent.value = 'data:text/html;base64,' + btoa(`
        <html>
          <head><title>${previewTarget.value.file_name}</title></head>
          <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>${previewTarget.value.file_name}</h2>
            <p>文件类型: ${previewTarget.value.file_type}</p>
            <p>文件大小: ${formatFileSize(previewTarget.value.file_size)}</p>
            <p>上传时间: ${formatDate(previewTarget.value.uploaded_at)}</p>
            <p>上传者: ${previewTarget.value.uploader_name}</p>
          </body>
        </html>
      `)
    }
  } catch (error) {
    console.error('预览加载失败:', error)
    ElMessage.error('预览加载失败')
    previewContent.value = null
  } finally {
    previewLoading.value = false
  }
}

// 生命周期
onMounted(() => {
  // 从路由参数获取日报ID
  const routeReportId = route.params.id
  if (routeReportId && typeof routeReportId === 'string') {
    reportId.value = parseInt(routeReportId)
    loadReportData()
    loadAttachments()
  }
})

// 加载日报数据
const loadReportData = async () => {
  if (!reportId.value) return
  
  try {
    const response = await getDailyReport(reportId.value)
    reportData.value = response
  } catch (error) {
    console.error('获取日报数据失败:', error)
    // 即使获取失败也不影响页面显示
  }
}

// 加载附件列表
const loadAttachments = async () => {
  if (!reportId.value) return
  
  loading.value = true
  
  try {
    const response = await getDailyReportAttachments(reportId.value)
    attachments.value = response
  } catch (error) {
    console.error('加载附件列表失败:', error)
    ElMessage.error('加载附件列表失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.daily-report-attachment-container {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

/* 页面头部 */
.page-header {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.title-section .page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-section .page-subtitle {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: #666;
}

.back-btn {
  border-radius: 8px;
  padding: 12px 16px;
}

.upload-btn {
  border-radius: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #409EFF, #66B1FF);
  border: none;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.upload-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}

/* 上传区域 */
.upload-area {
  margin-bottom: 24px;
}

.upload-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.upload-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.upload-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 8px;
}

.upload-content {
  padding: 40px;
}

.upload-dragger {
  width: 100%;
}

.upload-dragger .el-upload {
  width: 100%;
}

.upload-dragger .el-upload-dragger {
  width: 100%;
  height: 200px;
  border: 2px dashed #d9d9d9;
  border-radius: 12px;
  background: #fafafa;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.upload-dragger .el-upload-dragger:hover {
  border-color: #409EFF;
  background: #f0f9ff;
}

.upload-icon {
  margin-bottom: 16px;
}

.upload-text .upload-title {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #1a1a1a;
}

.upload-text .upload-subtitle {
  margin: 8px 0 0 0;
  font-size: 14px;
  color: #666;
}

/* 附件列表 */
.attachments-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.section-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-header .count {
  color: #666;
  font-weight: 400;
  font-size: 14px;
}

.loading-container,
.empty-container {
  padding: 60px 40px;
  text-align: center;
}

.empty-icon {
  margin-bottom: 16px;
}

/* 附件网格 */
.attachments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 16px;
  padding: 20px;
}

.attachment-card {
  background: white;
  border: 1px solid #f0f0f0;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
}

.attachment-card:hover {
  border-color: #409EFF;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.attachment-card.uploading {
  opacity: 0.7;
  background: #f9f9f9;
}

.file-icon {
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a1a;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 12px;
  color: #666;
  flex-wrap: nowrap;
  white-space: nowrap;
}

.file-uploader {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #666;
}

.file-actions {
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
  margin-left: 8px;
}

.attachment-card:hover .file-actions {
  opacity: 1;
}

.action-btn {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: #f0f9ff;
  color: #409EFF;
}

.action-btn.danger:hover {
  background: #fef0f0;
  color: #F56C6C;
}

.action-btn.preview-disabled {
  cursor: not-allowed;
  opacity: 0.4;
}

.action-btn.preview-disabled:hover {
  background: transparent;
  color: #909399;
  transform: none;
}

/* 对话框样式 */
.delete-content {
  text-align: center;
  padding: 20px;
}

.delete-icon {
  margin-bottom: 16px;
}

.delete-text p {
  margin: 8px 0;
  color: #606266;
}

.file-name-highlight {
  font-weight: 600;
  color: #1a1a1a;
  font-size: 16px;
}

.warning-text {
  color: #F56C6C;
  font-size: 14px;
}

.preview-content {
  min-height: 400px;
}

.preview-loading {
  padding: 20px;
}

.preview-container {
  height: 70vh;
  width: 100%;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  border-radius: 8px;
}

.preview-not-supported,
.preview-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #909399;
  text-align: center;
}

.preview-not-supported p,
.preview-error p {
  margin: 16px 0;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .daily-report-attachment-container {
    padding: 12px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-left {
    justify-content: center;
  }
  
  .attachments-grid {
    grid-template-columns: 1fr;
    padding: 12px;
  }
  
  .attachment-card {
    padding: 16px;
  }
  
  .file-actions {
    opacity: 1;
  }
}
</style>
