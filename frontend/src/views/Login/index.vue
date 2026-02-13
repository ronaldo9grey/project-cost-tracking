<template>
  <div class="login-container">
    <!-- 书本打开效果 - 左右两个区域 -->
    <div class="book-layout">
      <!-- 左侧品牌展示区域 -->
      <div class="brand-panel">
        <div class="brand-card">
          <div class="brand-content">
            <div class="logo-section">
              <div class="logo-container">
                <el-icon class="main-logo" :size="48" color="#3b82f6">
                  <Box />
                </el-icon>
              </div>
              <h1 class="brand-title">企业项目管理系统</h1>
            </div>
            
            <div class="features-grid">
              <div class="feature-item">
                <el-icon class="feature-icon" :size="18" color="#4ade80">
                  <TrendCharts />
                </el-icon>
                <span class="feature-text">智能分析</span>
              </div>
              <div class="feature-item">
                <el-icon class="feature-icon" :size="18" color="#3b82f6">
                  <Connection />
                </el-icon>
                <span class="feature-text">协同工作</span>
              </div>
              <div class="feature-item">
                <el-icon class="feature-icon" :size="18" color="#8b5cf6">
                  <ShieldIcon />
                </el-icon>
                <span class="feature-text">安全管理</span>
              </div>
              <div class="feature-item">
                <el-icon class="feature-icon" :size="18" color="#f59e0b">
                  <CpuIcon />
                </el-icon>
                <span class="feature-text">AI助手</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧登录表单区域 -->
      <div class="login-panel">
        <div class="login-card">
          <div class="login-header">
            <h2 class="login-title">欢迎回来</h2>
            <p class="login-subtitle">请登录您的账户</p>
          </div>
          
          <el-form ref="loginFormRef" :model="loginForm" :rules="rules" label-width="0" autocomplete="off">
            <el-form-item prop="username">
              <el-input
                ref="usernameInputRef"
                v-model="loginForm.username"
                placeholder="用户名"
                :prefix-icon="User"
                size="large"
                @keyup.enter="focusToPassword"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                ref="passwordInputRef"
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                :prefix-icon="Lock"
                size="large"
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="login-btn"
                :loading="loading"
                @click="handleLogin"
              >
                {{ loading ? '登录中...' : '登 录' }}
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Monitor, Box, TrendCharts, Connection, Lock as ShieldIcon, Monitor as CpuIcon } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { login, setToken, removeToken, getToken } from '../../api/unifiedApi'
import { getUserInfo } from '../../api/Auth'

const router = useRouter()
const route = useRoute()

const loginFormRef = ref<FormInstance>()
const usernameInputRef = ref()
const passwordInputRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度在2-50个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 4, max: 100, message: '密码长度至少4个字符', trigger: 'blur' }
  ]
}

onMounted(() => {
  if (usernameInputRef.value) {
    usernameInputRef.value.focus()
  }
})

