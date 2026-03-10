<template>
  <div class="app-container">
    <el-container v-if="isLoginPage" class="login-layout">
      <router-view />
    </el-container>
    <el-container v-else class="main-container">
      <el-aside width="200px" class="sidebar">
        <div class="logo">
          <h2>项目成本跟踪系统</h2>
        </div>
        <el-menu 
          :default-active="activeMenu" 
          class="el-menu-vertical-demo" 
          router
          @select="handleMenuSelect"
          background-color="#001529"
          text-color="rgba(255,255,255,0.65)"
          active-text-color="#1890ff"
        >
          <!-- 日报系统 -->
          <el-menu-item index="/daily-report">
            <el-icon><Document /></el-icon>
            <span>日报填报</span>
          </el-menu-item>
          <el-menu-item index="/daily-report-evaluation">
            <el-icon><UserFilled /></el-icon>
            <span>日报评价</span>
          </el-menu-item>
          <el-menu-item index="/daily-report/analysis">
            <el-icon><TrendCharts /></el-icon>
            <span>日报分析</span>
          </el-menu-item>
          <el-menu-item index="/monthly-goals">
            <el-icon><Aim /></el-icon>
            <span>目标管理</span>
          </el-menu-item>
          
          <!-- 项目系统 -->
          <el-menu-item index="/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <span>项目看板</span>
          </el-menu-item>
          <el-menu-item index="/project-cards">
            <el-icon><CreditCard /></el-icon>
            <span>项目卡片</span>
          </el-menu-item>
          <el-menu-item index="/projects">
            <el-icon><DocumentChecked /></el-icon>
            <span>项目管理</span>
          </el-menu-item>
          <el-menu-item index="/project-tracking">
            <el-icon><Box /></el-icon>
            <span>项目跟踪</span>
          </el-menu-item>
          
          <!-- 分析系统 -->
          <el-menu-item index="/cost-analysis">
            <el-icon><Money /></el-icon>
            <span>成本分析</span>
          </el-menu-item>
          <el-menu-item index="/supplier-performance">
            <el-icon><Avatar /></el-icon>
            <span>履约分析</span>
          </el-menu-item>
          <el-menu-item index="/resource-management">
            <el-icon><Tools /></el-icon>
            <span>资源管理</span>
          </el-menu-item>
          <el-menu-item index="/standardization">
            <el-icon><User /></el-icon>
            <span>项目标准</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="header">
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-avatar :size="32" src="./gcs.png" />
                <span>{{ userInfo.name || userInfo.employee_id || userInfo.username || '用户' }}</span>
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item command="password">修改密码</el-dropdown-item>
                  <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>

    <el-dialog v-model="profileDialogVisible" title="个人中心" width="500px">
      <el-form :model="userInfo" label-width="100px">
        <el-form-item label="员工编号">
          <el-input :value="userInfo.employee_id" disabled />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input :value="userInfo.name" disabled />
        </el-form-item>
        <el-form-item label="部门">
          <el-input :value="userInfo.department || '-'" disabled />
        </el-form-item>
        <el-form-item label="职位">
          <el-input :value="userInfo.position || '-'" disabled />
        </el-form-item>
        <el-form-item label="电话">
          <el-input :value="userInfo.phone || '-'" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input :value="userInfo.email || '-'" disabled />
        </el-form-item>
      </el-form>
    </el-dialog>

    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="500px">
      <el-form 
        ref="passwordFormRef" 
        :model="passwordForm" 
        :rules="passwordRules" 
        label-width="120px"
      >
        <el-form-item label="旧密码" prop="oldPassword">
          <el-input 
            v-model="passwordForm.oldPassword" 
            type="password" 
            placeholder="请输入旧密码"
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input 
            v-model="passwordForm.newPassword" 
            type="password" 
            placeholder="请输入新密码"
          />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPassword">
          <el-input 
            v-model="passwordForm.confirmPassword" 
            type="password" 
            placeholder="请确认新密码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          :loading="passwordLoading" 
          @click="handleChangePassword"
        >
          确认修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  HomeFilled,
  Document,
  Money,
  Avatar,
  Box,
  ArrowDown,
  User,
  DocumentChecked,
  UserFilled,
  CreditCard,
  Tools,
  TrendCharts,
  Aim
} from '@element-plus/icons-vue'
import { getToken, removeToken } from './api/axios'
import { changePassword } from './api/Auth'
import { getUserInfo } from './api/Auth'

