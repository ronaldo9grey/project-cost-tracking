<template>
  <div class="preview-page">
    <div style="padding: 20px; background: #f0f9ff; border: 1px solid #0ea5e9; border-radius: 8px; margin: 20px;">
      <h2 style="color: #0369a1;">📎 附件预览页面</h2>
      <p>附件ID: {{ route.params.id }}</p>
      <p>当前时间: {{ currentTime }}</p>
      <p>组件状态: 正常挂载</p>
    </div>

    <div style="padding: 20px;">
      <h3>基本信息</h3>
      <p>这是一个简化的预览页面，用于测试组件挂载和路由参数获取。</p>
      
      <el-button type="primary" @click="testLoad" style="margin-top: 20px;">
        测试加载功能
      </el-button>
      
      <div v-if="testResult" style="margin-top: 20px; padding: 10px; background: #f0f9ff; border-radius: 4px;">
        <p>测试结果: {{ testResult }}</p>
      </div>
      
      <el-button type="text" @click="goBack" style="margin-top: 20px; margin-left: 10px;">
        返回上一页
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

// 路由
const route = useRoute()
const router = useRouter()

// 状态
const currentTime = ref('')
const testResult = ref('')

// 组件挂载
onMounted(() => {
  console.log('✅ 简化版Preview组件挂载成功!')
  console.log('📍 路由参数:', route.params.id)
  
  // 更新时间
  currentTime.value = new Date().toLocaleTimeString()
  
  // 显示消息
  ElMessage.success('预览页面加载成功!')
})

// 测试函数
const testLoad = () => {
  testResult.value = `附件ID ${route.params.id} 加载测试成功！时间: ${new Date().toLocaleTimeString()}`
  ElMessage.info('测试加载完成')
}

// 返回函数
const goBack = () => {
  router.back()
}
</script>

<style scoped>
.preview-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px;
}
</style>