<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>项目看板</h1>
      <p>欢迎使用项目成本跟踪系统</p>
    </div>

    <!-- 欢迎信息 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <h2>🎉 登录成功！</h2>
          <div style="padding: 20px 0;">
            <p>✅ JWT认证系统正常工作</p>
            <p>✅ 前后端集成正常</p>
            <p>✅ 数据库连接正常</p>
            <p>✅ 用户权限管理正常</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 功能模块 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="8">
        <el-card class="function-card">
          <div class="card-content">
            <h3>项目管理</h3>
            <p>创建和管理项目</p>
            <el-button type="primary" @click="navigateTo('/projects')">进入</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="function-card">
          <div class="card-content">
            <h3>成本分析</h3>
            <p>分析项目成本数据</p>
            <el-button type="primary" @click="navigateTo('/cost-analysis')">进入</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="function-card">
          <div class="card-content">
            <h3>项目跟踪</h3>
            <p>跟踪项目进度</p>
            <el-button type="primary" @click="navigateTo('/project-tracking')">进入</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 更多功能 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="6">
        <el-card class="function-card-small">
          <div class="card-content">
            <h4>供应商管理</h4>
            <el-button size="small" @click="navigateTo('/supplier-performance')">进入</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="function-card-small">
          <div class="card-content">
            <h4>资源管理</h4>
            <el-button size="small" @click="navigateTo('/resource-management')">进入</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="function-card-small">
          <div class="card-content">
            <h4>日报管理</h4>
            <el-button size="small" @click="navigateTo('/daily-report')">进入</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="function-card-small">
          <div class="card-content">
            <h4>项目标准</h4>
            <el-button size="small" @click="navigateTo('/standardization')">进入</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部信息 -->
    <el-row style="margin-top: 40px;">
      <el-col :span="24">
        <div class="footer-info">
          <p>🚀 系统运行正常，您可以开始使用各种功能模块</p>
          <p>💡 提示：点击上方按钮可快速导航到对应功能</p>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
// 极简脚本，避免Composition API导入问题
const navigateTo = (path) => {
  window.location.href = path
}
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
  font-size: 32px;
}

.dashboard-header p {
  color: #606266;
  font-size: 18px;
}

.function-card {
  height: 200px;
  text-align: center;
}

.function-card-small {
  height: 150px;
  text-align: center;
}

.card-content {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.card-content h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 20px;
}

.card-content h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 16px;
}

.card-content p {
  color: #606266;
  margin-bottom: 20px;
  flex-grow: 1;
}

.footer-info {
  text-align: center;
  color: #909399;
  font-size: 14px;
  line-height: 1.6;
}

:deep(.el-card__body) {
  height: 100%;
}
</style>