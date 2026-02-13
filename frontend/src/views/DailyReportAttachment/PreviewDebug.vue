<template>
  <div>
    <h1>🎉 Debug组件挂载成功！</h1>
    <p>路由ID: {{ $route.params.id }}</p>
    <p>当前时间: {{ currentTime }}</p>
    <p>组件状态: 正常挂载</p>
    <button @click="goBack">返回上一页</button>
  </div>
</template>

<script>
export default {
  name: 'PreviewDebug',
  data() {
    return {
      currentTime: ''
    }
  },
  mounted() {
    this.currentTime = new Date().toLocaleString()
    
    console.log('🎬 Debug Preview组件已挂载!')
    console.log('📍 路由参数:', this.$route.params.id)
    console.log('📅 挂载时间:', this.currentTime)
    
    // 显示消息
    alert('Debug预览页面加载成功!')
  },
  methods: {
    goBack() {
      this.$router.back()
    }
  }
}
</script>

<style>
/* 移除所有样式，确保内容可见 */
</style>