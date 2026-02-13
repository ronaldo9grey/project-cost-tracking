// 测试编辑页面的token状态，模拟完整的编辑页面加载流程
export const editPageTokenTest = async () => {
  console.log('=== 测试编辑页面token状态 ===')
  
  // 1. 检查当前token状态
  console.log('1. 检查当前token状态:')
  const token = localStorage.getItem('token')
  console.log('Token存在:', !!token)
  if (token) {
    console.log('Token前30字符:', token.substring(0, 30) + '...')
    
    // 解码JWT
    try {
      const parts = token.split('.')
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]))
        console.log('JWT payload:', payload)
        console.log('JWT sub字段:', payload.sub)
      }
    } catch (e) {
      console.log('JWT解码失败:', e)
    }
  }
  
  // 2. 模拟编辑页面的加载流程
  console.log('\n2. 模拟编辑页面的加载流程:')
  
  // 2.1 加载任务列表
  console.log('2.1 加载任务列表...')
  try {
    const tasksResponse = await fetch('/api/v1/daily-report/legacy/my-tasks', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log('任务API状态:', tasksResponse.status)
    if (tasksResponse.ok) {
      const tasksData = await tasksResponse.json()
      console.log('✅ 任务API成功，任务数量:', Array.isArray(tasksData) ? tasksData.length : '非数组')
    } else {
      console.log('❌ 任务API失败:', await tasksResponse.text())
    }
  } catch (e) {
    console.log('❌ 任务API异常:', e)
  }
  
  // 2.2 加载日报详情（编辑页面最关键的部分）
  console.log('\n2.2 加载日报详情...')
  try {
    console.log('调用详情API，ID: 12...')
    const reportResponse = await fetch('/api/v1/daily-report/legacy/my-reports/12/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log('详情API状态:', reportResponse.status)
    console.log('详情API响应头:', Object.fromEntries(reportResponse.headers.entries()))
    
    if (reportResponse.ok) {
      const reportData = await reportResponse.json()
      console.log('✅ 详情API成功:', reportData.id, reportData.report_date)
    } else {
      const errorText = await reportResponse.text()
      console.log('❌ 详情API失败:', reportResponse.status, errorText)
      
      // 尝试解析JSON错误
      try {
        const errorJson = JSON.parse(errorText)
        console.log('错误JSON:', errorJson)
      } catch (e) {
        console.log('错误文本:', errorText)
      }
    }
  } catch (e) {
    console.log('❌ 详情API异常:', e)
  }
  
  // 3. 对比axios和fetch的差异
  console.log('\n3. 对比axios和fetch的差异:')
  try {
    // 使用axios（模拟列表页面的方式）
    console.log('3.1 使用axios方式...')
    const { getDailyReport } = await import('./dailyReport')
    const axiosResult = await getDailyReport(12)
    console.log('✅ axios方式成功:', axiosResult.id)
  } catch (e: any) {
    console.log('❌ axios方式失败:', e.response?.status, e.message)
  }
  
  // 4. 分析结果
  console.log('\n4. 分析结果:')
  console.log('基于以上测试，请关注:')
  console.log('A. 如果fetch成功但axios失败: 问题在axios拦截器')
  console.log('B. 如果fetch也失败: 问题在token或代理配置')
  console.log('C. 如果都成功: 问题在页面跳转时机')
  
  console.log('\n=== 编辑页面token测试完成 ===')
}

// 导出测试工具
if (typeof window !== 'undefined') {
  (window as any).editPageTokenTest = editPageTokenTest
}