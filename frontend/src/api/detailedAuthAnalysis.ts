// 详细的认证流程分析工具
export const detailedAuthAnalysis = async () => {
  console.log('=== 开始详细的认证流程分析 ===')
  
  try {
    // 1. 检查当前页面和路由状态
    console.log('1. 页面状态:')
    console.log('  当前路径:', window.location.pathname)
    console.log('  当前URL:', window.location.href)
    
    // 2. 检查localStorage状态
    console.log('2. localStorage状态:')
    const token = localStorage.getItem('token')
    const currentUser = localStorage.getItem('currentUser')
    console.log('  token存在:', !!token)
    console.log('  token长度:', token ? token.length : 0)
    console.log('  userInfo存在:', !!currentUser)
    
    // 3. 解码token内容
    if (token) {
      try {
        const parts = token.split('.')
        const payload = JSON.parse(atob(parts[1]))
        console.log('3. Token内容分析:')
        console.log('  用户名:', payload.sub || payload.username)
        console.log('  过期时间:', payload.exp ? new Date(payload.exp * 1000).toISOString() : '无过期时间')
        console.log('  当前时间:', new Date().toISOString())
        
        const now = Math.floor(Date.now() / 1000)
        console.log('  是否过期:', payload.exp && payload.exp < now)
        
      } catch (e) {
        console.log('3. Token解码失败:', e)
      }
    }
    
    // 4. 测试所有日报相关API
    console.log('4. 测试所有日报API:')
    
    // 测试列表API
    try {
      console.log('  测试列表API...')
      const listResponse = await fetch('/project/api/v1/daily-report/legacy/my-reports', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      console.log('    列表API状态:', listResponse.status)
      if (listResponse.ok) {
        const listData = await listResponse.json()
        console.log('    列表API成功:', listData.items?.length || 0, '条记录')
      } else {
        console.log('    列表API失败:', listResponse.statusText)
      }
    } catch (e) {
      console.log('    列表API异常:', e)
    }
    
    // 测试任务API
    try {
      console.log('  测试任务API...')
      const tasksResponse = await fetch('/project/api/v1/daily-report/legacy/my-tasks', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      console.log('    任务API状态:', tasksResponse.status)
      if (tasksResponse.ok) {
        const tasksData = await tasksResponse.json()
        console.log('    任务API成功:', Array.isArray(tasksData) ? tasksData.length : '非数组', '条任务')
      } else {
        console.log('    任务API失败:', tasksResponse.statusText)
      }
    } catch (e) {
      console.log('    任务API异常:', e)
    }
    
    // 测试详情API
    try {
      console.log('  测试详情API (ID: 10)...')
      const detailResponse = await fetch('/project/api/v1/daily-report/legacy/my-reports/10/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      console.log('    详情API状态:', detailResponse.status)
      if (detailResponse.ok) {
        const detailData = await detailResponse.json()
        console.log('    详情API成功:', detailData.id, detailData.report_date)
      } else {
        console.log('    详情API失败:', detailResponse.status, detailResponse.statusText)
        const errorText = await detailResponse.text()
        console.log('    详情API错误内容:', errorText)
      }
    } catch (e) {
      console.log('    详情API异常:', e)
    }
    
    // 5. 对比axios和fetch的差异
    console.log('5. 对比axios和fetch的行为差异:')
    
    try {
      // 使用axios（unifiedApi）
      console.log('  使用axios调用详情API...')
      const { getDailyReport } = await import('./dailyReport')
      const axiosResult = await getDailyReport(10)
      console.log('    axios调用成功:', axiosResult.id)
    } catch (e: any) {
      console.log('    axios调用失败:', e.response?.status, e.message)
    }
    
    console.log('=== 认证流程分析完成 ===')
    
  } catch (error) {
    console.error('分析过程出错:', error)
  }
}

// 导出测试函数
if (typeof window !== 'undefined') {
  (window as any).detailedAuthAnalysis = detailedAuthAnalysis
}