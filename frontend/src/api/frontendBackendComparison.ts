// 对比前端和后端请求的差异
export const frontendBackendComparison = async () => {
  console.log('=== 开始前端后端请求对比 ===')
  
  const token = localStorage.getItem('token')
  if (!token) {
    console.log('❌ 没有找到token')
    return
  }
  
  console.log('✅ 找到token:', token.substring(0, 20) + '...')
  
  // 1. 模拟后端请求方式
  console.log('1. 模拟后端请求方式...')
  try {
    const response = await fetch('/project/api/v1/daily-report/legacy/my-reports/12/', {
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
      console.log('❌ 后端方式失败:', response.status)
    }
  } catch (e) {
    console.log('❌ 后端方式异常:', e)
  }
  
  // 2. 模拟前端axios请求
  console.log('\n2. 模拟前端axios请求...')
  try {
    const { getDailyReport } = await import('./dailyReport')
    const data = await getDailyReport(12)
    console.log('✅ 前端axios成功:', data.id, data.report_date)
  } catch (e: any) {
    console.log('❌ 前端axios失败:', e.response?.status, e.message)
  }
  
  // 3. 对比请求头
  console.log('\n3. 请求头对比分析...')
  console.log('当前页面:', window.location.href)
  console.log('当前路径:', window.location.pathname)
  
  // 4. 测试代理配置
  console.log('\n4. 测试代理配置...')
  
  // 直接测试API路径
  try {
    const directResponse = await fetch('/project/api/v1/daily-report/legacy/my-reports/12/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    console.log('直接路径状态:', directResponse.status)
  } catch (e) {
    console.log('直接路径异常:', e)
  }
  
  // 完整URL测试
  try {
    const fullResponse = await fetch('http://localhost:8000/api/v1/daily-report/legacy/my-reports/12/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    console.log('完整URL状态:', fullResponse.status)
  } catch (e) {
    console.log('完整URL异常:', e)
  }
  
  // 5. 检查CORS问题
  console.log('\n5. CORS和代理问题分析...')
  console.log('Vite代理配置检查:')
  console.log('  - 开发环境使用代理转发到后端')
  console.log('  - 可能存在代理配置问题')
  
  console.log('\n=== 前端后端请求对比完成 ===')
}

// 导出测试函数
if (typeof window !== 'undefined') {
  (window as any).frontendBackendComparison = frontendBackendComparison
}