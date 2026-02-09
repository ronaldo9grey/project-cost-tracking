// 深度对比前端和后端请求，找出认证失败的确切原因
export const frontendBackendDeepComparison = async () => {
  console.log('=== 深度对比前端和后端请求 ===')
  
  // 1. 获取当前token状态
  let token = localStorage.getItem('token')
  if (!token) {
    console.log('1. 没有找到token，重新登录...')
    
    // 清理并重新登录
    localStorage.clear()
    
    const formData = new URLSearchParams()
    formData.append('username', 'admin')
    formData.append('password', '123456')
    
    const loginResponse = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData
    })
    
    if (loginResponse.ok) {
      const loginData = await loginResponse.json()
      token = loginData.data?.access_token
      localStorage.setItem('token', token)
      console.log('重新登录成功，token:', token?.substring(0, 30) + '...')
    } else {
      console.log('重新登录失败')
      return
    }
  } else {
    console.log('1. 找到现有token:', token.substring(0, 30) + '...')
  }
  
  // 2. 使用后端成功的方式测试
  console.log('\n2. 使用后端成功的方式测试...')
  
  try {
    // 完全复制后端成功的请求方式
    const response = await fetch('/api/v1/daily-report/legacy/my-reports/12/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    })
    
    console.log('后端方式状态:', response.status)
    
    if (response.ok) {
      const data = await response.json()
      console.log('✅ 后端方式成功:', data.id, data.report_date)
    } else {
      const errorText = await response.text()
      console.log('❌ 后端方式失败:', response.status, errorText)
      
      // 详细分析请求头
      console.log('\n3. 分析请求头差异...')
      console.log('使用的请求头:', {
        'Authorization': `Bearer ${token.substring(0, 30)}...`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      })
      
      console.log('使用的URL:', '/api/v1/daily-report/legacy/my-reports/12/')
    }
  } catch (e) {
    console.log('❌ 后端方式异常:', e)
  }
  
  // 3. 测试axios请求
  console.log('\n4. 测试axios请求...')
  
  try {
    const { getDailyReport } = await import('./dailyReport')
    console.log('开始axios调用...')
    const axiosResult = await getDailyReport(12)
    console.log('✅ axios调用成功:', axiosResult.id)
  } catch (e: any) {
    console.log('❌ axios调用失败:', e.response?.status, e.message)
    
    console.log('axios错误详情:', {
      message: e.message,
      status: e.response?.status,
      url: e.config?.url,
      method: e.config?.method,
      headers: e.config?.headers,
      timestamp: new Date().toISOString()
    })
  }
  
  // 4. 检查HTTP拦截器是否干扰
  console.log('\n5. 检查HTTP拦截器...')
  
  try {
    // 直接使用原始axios实例
    const response = await fetch('/api/v1/daily-report/legacy/my-reports/12/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log('原始fetch状态:', response.status)
    
    if (response.ok) {
      const data = await response.json()
      console.log('✅ 原始fetch成功:', data.id)
    } else {
      const errorText = await response.text()
      console.log('❌ 原始fetch失败:', response.status, errorText)
    }
  } catch (e) {
    console.log('❌ 原始fetch异常:', e)
  }
  
  // 5. 建议解决方案
  console.log('\n6. 建议解决方案:')
  console.log('如果后端方式成功但axios失败，说明问题在HTTP拦截器')
  console.log('如果后端方式也失败，说明问题在代理配置')
  console.log('如果全部成功，说明问题在请求时机')
  
  console.log('\n=== 深度对比完成 ===')
}

// 导出对比工具
if (typeof window !== 'undefined') {
  (window as any).frontendBackendDeepComparison = frontendBackendDeepComparison
}