// 用户名输入框按回车聚焦到密码框
const focusToPassword = () => {
  if (passwordInputRef.value) {
    passwordInputRef.value.focus()
  }
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  // 首先检查表单是否为空
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  // 手动验证表单字段
  if (!loginForm.username.trim()) {
    ElMessage.warning('请输入用户名')
    return
  }
  
  if (!loginForm.password.trim()) {
    ElMessage.warning('请输入密码')
    return
  }

  await loginFormRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.error('请检查输入的用户名和密码')
      return
    }

    loading.value = true
    try {
      // 彻底清理所有认证相关的缓存数据
      localStorage.removeItem('token')
      localStorage.removeItem('currentUser')
      localStorage.removeItem('userInfo')
      localStorage.removeItem('cachedUserData')
      console.log('清理所有认证相关缓存，准备重新登录')
      
      const response = await login({
        username: loginForm.username,
        password: loginForm.password
      })

      console.log('登录响应数据:', response)
      
      // 检查响应格式并获取token
      let token
      if (response && response.code === 200 && response.data && response.data.access_token) {
        token = response.data.access_token
        console.log('✅ 获取到token:', token.substring(0, 20) + '...')
        setToken(token)
      } else {
        console.error('❌ 登录响应格式错误:', response)
        throw new Error('登录失败：服务器响应格式错误')
      }
      
      // 登录成功后，获取完整的用户信息（从personnel表）
      console.log('开始获取完整用户信息...')
      try {
        // 查询personnel表获取完整信息
        const queryUrl = `/api/v1/resource/personnel?employee_id=${loginForm.username}`
        console.log('🔍 查询URL:', queryUrl)
        
        const personnelResponse = await fetch(queryUrl, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        
        console.log('📊 API响应状态:', personnelResponse.status, personnelResponse.statusText)
        
        let userInfo = {
          id: "1", // 使用固定ID
          employee_id: loginForm.username,
          employee_name: loginForm.username,
          name: loginForm.username,
          username: loginForm.username,
          department: '',
          position: '',
          phone: '',
          email: '',
          role_id: 1
        }
        
        if (personnelResponse.ok) {
          const personnelData = await personnelResponse.json()
          console.log('📋 API返回数据:', personnelData)
          console.log('📋 原始数据字段:', Object.keys(personnelData))
          console.log('📋 data字段存在:', !!personnelData.data)
          
          if (personnelData.data && personnelData.data.length > 0) {
            const personnel = personnelData.data[0]
            console.log('👤 找到人员数据:', personnel)
            console.log('👤 人员数据字段:', Object.keys(personnel))
            
            userInfo = {
              id: personnel.id || "1",
              employee_id: personnel.employee_id,
              employee_name: personnel.name,
              name: personnel.name,
              username: personnel.employee_id,
              department: personnel.department || '',
              position: personnel.position || '',
              phone: personnel.phone || '',
              email: personnel.email || '',
              role_id: 1
            }
            console.log('✅ 获取到完整用户信息:', userInfo)
          } else {
            console.log('⚠️ API返回数据但没有匹配记录')
            console.log('⚠️ 尝试模糊搜索...')
            
            // 尝试模糊搜索
            const fuzzyResponse = await fetch(`/api/v1/resource/personnel?name=${loginForm.username}`, {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              }
            })
            
            if (fuzzyResponse.ok) {
              const fuzzyData = await fuzzyResponse.json()
              console.log('🔍 模糊搜索结果:', fuzzyData)
              
              if (fuzzyData.data && fuzzyData.data.length > 0) {
                const personnel = fuzzyData.data[0]
                userInfo = {
                  id: personnel.id || "1",
                  employee_id: personnel.employee_id,
                  employee_name: personnel.name,
                  name: personnel.name,
                  username: personnel.employee_id,
                  department: personnel.department || '',
                  position: personnel.position || '',
                  phone: personnel.phone || '',
                  email: personnel.email || '',
                  role_id: 1
                }
                console.log('✅ 模糊搜索获取到完整用户信息:', userInfo)
              }
            }
          }
        } else {
          console.log('❌ API调用失败:', personnelResponse.status, personnelResponse.statusText)
        }
        
        // 缓存完整用户信息
        localStorage.setItem('currentUser', JSON.stringify(userInfo))
        console.log('✅ 完整用户信息已缓存:', userInfo)
        
        // 同时广播用户信息更新事件
        window.dispatchEvent(new CustomEvent('userInfoUpdated', { 
          detail: userInfo 
        }))
        
      } catch (personnelError) {
        console.error('获取用户信息出错:', personnelError)
        // 即使获取personnel信息失败，也保存基本信息
        const basicUserInfo = {
          id: "1",
          employee_id: loginForm.username,
          employee_name: loginForm.username,
          name: loginForm.username,
          username: loginForm.username,
          department: '',
          position: '',
          phone: '',
          email: '',
          role_id: 1
        }
        localStorage.setItem('currentUser', JSON.stringify(basicUserInfo))
      }
      
      // 添加token调试信息
      console.log('Token保存完成:', {
        token: token.substring(0, 20) + '...',
        timestamp: new Date().toISOString()
      })
      console.log('登录成功，用户信息已缓存')

      ElMessage.success('登录成功')

      // 立即导航，App.vue会自动加载用户信息
      const redirect = route.query.redirect as string
      router.push(redirect || '/dashboard')
    } catch (error: any) {
      console.error('登录失败:', error)
      // 清理所有认证相关数据
      removeToken()
      localStorage.removeItem('currentUser')
      localStorage.removeItem('userInfo')
      localStorage.removeItem('cachedUserData')
      
      // 优化错误提示
      let errorMessage = '登录失败，请稍后重试'
      
      if (error?.response?.status === 401) {
        errorMessage = '用户名或密码错误，请检查后重试'
      } else if (error?.response?.status === 403) {
        errorMessage = '账户被禁用或权限不足，请联系管理员'
      } else if (error?.response?.status === 422) {
        errorMessage = '请检查输入的用户名和密码格式'
      } else if (error?.response?.status === 429) {
        errorMessage = '登录尝试次数过多，请稍后再试'
      } else if (error?.response?.status >= 500) {
        errorMessage = '服务器错误，请稍后重试'
      } else if (error?.message) {
        // 如果是网络错误或连接问题
        if (error.message.includes('Network') || error.message.includes('network') || error.message.includes('Network Error')) {
          errorMessage = '网络连接失败，请检查网络设置'
        } else if (error.message.includes('timeout') || error.message.includes('Timeout')) {
          errorMessage = '请求超时，请检查网络连接'
        } else if (error.message.includes('Failed to fetch') || error.message.includes('fetch')) {
          errorMessage = '无法连接到服务器，请稍后重试'
        } else {
          errorMessage = error.message
        }
      }
      
      ElMessage.error(errorMessage)
      
      // 登录失败时触发shake动画
      const loginCard = document.querySelector('.login-card')
      if (loginCard) {
        loginCard.classList.add('shake')
        setTimeout(() => {
          loginCard.classList.remove('shake')
        }, 500)
      }
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  position: relative;
  overflow: hidden;
  padding-right: 10vw;
  background: 
    linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)),
    url('/login-bg.jpg?') center/cover no-repeat;
}

