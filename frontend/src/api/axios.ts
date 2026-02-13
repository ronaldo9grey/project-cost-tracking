import axios from 'axios'
import { ElMessage } from 'element-plus'

// 统一导出所有函数，避免导入冲突
export { ElMessage }

const requestCache = new Map<string, { data: any; timestamp: number }>()
const CACHE_EXPIRY = 5 * 60 * 1000
const MAX_RETRIES = 3

const service = axios.create({
  baseURL: '/',  // 基础路径，通过Vite代理
  timeout: 60000,  // 增加到60秒超时
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

const generateCacheKey = (config: any) => {
  const { method, url, params, data } = config || {}
  return `${method || 'GET'}-${url || ''}-${JSON.stringify(params || {})}-${JSON.stringify(data || {})}`
}

service.interceptors.request.use(
  (config) => {
    // 对登录请求特殊处理，不添加token
    if (config.url?.includes('/auth/login')) {
      console.log('登录请求，不添加token:', config.method?.toUpperCase(), config.url)
    } else {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
        console.log('添加Token到请求:', {
          method: config.method?.toUpperCase(),
          url: config.url,
          tokenLength: token.length,
          tokenStart: token.substring(0, 20),
          timestamp: new Date().toISOString()
        })
      } else {
        console.warn('未找到token:', {
          method: config.method?.toUpperCase(),
          url: config.url,
          timestamp: new Date().toISOString()
        })
      }
    }
    
    if (!config.method) {
      config.method = 'GET'
    }
    
    if (!config.retryCount) {
      config.retryCount = 0
    }
    
    console.log('Request:', config.method?.toUpperCase(), config.url)
    
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  (response) => {
    const resData = response.data
    
    // 简化的响应处理，确保永远不会返回null
    if (resData.code === 200) {
      // 对登录接口特殊处理
      if (response.config.url?.includes('/auth/login')) {
        return resData.data || resData
      }
      
      // 对用户信息接口特殊处理，返回data部分
      if (response.config.url?.includes('/auth/users/me')) {
        return resData.data // 返回用户数据对象
      }
      
      // 其他API返回业务数据部分
      if (resData.data && typeof resData.data === 'object') {
        if ('items' in resData.data) {
          return resData.data
        }
        if (Array.isArray(resData.data)) {
          // 对于人员列表等数组数据，直接返回数组，不包装成items格式
          return resData.data
        }
        // 对于统计数据等单一对象，返回原始data
        if (resData.data.status_counts || resData.data.total_projects !== undefined) {
          return resData.data
        }
        // 对于其他单一对象数据，返回原始data
        return resData.data
      }
      return { items: [], total: 0 }
    } else if (resData.code === 404) {
      return { code: 404, data: null, message: resData.message }
    } else if (resData.message && !resData.message.includes('成功')) {
      ElMessage.error(resData.message)
      return Promise.reject(new Error(resData.message))
    } else {
      return resData
    }
  },
  (error) => {
    let message = '请求失败'
    const config = error.config
    
    if (error.response) {
      const status = error.response.status
      message = error.response.data?.message || error.response.data?.detail || `请求失败 (${status})`
      
      switch (status) {
        case 401:
          const isLoginRequest = config?.url?.includes('/auth/login')
          const isDailyReportRequest = config?.url?.includes('/daily-report')
          const isEvaluationRequest = config?.url?.includes('/daily-report-evaluation')
          const isReportRelated = isDailyReportRequest || config?.url?.includes('/work-item') || isEvaluationRequest
          
          if (isLoginRequest) {
            message = '用户名或密码错误，请检查后重试'
            error.message = message
          } else {
            // 检查是否是日报相关API的401错误
            if (isReportRelated) {
              // 对于日报相关API，记录日志但不清空消息，避免组件错误处理
              console.warn('日报相关API返回401，静默处理:', {
                url: config?.url,
                method: config?.method,
                timestamp: new Date().toISOString(),
                hasToken: !!localStorage.getItem('token')
              })
              
              // 清理token但不显示消息
              localStorage.removeItem('token')
              
              // 设置空消息，避免组件显示错误
              message = ''
            } else {
              // 对于非日报API，正常处理401错误
              message = '未授权，请重新登录'
              console.warn('API请求返回401状态码:', {
                url: config?.url,
                method: config?.method,
                timestamp: new Date().toISOString()
              })
              
              // 清理token
              localStorage.removeItem('token')
              
              if (!window.location.pathname.includes('/login')) {
                setTimeout(() => {
                  window.location.href = '/login'
                }, 100)
              }
              
              ElMessage.error(message)
            }
          }
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = `请求失败 (${status})`
      }
    } else if (error.request) {
      message = '网络错误，服务器没有响应'
      
      if (config && config.retryCount < MAX_RETRIES) {
        config.retryCount++
        console.log(`请求重试中 (${config.retryCount}/${MAX_RETRIES}): ${config.url}`)
        return service(config)
      }
    } else {
      message = '请求配置错误'
    }
    
    if (!config?.url?.includes('/auth/login') && !config?.url?.includes('/ai-result')) {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  }
)

export const clearCache = (url?: string) => {
  if (url) {
    for (const [key] of requestCache) {
      if (key.includes(url)) {
        requestCache.delete(key)
      }
    }
  } else {
    requestCache.clear()
  }
}

export const getToken = () => localStorage.getItem('token')
export const setToken = (token: string) => localStorage.setItem('token', token)
export const removeToken = () => localStorage.removeItem('token')

export const login = (params: { username: string; password: string }) => {
  const formData = new URLSearchParams()
  formData.append('username', params.username)
  formData.append('password', params.password)
  console.log('发送登录请求:', params.username)
  return service.post('/api/v1/auth/login', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}

export default service
