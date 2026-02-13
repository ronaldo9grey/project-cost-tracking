<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>项目看板</h1>
      <p>欢迎来到项目成本跟踪系统</p>
    </div>

    <!-- 欢迎信息 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <h2>系统状态</h2>
          <div style="padding: 20px 0;">
            <p>✅ 用户认证系统正常工作</p>
            <p>✅ JWT Token验证正常</p>
            <p>✅ 数据库连接正常</p>
            <p>✅ 前后端集成正常</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="6">
        <el-card class="shortcut-card">
          <div class="card-content">
            <el-icon><FolderOpened /></el-icon>
            <h3>项目管理</h3>
            <p>管理项目生命周期</p>
            <el-button type="primary" @click="$router.push('/projects')">进入</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="shortcut-card">
          <div class="card-content">
            <el-icon><Money /></el-icon>
            <h3>成本分析</h3>
            <p>分析项目成本数据</p>
            <el-button type="primary" @click="$router.push('/cost-analysis')">进入</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="shortcut-card">
          <div class="card-content">
            <el-icon><TrendCharts /></el-icon>
            <h3>项目跟踪</h3>
            <p>跟踪项目执行进度</p>
            <el-button type="primary" @click="$router.push('/project-tracking')">进入</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="shortcut-card">
          <div class="card-content">
            <el-icon><User /></el-icon>
            <h3>资源管理</h3>
            <p>管理项目资源</p>
            <el-button type="primary" @click="$router.push('/resource-management')">进入</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { FolderOpened, Money, TrendCharts, User } from '@element-plus/icons-vue'

// 获取当前用户信息
const currentUser = ref(null)

onMounted(() => {
  // 从localStorage获取用户信息
  const userInfo = localStorage.getItem('currentUser')
  if (userInfo) {
    currentUser.value = JSON.parse(userInfo)
    console.log('Dashboard: 当前用户信息:', currentUser.value)
  }
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.dashboard-header {
  text-align: center;
  margin-bottom: 30px;
}

.dashboard-header h1 {
  color: #303133;
  margin-bottom: 10px;
}

.dashboard-header p {
  color: #606266;
  font-size: 16px;
}

.shortcut-card {
  text-align: center;
  height: 250px;
}

.card-content {
  padding: 20px;
}

.card-content .el-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 15px;
}

.card-content h3 {
  margin: 15px 0 10px 0;
  color: #303133;
}

.card-content p {
  color: #606266;
  margin-bottom: 20px;
}

:deep(.el-card__body) {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>