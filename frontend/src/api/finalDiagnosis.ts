// 最终诊断：追踪前端请求的确切失败原因
export const finalDiagnosis = async () => {
  console.log('=== 开始最终诊断 ===')
  
  const token = localStorage.getItem('token')
  if (!token) {
    console.log('❌ 没有token，诊断结束')
    return
  }
  
  console.log('✅ 找到token:', token.substring(0, 20) + '...')
  
  // 1. 测试代理是否正常工作
  console.log('1. 测试代理是否正常工作...')
  try {
    const proxyTest = await fetch('/api/v1/daily-report/legacy/my-reports', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    console.log('代理测试状态:', proxyTest.status)
    
    if (proxyTest.ok) {
      const data = await proxyTest.json()
      console.log('✅ 代理正常工作，获取到', data.items?.length || 0, '条记录')
      
      // 2. 使用代理测试详情API
      console.log('2. 使用代理测试详情API...')
      const proxyDetail = await fetch('/api/v1/daily-report/legacy/my-reports/12/', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      console.log('代理详情状态:', proxyDetail.status)
      
      if (proxyDetail.ok) {
        const detailData = await proxyDetail.json()
        console.log('✅ 代理详情API成功:', detailData.id)
      } else {
        console.log('❌ 代理详情API失败:', proxyDetail.status)
        const errorText = await proxyDetail.text()
        console.log('错误内容:', errorText)
      }
    } else {
      console.log('❌ 代理测试失败:', proxyTest.status)
    }
  } catch (e) {
    console.log('❌ 代理测试异常:', e)
  }
  
  // 3. 详细追踪axios请求
  console.log('3. 详细追踪axios请求...')
  try {
    // 导入axios实例
    const { getDailyReport } = await import('./dailyReport')
    
    console.log('开始axios请求...')
    const result = await getDailyReport(12)
    console.log('✅ axios请求成功:', result.id)
  } catch (e: any) {
    console.log('❌ axios请求失败:', e.response?.status)
    console.log('错误详情:', {
      message: e.message,
      status: e.response?.status,
      url: e.config?.url,
      method: e.config?.method,
      headers: e.config?.headers,
      timestamp: new Date().toISOString()
    })
    
    // 分析可能的原因
    console.log('\n4. 原因分析:')
    console.log('A. HTTP拦截器处理异常')
    console.log('B. 请求头不匹配')
    console.log('C. 代理配置问题')
    console.log('D. 时机问题（页面切换时token丢失）')
  }
  
  // 5. 监控页面切换
  console.log('\n5. 页面切换监控:')
  console.log('当前页面:', window.location.pathname)
  console.log('页面标题:', document.title)
  
  // 6. 建议的解决方案
  console.log('\n6. 建议的解决方案:')
  console.log('如果问题持续，请尝试:')
  console.log('1. 重新登录')
  console.log('2. 清除浏览器缓存')
  console.log('3. 重启前端服务')
  console.log('4. 检查网络连接')
  
  console.log('\n=== 最终诊断完成 ===')
}

// 导出测试函数
if (typeof window !== 'undefined') {
  (window as any).finalDiagnosis = finalDiagnosis
}