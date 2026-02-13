<template>
  <div class="preview-page">
    <!-- 顶部导航栏 -->
    <div class="preview-header">
      <div class="header-left">
        <el-button type="text" @click="handleGoBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>
      <div class="header-center">
        <h1 class="page-title">{{ fileInfo?.file_name || '文件预览' }}</h1>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleDownload" :loading="downloading">
          <el-icon><Download /></el-icon>
          下载文件
        </el-button>
      </div>
    </div>

    <!-- 预览内容区 -->
    <div class="preview-content">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="15" animated />
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <el-icon size="64" color="#F56C6C">
          <CircleClose />
        </el-icon>
        <h3>预览加载失败</h3>
        <p>{{ error }}</p>
        <el-button type="primary" @click="loadPreview">重新加载</el-button>
      </div>

      <!-- 预览内容 -->
      <div v-else-if="previewContent" class="preview-container">
        <!-- 图片预览 -->
        <div v-if="isImage" class="image-preview">
          <img 
            :src="previewContent" 
            :alt="fileInfo?.file_name"
            class="preview-image"
            @load="onImageLoad"
            @error="onImageError"
          />
        </div>

        <!-- PDF预览 -->
        <div v-else-if="isPDF" class="pdf-preview">
          <iframe 
            :src="previewContent"
            class="pdf-iframe"
            frameborder="0"
          ></iframe>
        </div>

        <!-- 文本预览 -->
        <div v-else-if="isText" class="text-preview">
          <div class="text-content">
            <pre>{{ textContent }}</pre>
          </div>
        </div>

        <!-- 不支持的格式 -->
        <div v-else class="unsupported-preview">
          <el-icon size="64" color="#909399">
            <Document />
          </el-icon>
          <h3>该文件格式不支持在线预览</h3>
          <p>请下载文件到本地查看</p>
        </div>
      </div>
    </div>

    <!-- 文件信息面板 -->
    <div class="file-info-panel" v-if="fileInfo">
      <h3>文件信息</h3>
      <div class="info-grid">
        <div class="info-item">
          <span class="label">文件名：</span>
          <span class="value">{{ fileInfo.file_name }}</span>
        </div>
        <div class="info-item">
          <span class="label">文件大小：</span>
          <span class="value">{{ formatFileSize(fileInfo.file_size) }}</span>
        </div>
        <div class="info-item">
          <span class="label">文件类型：</span>
          <span class="value">{{ fileInfo.file_type }}</span>
        </div>
        <div class="info-item">
          <span class="label">上传时间：</span>
          <span class="value">{{ formatDate(fileInfo.uploaded_at) }}</span>
        </div>
        <div class="info-item">
          <span class="label">上传者：</span>
          <span class="value">{{ fileInfo.uploader_name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Download, CircleClose, Document } from '@element-plus/icons-vue'
import { getDailyReportAttachment, previewDailyReportAttachment } from '../../api/DailyReport'

// 路由
const route = useRoute()
const router = useRouter()

// 状态
const fileInfo = ref<any>(null)
const previewContent = ref<string>('')
const loading = ref(false)
const error = ref('')
const downloading = ref(false)
const textContent = ref('')

// 路由准备状态
const isRouteReady = ref(false)

// 附件ID - 安全获取路由参数
const attachmentId = ref<string>('')

// 监听路由参数变化
watch(() => route.params.id, (newId) => {
  console.log('🔍 路由参数变化:', newId)
  
  if (newId && newId !== '') {
    attachmentId.value = newId as string
    isRouteReady.value = true
    console.log('🔑 附件ID已设置:', attachmentId.value)
    console.log('✅ 路由准备就绪')
  } else {
    isRouteReady.value = false
    console.log('⏳ 等待路由参数...')
  }
}, { immediate: true })

// 计算属性
const isImage = computed(() => {
  return fileInfo.value?.file_type?.includes('image')
})

const isPDF = computed(() => {
  return fileInfo.value?.file_type?.includes('pdf')
})

const isText = computed(() => {
  return fileInfo.value?.file_type?.includes('text/plain')
})

// 页面状态跟踪
const isInitialized = ref(false)

// 初始化加载
const initializePreview = async () => {
  console.log('🚀 initializePreview被调用:', {
    attachmentId: attachmentId.value,
    isInitialized: isInitialized.value
  })
  
  // 如果已经初始化过，跳过
  if (isInitialized.value) {
    console.log('⏳ 已初始化，跳过')
    return
  }
  
  // 如果没有附件ID，尝试从路由获取
  if (!attachmentId.value && route.params.id) {
    attachmentId.value = route.params.id as string
    console.log('🔄 从路由获取附件ID:', attachmentId.value)
  }
  
  if (!attachmentId.value) {
    console.warn('⚠️ 没有附件ID，跳过初始化')
    return
  }
  
  console.log('✅ 开始初始化预览，附件ID:', attachmentId.value)
  isInitialized.value = true
  
  try {
    await loadPreview()
  } catch (error) {
    console.error('❌ 初始化失败:', error)
    isInitialized.value = false // 允许重试
  }
}

// 监听路由变化
watch(
  () => route.params.id,
  (newId, oldId) => {
    console.log('🔄 路由变化检测:', { oldId, newId })
    
    // 重置状态
    isInitialized.value = false
    fileInfo.value = null
    previewContent.value = ''
    textContent.value = ''
    error.value = ''
    
    console.log('🔄 路由参数变化，重新初始化...')
    // 立即和延迟初始化
    initializePreview()
    
    // 延迟初始化确保路由参数完全设置
    setTimeout(() => {
      initializePreview()
    }, 100)
    
    // 再次延迟初始化
    setTimeout(() => {
      initializePreview()
    }, 300)
  }
)

// 监听路由准备状态变化
watch(
  () => isRouteReady.value,
  (ready) => {
    console.log('🔍 路由准备状态变化:', ready)
    if (ready && !isInitialized.value) {
      initializePreview()
    }
  }
)

// 组件挂载时初始化
onMounted(() => {
  console.log('🎬 Preview组件已挂载，路由参数:', route.params.id)
  console.log('🎬 组件当前状态:', {
    routeId: route.params.id,
    attachmentId: attachmentId.value,
    isRouteReady: isRouteReady.value
  })
  
  // 立即尝试初始化一次
  initializePreview()
  
  // 延迟再次尝试初始化
  setTimeout(() => {
    console.log('⏰ 延迟初始化检查:', {
      routeId: route.params.id,
      attachmentId: attachmentId.value,
      isRouteReady: isRouteReady.value
    })
    initializePreview()
  }, 200)
  
  // 3秒后再次尝试
  setTimeout(() => {
    console.log('🕐 3秒后检查:', {
      routeId: route.params.id,
      attachmentId: attachmentId.value,
      isRouteReady: isRouteReady.value
    })
    if (!isInitialized.value) {
      console.log('⚠️ 3秒后仍未初始化，尝试刷新页面')
      window.location.reload()
    }
  }, 3000)
  
  // 5秒后如果仍未初始化，强制刷新页面
  setTimeout(() => {
    console.log('🕐 5秒后最终检查:', {
      routeId: route.params.id,
      attachmentId: attachmentId.value,
      isRouteReady: isRouteReady.value,
      isInitialized: isInitialized.value
    })
    if (!isInitialized.value) {
      console.log('⚠️ 5秒后仍未初始化，强制刷新页面')
      window.location.reload()
    }
  }, 5000)
})

const loadPreview = async () => {
  if (!attachmentId.value) {
    console.warn('⚠️ 附件ID不存在:', attachmentId.value)
    return
  }

  loading.value = true
  error.value = ''
  previewContent.value = ''
  textContent.value = ''

  try {
    console.log('📦 开始加载附件预览:', attachmentId.value)
    
    // 获取文件信息
    const fileResponse = await getDailyReportAttachment(parseInt(attachmentId.value))
    console.log('📄 文件信息响应:', fileResponse)
    fileInfo.value = fileResponse

    // 获取预览内容
    if (isImage.value || isPDF.value || isText.value) {
      console.log('🖼️ 开始获取预览内容，文件类型:', fileInfo.value?.file_type)
      const previewResponse = await previewDailyReportAttachment(parseInt(attachmentId.value))
      
      if (isImage.value || isPDF.value) {
        previewContent.value = previewResponse
        console.log('✅ 预览内容已设置:', previewContent.value ? '有内容' : '无内容')
      } else if (isText.value) {
        // 对于文本文件，需要解码base64内容
        const base64Content = previewResponse.split(',')[1] // 移除data:text/plain;base64,前缀
        textContent.value = atob(base64Content)
        console.log('📝 文本内容已解码')
      }
    } else {
      console.log('❌ 不支持的预览类型:', fileInfo.value?.file_type)
    }
    
    console.log('🎉 预览加载完成')
  } catch (err: any) {
    console.error('❌ 预览加载失败:', err)
    error.value = err.response?.data?.detail || err.message || '加载预览内容失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化日期
const formatDate = (dateString: string): string => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 返回上一页
const handleGoBack = () => {
  router.back()
}

// 下载文件
const handleDownload = async () => {
  if (!fileInfo.value) return
  
  downloading.value = true
  try {
    const response = await fetch(`/api/v1/daily-reports/attachments/${attachmentId.value}/download`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = fileInfo.value.file_name
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      ElMessage.success('文件下载成功')
    } else {
      throw new Error('下载失败')
    }
  } catch (error: any) {
    console.error('下载失败:', error)
    ElMessage.error('文件下载失败')
  } finally {
    downloading.value = false
  }
}

// 图片加载成功
const onImageLoad = () => {
  console.log('✅ 图片加载成功')
}

// 图片加载失败
const onImageError = () => {
  console.error('❌ 图片加载失败')
  error.value = '图片加载失败'
  ElMessage.error('图片加载失败')
}
</script>

<style scoped>
.preview-page {
  min-height: 100vh;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
}

.preview-header {
  background: white;
  border-bottom: 1px solid #e8e8e8;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.header-left, .header-center, .header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.preview-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
  gap: 16px;
}

.error-container h3 {
  color: #333;
  margin: 0;
}

.preview-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.image-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background: #fafafa;
}

.preview-image {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.pdf-preview {
  width: 100%;
  height: 70vh;
  border: none;
}

.pdf-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.text-preview {
  padding: 24px;
  background: white;
}

.text-content {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 16px;
  overflow-x: auto;
  max-height: 70vh;
  overflow-y: auto;
}

.text-content pre {
  margin: 0;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.unsupported-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  text-align: center;
  gap: 16px;
  background: white;
}

.unsupported-preview h3 {
  color: #666;
  margin: 0;
}

.file-info-panel {
  background: white;
  margin: 24px;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.file-info-panel h3 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.label {
  font-weight: 600;
  color: #666;
  min-width: 80px;
  margin-right: 12px;
}

.value {
  color: #333;
  flex: 1;
}

/* 路由加载状态 */
.route-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 40px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .preview-header {
    padding: 12px 16px;
  }
  
  .header-center .page-title {
    font-size: 16px;
  }
  
  .preview-content {
    padding: 16px;
  }
  
  .file-info-panel {
    margin: 16px;
    padding: 16px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .route-loading {
    padding: 20px;
  }
}
</style>