/* 书本打开效果布局 */

.book-layout {
  display: flex;
  gap: 0;
  max-width: 900px;
  width: 100%;
  height: 550px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.15);
}

/* 左侧品牌展示区域 */
.brand-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
  background: 
    linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%),
    url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='m36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  color: white;
  position: relative;
  overflow: hidden;
}

.brand-card {
  width: 100%;
  height: 100%;
  max-width: 650px;
  padding: 60px 50px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 0;
  border: none;
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* 已删除书本打开效果中线 */

.brand-content {
  position: relative;
  z-index: 1;
  text-align: center;
  color: #1e293b;
}

.logo-section {
  margin-bottom: 32px;
}

.logo-container {
  position: relative;
  display: inline-block;
  margin-bottom: 16px;
}

.main-logo {
  position: relative;
  z-index: 2;
  filter: drop-shadow(0 4px 12px rgba(59, 130, 246, 0.3));
}

.brand-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 24px 0;
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.features-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 32px;
  max-width: 480px;
  margin-left: auto;
  margin-right: auto;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.feature-icon {
  flex-shrink: 0;
  font-size: 16px;
  color: #3b82f6;
}

.feature-text {
  font-size: 12px;
  font-weight: 500;
  color: #1e293b;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.brand-footer {
  padding-top: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.2);
}

.copyright {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.6);
  margin: 0;
}

/* 右侧登录表单区域 */
.login-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: 
    linear-gradient(135deg, rgba(52, 211, 153, 0.95) 0%, rgba(16, 185, 129, 0.95) 100%),
    url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='m36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  color: white;
  position: relative;
  overflow: hidden;
}

