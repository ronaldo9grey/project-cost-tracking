// 简单的认证流程测试工具
// 可以直接在组件中调用来测试认证流程

import axios from 'axios'
import { ElMessage } from 'element-plus'

export const testSimpleAuth = async () => {
  console.log('=== 开始简单认证测试 ===')
  
  try {
    // 1. 清理所有存储
    localStorage.removeItem('token')
    localStorage.removeItem('currentUser')
    console.log('1. 清理存储完成')
    
    // 2. 直接使用axios进行登录
    const formData = new URLSearchParams()
    formData.append('username', 'admin')
    formData.append('password', '123456')
    
    console.log('2. 发送登录请求...')
    
    const loginResponse = await axios.post('v1/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    
    console.log('3. 登录响应:', loginResponse.data)
    
    if (loginResponse.data?.code === 200 && loginResponse.data?.data?.access_token) {
      const token = loginResponse.data.data.access_token
      
      // 3. 手动保存token
      localStorage.setItem('token', token)
      console.log('4. Token保存:', token.substring(0, 20) + '...')
      
      // 4. 测试发送token的请求
      console.log('5. 测试发送token请求...')
      
      const testResponse = await axios.get('v1/daily-report/legacy/my-reports', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      console.log('6. 测试响应:', testResponse.data)
      
      if (testResponse.data?.items) {
        console.log('✅ 认证流程测试成功！找到', testResponse.data.items.length, '条日报')
        return { success: true, data: testResponse.data }
      } else {
        console.log('❌ 测试响应格式异常:', testResponse.data)
        return { success: false, error: '响应格式异常' }
      }
      
    } else {
      console.log('❌ 登录响应格式错误:', loginResponse.data)
      return { success: false, error: '登录响应格式错误' }
    }
    
  } catch (error: any) {
    console.error('❌ 测试过程出错:', error)
    console.error('错误详情:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url
    })
    return { success: false, error: error.message }
  }
}

// 测试函数，可以直接在控制台调用
if (typeof window !== 'undefined') {
  (window as any).testSimpleAuth = testSimpleAuth
}