// 对比前端和后端请求的差异，找出身份验证失败的根本原因
export const requestComparison = async () => {
  console.log('=== 对比前端和后端请求差异 ===')
  
  // 1. 清理localStorage，确保测试准确性
  console.log('1. 清理localStorage...')
  localStorage.removeItem('token')
  localStorage.removeItem('currentUser')
  
  // 2. 重新登录
  console.log('2. 重新登录...')
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
  
  console.log('登录响应状态:', loginResponse.status)
  
  if (loginResponse.ok) {
    const loginData = await loginResponse.json()
    console.log('登录成功:', loginData)
    
    if (loginData.code === 200 && loginData.data?.access_token) {
      const token = loginData.data.access_token
      console.log('新token:', token.substring(0, 30) + '...')
      
      // 保存token
      localStorage.setItem('token', token)
      
      // 3. 模拟后端成功的请求方式
      console.log('\n3. 使用后端成功的方式测试...')
      
      try {
        // 使用完全相同的请求方式
        const response = await fetch('/api/v1/daily-report/legacy/my-reports/12/', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        })
        
        console.log('API响应状态:', response.status)
        
        if (response.ok) {
          const data = await response.json()
          console.log('✅ API调用成功:', data.id, data.report_date)
        } else {
          const errorText = await response.text()
          console.log('❌ API调用失败:', response.status, errorText)
          
          // 4. 详细分析失败原因
          console.log('\n4. 详细分析失败原因...')
          console.log('请求头信息:', {
            'Authorization': `Bearer ${token.substring(0, 20)}...`,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          })
          
          console.log('请求URL:', '/api/v1/daily-report/legacy/my-reports/12/')
          console.log('请求方法:', 'GET')
          console.log('响应状态:', response.status)
          console.log('响应头:', Object.fromEntries(response.headers.entries()))
        }
      } catch (e) {
        console.log('❌ 请求异常:', e)
      }
      
      // 5. 对比axios和fetch的差异
      console.log('\n5. 对比axios和fetch的差异...')
      try {
        // 使用axios方式
        const { getDailyReport } = await import('./dailyReport')
        console.log('开始axios请求...')
        const axiosResult = await getDailyReport(12)
        console.log('✅ axios请求成功:', axiosResult.id)
      } catch (e: any) {
        console.log('❌ axios请求失败:', e.response?.status, e.message)
        
        console.log('axios错误详情:', {
          message: e.message,
          status: e.response?.status,
          url: e.config?.url,
          headers: e.config?.headers,
          method: e.config?.method
        })
      }
    }
  }
  
  console.log('\n=== 对比完成 ===')
}

// 导出对比工具
if (typeof window !== 'undefined') {
  (window as any).requestComparison = requestComparison
}