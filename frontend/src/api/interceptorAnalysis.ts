// 分析HTTP拦截器是否干扰了编辑页面的token发送
export const interceptorAnalysis = async () => {
  console.log('=== 分析HTTP拦截器是否干扰 ===')
  
  // 1. 记录开始时间
  const startTime = new Date().toISOString()
  console.log('测试开始时间:', startTime)
  
  // 2. 检查当前token状态
  const token = localStorage.getItem('token')
  console.log('当前token存在:', !!token)
  if (token) {
    console.log('Token前30字符:', token.substring(0, 30) + '...')
  }
  
  // 3. 测试编辑页面的具体API调用
  console.log('\n3. 测试编辑页面的具体API调用...')
  
  try {
    // 直接调用编辑页面使用的API
    const reportId = 12  // 使用实际的日报ID
    
    console.log('调用API:', `v1/daily-report/legacy/my-reports/${reportId}/`)
    
    const response = await fetch(`v1/daily-report/legacy/my-reports/${reportId}/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    })
    
    console.log('API响应状态:', response.status)
    console.log('API响应头:', Object.fromEntries(response.headers.entries()))
    
    if (response.ok) {
      const data = await response.json()
      console.log('✅ API调用成功:', data.id, data.report_date)
    } else {
      const errorText = await response.text()
      console.log('❌ API调用失败:', response.status, errorText)
      
      // 尝试解析错误信息
      try {
        const errorJson = JSON.parse(errorText)
        console.log('错误JSON解析:', errorJson)
      } catch (e) {
        console.log('错误文本（非JSON）:', errorText)
      }
    }
    
  } catch (error) {
    console.log('❌ API调用异常:', error)
  }
  
  // 4. 对比不同的请求方式
  console.log('\n4. 对比不同的请求方式...')
  
  // 4.1 使用axios调用
  console.log('4.1 使用axios调用...')
  try {
    const { getDailyReport } = await import('./dailyReport')
    console.log('开始axios调用...')
    const result = await getDailyReport(12)
    console.log('✅ axios调用成功:', result.id)
  } catch (error: any) {
    console.log('❌ axios调用失败:', error.response?.status, error.message)
    
    // 详细分析axios错误
    console.log('axios错误详情:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      method: error.config?.method,
      headers: error.config?.headers,
      data: error.response?.data
    })
  }
  
  // 4.2 使用代理转发测试
  console.log('\n4.2 使用代理转发测试...')
  try {
    // 测试代理是否正常工作
    const proxyResponse = await fetch('/project/api/v1/daily-report/legacy/my-reports', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log('代理测试状态:', proxyResponse.status)
    
    if (proxyResponse.ok) {
      const proxyData = await proxyResponse.json()
      console.log('✅ 代理测试成功，列表数量:', proxyData.items?.length || 0)
    } else {
      const proxyError = await proxyResponse.text()
      console.log('❌ 代理测试失败:', proxyResponse.status, proxyError)
    }
    
  } catch (error) {
    console.log('❌ 代理测试异常:', error)
  }
  
  // 5. 分析可能的问题源
  console.log('\n5. 分析可能的问题源...')
  console.log('问题可能原因:')
  console.log('A. HTTP拦截器干扰 - 请求头被修改')
  console.log('B. 代理配置问题 - 转发失败')
  console.log('C. 请求时机问题 - 页面跳转时token丢失')
  console.log('D. CORS问题 - 跨域限制')
  
  // 6. 建议解决方案
  console.log('\n6. 建议解决方案:')
  console.log('如果fetch成功但axios失败: 禁用HTTP拦截器')
  console.log('如果fetch也失败: 检查代理配置')
  console.log('如果都成功: 检查请求时机')
  
  console.log('\n=== 拦截器分析完成 ===')
}

// 导出分析工具
if (typeof window !== 'undefined') {
  (window as any).interceptorAnalysis = interceptorAnalysis
}