/* 移除重复的背景动画 */

.login-card {
  width: 100%;
  height: 100%;
  max-width: 650px;
  padding: 60px 50px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 0;
  border: none;
  position: relative;
  z-index: 1;
  color: #333;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
}

.logo {
  margin-bottom: 20px;
  position: relative;
}

.login-header h1 {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 12px 0;
  text-shadow: 0 2px 10px rgba(102, 126, 234, 0.2);
}

.subtitle {
  font-size: 15px;
  color: #606266;
  margin: 0;
  font-weight: 400;
}

.login-form {
  margin-bottom: 24px;
}

.login-btn {
  width: 100%;
  font-size: 16px;
  font-weight: 600;
  height: 50px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.login-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.login-btn:disabled {
  transform: none;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
}

.login-footer {
  text-align: center;
  margin-top: 24px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-title {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.login-subtitle {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
  font-weight: 400;
}

/* 登录按钮样式 */
.login-btn {
  width: 100%;
  font-size: 16px;
  font-weight: 600;
  height: 52px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.login-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.login-btn:disabled {
  transform: none;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
}

/* 登录失败时的动画效果 */
.login-card.shake {
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  10%, 30%, 50%, 70%, 90% {
    transform: translateX(-5px);
  }
  20%, 40%, 60%, 80% {
    transform: translateX(5px);
  }
}

/* 品牌区域动画 */
@keyframes brandFloat {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes logoGlow {
  0%, 100% {
    opacity: 0.3;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 0.6;
    transform: translate(-50%, -50%) scale(1.1);
  }
}

@keyframes loginFloat {
  0% {
    background-position: 0 0, 0 0;
  }
  100% {
    background-position: 80px 80px, -80px -80px;
  }
}

/* 动画效果 */

/* 响应式设计 */
@media (max-width: 1200px) {
  .brand-panel {
    flex: 1;
    padding: 40px 30px;
  }
  
  .login-panel {
    flex: 1;
    padding: 40px 30px;
  }
  
  .brand-title {
    font-size: 24px;
  }
  
  .vision-title {
    font-size: 18px;
  }
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }
  
  .brand-panel {
    flex: none;
    height: 300px;
    padding: 30px 40px;
    text-align: center;
  }
  
  .logo-section {
    margin-bottom: 30px;
  }
  
  .brand-title {
    font-size: 28px;
  }
  
  .vision-section {
    margin-bottom: 40px;
  }
  
  .vision-title {
    font-size: 20px;
  }
  
  .features-grid {
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 30px;
  }
  
  .feature-item {
    padding: 12px;
    flex-direction: column;
    text-align: center;
    gap: 8px;
  }
  
  .brand-footer {
    display: none;
  }
  
  .login-panel {
    flex: none;
    padding: 40px 30px;
  }
  
  .login-card {
    max-width: 100%;
    padding: 32px;
  }
  
  .login-title {
    font-size: 24px;
  }
}

@media (max-width: 480px) {
  .brand-panel {
    padding: 20px;
    height: 250px;
  }
  
  .brand-title {
    font-size: 24px;
  }
  
  .vision-title {
    font-size: 18px;
  }
  
  .vision-description {
    font-size: 14px;
  }
  
  .login-panel {
    padding: 30px 20px;
  }
  
  .login-card {
    padding: 24px;
  }
  
  .login-title {
    font-size: 20px;
  }
  
  .login-btn {
    height: 48px;
    font-size: 15px;
  }
}

/* 输入框样式增强 */
:deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(5px);
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  transform: translateY(-1px);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.25);
  border-color: #667eea;
}

:deep(.el-input__inner) {
  font-size: 15px;
  color: #303133;
}

:deep(.el-input__prefix-inner) {
  color: #909399;
}

/* 表单项间距优化 */
:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}
</style>