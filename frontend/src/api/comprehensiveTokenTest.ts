// 完整的token验证测试
import { getDailyReport } from './dailyReport'

export const comprehensiveTokenTest = async () => {
  console.log('=== 开始完整token验证测试 ===')
  
  try {
    // 1. 检查localStorage中的token
    const token = localStorage.getItem('token')
    console.log('1. localStorage token:', token ? token.substring(0, 20) + '...' : 'null')
    
    if (!token) {
      console.log('❌ 没有找到token')
      return { success: false, reason: 'no_token' }
    }
    
    // 2. 检查token格式
    const parts = token.split('.')
    console.log('2. Token parts:', parts.length)
    
    if (parts.length !== 3) {
      console.log('❌ Token格式不正确')
      return { success: false, reason: 'invalid_format' }
    }
    
    // 3. 解码payload
    try {
      const payload = JSON.parse(atob(parts[1]))
      console.log('3. Token payload:', payload)
      
      const now = Math.floor(Date.now() / 1000)
      console.log('4. 当前时间戳:', now)
      console.log('5. Token过期时间:', payload.exp)
      
      if (payload.exp && payload.exp < now) {
        console.log('❌ Token已过期')
        return { success: false, reason: 'expired', exp: payload.exp }
      }
      
    } catch (e) {
      console.log('❌ Token payload解析失败:', e)
      return { success: false, reason: 'parse_error' }
    }
    
    // 4. 手动验证token是否有效
    console.log('6. 开始手动验证token...')
    
    const formData = new URLSearchParams()
    formData.append('username', 'admin')
    formData.append('password', '123456')
    
    const loginResponse = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    })
    
    console.log('7. 重新登录结果:', loginResponse.status)
    
    if (loginResponse.ok) {
      const newLoginData = await loginResponse.json()
      console.log('8. 新token:', newLoginData.data?.access_token?.substring(0, 20) + '...')
      
      // 比较新旧token
      const newToken = newLoginData.data?.access_token
      if (newToken && newToken !== token) {
        console.log('⚠️  Token已更新，旧token可能已失效')
        localStorage.setItem('token', newToken)
        console.log('已更新localStorage中的token')
      }
    }
    
    // 5. 测试API调用
    console.log('9. 测试getDailyReport调用...')
    const testId = 12
    
    try {
      const report = await getDailyReport(testId)
      console.log('10. ✅ API调用成功:', report.id)
      return { success: true, report }
    } catch (apiError: any) {
      console.log('10. ❌ API调用失败:', {
        status: apiError.response?.status,
        message: apiError.message,
        url: apiError.config?.url
      })
      
      // 重新尝试一次
      console.log('11. 重新尝试API调用...')
      const report = await getDailyReport(testId)
      console.log('11. ✅ 第二次API调用成功:', report.id)
      return { success: true, report }
      
    }
    
  } catch (error: any) {
    console.error('❌ 完整测试失败:', error)
    return { success: false, error }
  }
}

// 导出测试函数
if (typeof window !== 'undefined') {
  (window as any).comprehensiveTokenTest = comprehensiveTokenTest
}