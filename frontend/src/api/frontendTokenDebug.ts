// 深度调试前端token状态，找出干扰因素
export const frontendTokenDebug = async () => {
  console.log('=== 深度调试前端token状态 ===')
  
  // 1. 检查localStorage中的token
  console.log('1. localStorage token检查:')
  const token = localStorage.getItem('token')
  console.log('Token存在:', !!token)
  if (token) {
    console.log('Token长度:', token.length)
    console.log('Token前30字符:', token.substring(0, 30) + '...')
    console.log('Token类型:', typeof token)
    
    // 解码JWT查看内容
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
  } else {
    console.log('没有找到token')
  }
  
  // 2. 检查页面状态
  console.log('\n2. 页面状态检查:')
  console.log('当前URL:', window.location.href)
  console.log('当前路径:', window.location.pathname)
  console.log('页面标题:', document.title)
  
  // 3. 尝试直接API调用
  console.log('\n3. 直接API调用测试:')
  
  try {
    console.log('调用列表API...')
    const listResponse = await fetch('/project/api/v1/daily-report/legacy/my-reports', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log('列表API状态:', listResponse.status)
    if (listResponse.ok) {
      const listData = await listResponse.json()
      console.log('✅ 列表API成功，日报数量:', listData.items?.length || 0)
    } else {
      console.log('❌ 列表API失败:', await listResponse.text())
    }
    
    console.log('调用详情API...')
    const detailResponse = await fetch('/project/api/v1/daily-report/legacy/my-reports/12/', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log('详情API状态:', detailResponse.status)
    if (detailResponse.ok) {
      const detailData = await detailResponse.json()
      console.log('✅ 详情API成功:', detailData.id, detailData.report_date)
    } else {
      console.log('❌ 详情API失败:', await detailResponse.text())
    }
    
  } catch (e) {
    console.log('❌ API调用异常:', e)
  }
  
  // 4. 检查HTTP拦截器状态
  console.log('\n4. HTTP拦截器状态检查:')
  console.log('检查axios实例状态...')
  
  try {
    // 直接使用axios实例
    const axios = await import('axios').then(m => m.default || m)
    
    // 测试axios直接调用
    console.log('测试axios直接调用...')
    const axiosResult = await axios.get('v1/daily-report/legacy/my-reports/12/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    console.log('✅ axios直接调用成功:', axiosResult.data)
    
  } catch (e: any) {
    console.log('❌ axios直接调用失败:', e.response?.status, e.message)
    
    console.log('axios错误详情:', {
      status: e.response?.status,
      message: e.message,
      data: e.response?.data
    })
  }
  
  // 5. 检查可能的干扰源
  console.log('\n5. 检查可能的干扰源:')
  
  // 检查是否有多个标签页
  const channels = new BroadcastChannel('test-channel')
  console.log('BroadcastChannel可用:', !!channels)
  
  // 检查localStorage事件监听
  console.log('监听localStorage变化...')
  window.addEventListener('storage', (event) => {
    console.log('localStorage变化:', event.key, event.newValue?.substring(0, 20) + '...')
  })
  
  console.log('\n=== 调试完成 ===')
}

// 导出调试工具
if (typeof window !== 'undefined') {
  (window as any).frontendTokenDebug = frontendTokenDebug
}