// 路由
const route = useRoute()
const router = useRouter()

// 组件错误处理
const onComponentError = (error: any) => {
  console.error('🔴 组件错误:', error)
  ElMessage.error(`组件渲染错误: ${error.message || error}`)
}

const onVnodeBeforeMount = () => {
  console.log('🔄 组件即将挂载')
}

const onVnodeMounted = () => {
  console.log('✅ 组件挂载完成')
}

const activeMenu = ref('')
const profileDialogVisible = ref(false)
const passwordDialogVisible = ref(false)
const passwordLoading = ref(false)
const passwordFormRef = ref<FormInstance>()

const userInfo = reactive({
  id: 0,
  username: '',
  employee_id: '',
  name: '',
  department: '',
  position: '',
  phone: '',
  email: '',
  role_id: 0 as number | null
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule: any, value: string, callback: Function) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules: FormRules = {
  oldPassword: [
    { required: true, message: '请输入旧密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const isLoginPage = computed(() => {
  return route.path === '/login' || route.path === '/'
})

// 在router创建后再设置activeMenu
activeMenu.value = route.path

// 页面刷新时清除缓存
window.addEventListener('beforeunload', () => {
  localStorage.removeItem('cachedUserData')
})

const handleMenuSelect = (key: string) => {
  activeMenu.value = key
}

const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      profileDialogVisible.value = true
      break
    case 'password':
      passwordDialogVisible.value = true
      break
    case 'logout':
      await handleLogout()
      break
  }
}

const handleLogout = async () => {
  try {
    // 清除token
    removeToken()
    
    // 清除localStorage中的用户信息
    localStorage.removeItem('currentUser')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('cachedUserData')
    
    // 重置用户信息状态
    Object.assign(userInfo, {
      id: 0,
      username: '',
      employee_id: '',
      name: '',
      department: '',
      position: '',
      phone: '',
      email: '',
      role_id: 0
    })
    
    ElMessage.success('已退出登录')
    
    // 跳转到登录页面
    router.push('/login')
  } catch (error) {
    console.error('退出登录失败:', error)
    ElMessage.error('退出登录失败')
  }
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    await passwordFormRef.value.validate()
    passwordLoading.value = true
    
    await changePassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })
    
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (error: any) {
    console.error('密码修改失败:', error)
    ElMessage.error(error.response?.data?.detail || '密码修改失败')
  } finally {
    passwordLoading.value = false
  }
}

// 获取Token
const getToken = () => {
  return localStorage.getItem('token')
}

// 检查Token是否有效
const checkToken = () => {
  const token = getToken()
  if (!token) return false
  
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const currentTime = Date.now() / 1000
    return payload.exp > currentTime
  } catch {
    return false
  }
}

// 为当前路由检查token
const checkTokenForCurrentRoute = () => {
  const currentPath = route.path
  
  // 跳过登录页面和其他公开页面
  const publicPaths = ['/login', '/', '/forgot-password']
  if (publicPaths.includes(currentPath)) {
    console.log('🔄 公开页面，跳过token检查')
    return
  }
  
  console.log('🔄 开始检查当前路由token:', currentPath)
  
  if (!checkToken()) {
    console.log('❌ Token无效或不存在，跳转到登录页')
    ElMessage.warning('登录已过期，请重新登录')
    router.push('/login')
    return
  }
  
  console.log('✅ Token有效，允许访问:', currentPath)
}

