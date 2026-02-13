// 统一的API模块，解决导入冲突问题
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const service = axios.create({
  baseURL: '/',  // 基础路径，通过Vite代理
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// 请求拦截器 - 简化版本，避免干扰
service.interceptors.request.use(
  (config) => {
    // 对登录请求特殊处理，不添加token
    if (config.url?.includes('/auth/login')) {
      console.log('登录请求，不添加token:', config.method?.toUpperCase(), config.url)
    } else {
      // 简化的token添加逻辑
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
        console.log('添加Token:', config.method?.toUpperCase(), config.url)
      } else {
        console.log('未找到token:', config.method?.toUpperCase(), config.url)
      }
    }
    
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器 - 最小化处理，让数据自然传递
service.interceptors.response.use(
  (response) => {
    // 最小化处理，直接返回响应数据
    const resData = response.data
    
    // 对登录接口特殊处理 - 返回完整响应数据
    if (response.config.url?.includes('/auth/login')) {
      console.log('登录响应处理:', {
        code: resData.code,
        message: resData.message,
        hasToken: !!resData.data?.access_token,
        tokenLength: resData.data?.access_token?.length || 0
      })
      return resData  // 返回完整响应 {code, message, data}
    }
    
    // 对于其他API，直接返回数据，不做额外处理
    console.log('API响应:', response.config.method?.toUpperCase(), response.config.url, resData.code || '直接数据')
    return resData
  },
  (error) => {
    // 最小化错误处理，让错误自然传播
    console.error('API请求失败:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.message
    })
    
    // 让错误自然传播，不做特殊处理
    return Promise.reject(error)
  }
)

// Token管理函数
export const getToken = () => localStorage.getItem('token')
export const setToken = (token: string) => localStorage.setItem('token', token)
export const removeToken = () => localStorage.removeItem('token')

// 登录函数 - 真实JWT认证
export const login = (params: { username: string; password: string }) => {
  console.log('发送登录请求:', params.username)
  
  // 真实API调用 - 连接数据库进行用户验证
  const formData = new URLSearchParams()
  formData.append('username', params.username)
  formData.append('password', params.password)
  
  console.log('请求URL:', '/api/v1/auth/login')
  console.log('请求数据:', { username: params.username, password: '***' })
  console.log('Content-Type:', 'application/x-www-form-urlencoded')
  
  return service.post('/api/v1/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  }).then(response => {
    console.log('✅ 登录请求成功:', response.status, response.data)
    return response
  }).catch(error => {
    console.error('❌ 登录请求失败:', error.message, error.response?.data)
    throw error
  })
}

// 导出配置好的axios实例
export default service