// 加载用户信息
const loadUserInfo = async (retryCount = 0) => {
  const maxRetries = 3
  
  try {
    console.log(`🔄 开始加载用户信息 (尝试 ${retryCount + 1}/${maxRetries + 1})`)
    
    const token = getToken()
    if (!token) {
      throw new Error('没有有效的token')
    }
    
    const response = await getUserInfo()
    let userData = response
    
    // 如果API返回的是包含data字段的响应
    if (response && typeof response === 'object' && 'data' in response && 'user' in response.data) {
      userData = response.data.user
    }
    // 直接是用户数据对象
    else if (response && typeof response === 'object' && response.data) {
      userData = response.data
    }
    // 直接是用户数据对象
    else {
      userData = response
    }
    
    console.log('处理后的用户数据:', userData)
    
    if (userData && typeof userData === 'object' && userData.id) {
      Object.assign(userInfo, {
        id: userData.id || 0,
        username: userData.username || '',
        employee_id: userData.employee_id || userData.username || '',
        name: userData.name || '',
        department: userData.department || '',
        position: userData.position || '',
        phone: userData.phone || '',
        email: userData.email || '',
        role_id: userData.role_id || 0
      })
      
      // 更新localStorage中的缓存
      localStorage.setItem('currentUser', JSON.stringify({
        id: userInfo.id,
        username: userInfo.username,
        employee_id: userInfo.employee_id,
        name: userInfo.name,
        department: userInfo.department,
        position: userInfo.position,
        phone: userInfo.phone,
        email: userInfo.email,
        role_id: userInfo.role_id
      }))
      
      console.log('✅ 用户信息加载完成 - API获取:', userInfo)
      console.log('最终用户信息状态:', userInfo)
      
      // 加载成功后，获取详细的人员信息
      await loadPersonnelDetail()
    } else {
      console.warn('⚠️ 用户数据格式不正确:', userData)
      throw new Error('用户数据格式不正确')
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
    
    // 如果是网络错误或重试次数未达上限，则重试
    if (retryCount < maxRetries) {
      console.log(`🔄 重试获取用户信息 (${retryCount + 1}/${maxRetries})`)
      setTimeout(() => {
        loadUserInfo(retryCount + 1)
      }, 1000 * (retryCount + 1))
    } else {
      console.error('❌ 用户信息加载失败，已达到最大重试次数')
      ElMessage.error('加载用户信息失败，请刷新页面重试')
      
      // 如果token有问题，跳转到登录页
      if (!checkToken()) {
        router.push('/login')
      }
    }
  }
}

// 加载详细的人员信息
const loadPersonnelDetail = async () => {
  try {
    // 调试信息
    console.log('开始加载人员详细信息...')
    console.log('使用的查询参数:', {
      name: userInfo.username,
      employee_id: userInfo.employee_id,
      username: userInfo.username
    })
    
    const response = await fetch(`/project/api/v1/resource/personnel?limit=1&name=${userInfo.username}`, {
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log('人员查询响应状态:', response.status)
    if (response.ok) {
      const data = await response.json()
      console.log('人员查询响应数据:', data)
      
      if (data.data && data.data.length > 0) {
        const personnel = data.data[0]
        Object.assign(userInfo, {
          employee_id: personnel.employee_id,
          name: personnel.name,
          department: personnel.department || '',
          position: personnel.position || '',
          phone: personnel.phone || '',
          email: personnel.email || ''
        })
        
        // 更新缓存
        localStorage.setItem('currentUser', JSON.stringify({
          id: userInfo.id,
          username: userInfo.username,
          employee_id: userInfo.employee_id,
          name: userInfo.name,
          department: userInfo.department,
          position: userInfo.position,
          phone: userInfo.phone,
          email: userInfo.email,
          role_id: userInfo.role_id
        }))
        
        console.log('✅ 人员详细信息加载完成:', userInfo)
      } else {
        console.log('⚠️ 未找到人员详细信息，使用基础信息')
      }
    } else {
      console.error('❌ 人员查询失败:', response.status, response.statusText)
    }
  } catch (error) {
    console.error('获取人员详情失败:', error)
  }
}

import { watch } from 'vue'

onMounted(() => {
  activeMenu.value = route.path
  
  // 页面加载时先从localStorage恢复用户信息
  const cachedUser = localStorage.getItem('currentUser')
  if (cachedUser) {
    try {
      const userData = JSON.parse(cachedUser)
      Object.assign(userInfo, userData)
      console.log('✅ 从缓存恢复用户信息:', userInfo)
    } catch (error) {
      console.warn('⚠️ 缓存用户信息解析失败:', error)
      localStorage.removeItem('currentUser')
    }
  }
  
  // 监听用户信息更新事件 - 所有页面都需要
  window.addEventListener('userInfoUpdated', (event: any) => {
    console.log('🎯 收到用户信息更新事件:', event.detail)
    if (event.detail) {
      Object.assign(userInfo, event.detail)
      console.log('✅ 用户信息立即更新:', userInfo)
    }
  })
  
  // 监听路由变化，根据当前页面决定是否检查token
  watch(() => route.path, (newPath, oldPath) => {
    console.log('📄 路由变化:', oldPath, '->', newPath)
    
    // 无论路由变化到哪里，都调用检查函数，函数内部会判断是否跳过
    console.log('🔄 路由变化后开始token检查')
    checkTokenForCurrentRoute()
  })
  
  // 立即检查一次当前路由
  console.log('🔄 组件挂载完成，检查当前路由')
  checkTokenForCurrentRoute()
  
  // 如果有token，则异步加载最新的用户信息
  const token = getToken()
  if (token) {
    console.log('🔄 页面加载完成，异步刷新用户信息')
    loadUserInfo().catch(error => {
      console.warn('⚠️ 用户信息刷新失败，使用缓存数据:', error)
    })
  }
  
  // 监听userInfo变化，自动更新缓存
  watch(userInfo, (newUserInfo) => {
    try {
      localStorage.setItem('currentUser', JSON.stringify(newUserInfo))
      console.log('🔄 用户信息变化，自动更新缓存:', newUserInfo)
    } catch (error) {
      console.warn('⚠️ 更新用户缓存失败:', error)
    }
  }, { deep: true })
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

#app {
  width: 100%;
  height: 100%;
}

.app-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.login-layout {
  height: 100%;
  width: 100%;
}

.main-container {
  height: 100%;
}

.sidebar {
  background: #001529;
  overflow: hidden;
}

/* 菜单样式 */
.el-menu-vertical-demo {
  border-right: none;
  background-color: transparent;
}

.el-menu-vertical-demo .el-menu-item {
  height: 48px;
  line-height: 48px;
  padding-left: 20px;
  margin: 4px 8px;
  border-radius: 6px;
  transition: all 0.3s;
}

.el-menu-vertical-demo .el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.el-menu-vertical-demo .el-menu-item.is-active {
  background-color: #1890ff;
  color: #fff;
}

.el-menu-vertical-demo .el-menu-item .el-icon {
  margin-right: 8px;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  margin-bottom: 16px;
}

.logo h2 {
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.header {
  background: white;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s;
  outline: none;
  border: none;
  background: none;
}

.user-info:hover {
  background-color: #f5f5f5;
  outline: none;
  border: none;
}

.user-info:focus {
  outline: none;
  border: none;
}

.user-info:focus-visible {
  outline: none;
  border: none;
}

/* 覆盖Element Plus dropdown默认样式 */
.el-dropdown .user-info {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}

.el-dropdown .user-info:hover {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}

/* 覆盖el-avatar默认hover效果 */
.user-info .el-avatar {
  border: none !important;
  outline: none !important;
  transition: all 0.2s;
}

.user-info .el-avatar:hover {
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}

.main-content {
  background: #f0f2f5;
  overflow: auto;
}

/* 路由切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>