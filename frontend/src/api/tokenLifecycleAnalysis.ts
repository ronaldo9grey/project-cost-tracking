// Token生命周期完整分析
export const tokenLifecycleAnalysis = async () => {
  console.log('=== 开始Token生命周期分析 ===')
  
  // 1. 记录分析开始时间
  const startTime = new Date().toISOString()
  console.log('分析开始时间:', startTime)
  
  // 2. 检查当前token状态
  console.log('1. 当前token状态检查:')
  const currentToken = localStorage.getItem('token')
  console.log('  localStorage token存在:', !!currentToken)
  console.log('  token长度:', currentToken ? currentToken.length : 0)
  console.log('  token前缀:', currentToken ? currentToken.substring(0, 20) + '...' : 'null')
  
  if (!currentToken) {
    console.log('❌ 没有找到token，分析结束')
    return { hasToken: false }
  }
  
  // 3. 解析token内容
  console.log('2. Token内容分析:')
  try {
    const parts = currentToken.split('.')
    if (parts.length !== 3) {
      console.log('❌ Token格式错误：不是有效的JWT')
      return { hasToken: true, valid: false, reason: 'invalid_format' }
    }
    
    const payload = JSON.parse(atob(parts[1]))
    console.log('  Token payload:')
    console.log('    用户名:', payload.sub || payload.username)
    console.log('    颁发者:', payload.iss)
    console.log('    受众:', payload.aud)
    console.log('    过期时间:', payload.exp ? new Date(payload.exp * 1000).toISOString() : '无过期时间')
    console.log('    颁发时间:', payload.iat ? new Date(payload.iat * 1000).toISOString() : '无颁发时间')
    console.log('    当前时间:', new Date().toISOString())
    
    const now = Math.floor(Date.now() / 1000)
    const isExpired = payload.exp && payload.exp < now
    console.log('    是否过期:', isExpired)
    
    if (isExpired) {
      console.log('❌ Token已过期')
      return { hasToken: true, valid: false, reason: 'expired', payload }
    }
    
  } catch (e) {
    console.log('❌ Token解析失败:', e)
    return { hasToken: true, valid: false, reason: 'parse_error' }
  }
  
  // 4. 测试当前token在不同API中的表现
  console.log('3. 测试当前token在不同API中的表现:')
  const apiTests = [
    { name: '列表API', url: 'v1/daily-report/legacy/my-reports' },
    { name: '详情API', url: 'v1/daily-report/legacy/my-reports/12/' },
    { name: '任务API', url: 'v1/daily-report/legacy/my-tasks' }
  ]
  
  const testResults = []
  
  for (const test of apiTests) {
    try {
      console.log(`  测试${test.name}...`)
      const response = await fetch(test.url, {
        headers: {
          'Authorization': `Bearer ${currentToken}`,
          'Content-Type': 'application/json'
        }
      })
      
      console.log(`    状态: ${response.status}`)
      
      if (response.ok) {
        console.log(`    ✅ ${test.name}成功`)
        testResults.push({ name: test.name, status: 'success' })
      } else {
        const errorText = await response.text()
        console.log(`    ❌ ${test.name}失败: ${errorText}`)
        testResults.push({ name: test.name, status: 'failed', error: errorText })
      }
    } catch (e) {
      console.log(`    ❌ ${test.name}异常:`, e)
      testResults.push({ name: test.name, status: 'exception', error: e.message })
    }
  }
  
  // 5. 检查可能的token变更历史
  console.log('4. 检查token变更历史:')
  console.log('  检查localStorage key变化...')
  
  // 6. 验证登录流程
  console.log('5. 验证当前登录流程:')
  try {
    const formData = new URLSearchParams()
    formData.append('username', 'admin')
    formData.append('password', '123456')
    
    const loginResponse = await fetch('/project/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    })
    
    console.log('  重新登录状态:', loginResponse.status)
    
    if (loginResponse.ok) {
      const loginData = await loginResponse.json()
      const newToken = loginData.data?.access_token
      
      console.log('  重新登录成功')
      console.log('  旧token:', currentToken.substring(0, 30) + '...')
      console.log('  新token:', newToken?.substring(0, 30) + '...')
      console.log('  Token是否相同:', currentToken === newToken)
      
      if (newToken && newToken !== currentToken) {
        console.log('  ⚠️  Token已更新，更新localStorage...')
        localStorage.setItem('token', newToken)
        
        // 立即测试新token
        console.log('  测试新token...')
        const newDetailResponse = await fetch('/project/api/v1/daily-report/legacy/my-reports/12/', {
          headers: {
            'Authorization': `Bearer ${newToken}`,
            'Content-Type': 'application/json'
          }
        })
        
        console.log('  新token详情API状态:', newDetailResponse.status)
        
        if (newDetailResponse.ok) {
          console.log('✅ 问题解决！新token可以正常工作')
          return { 
            hasToken: true, 
            valid: true, 
            updated: true, 
            reason: 'token_refreshed_and_working',
            testResults: testResults
          }
        } else {
          console.log('❌ 新token仍然无法工作')
          return { 
            hasToken: true, 
            valid: false, 
            reason: 'token_refresh_failed',
            error: await newDetailResponse.text()
          }
        }
      } else {
        console.log('  ✅ Token相同，无需更新')
      }
    } else {
      console.log('❌ 重新登录失败:', await loginResponse.text())
    }
  } catch (e) {
    console.log('❌ 重新登录异常:', e)
  }
  
  // 7. 总结分析结果
  console.log('6. 分析总结:')
  console.log('  当前token状态:', currentToken ? '存在' : '不存在')
  console.log('  API测试结果:', testResults)
  
  return {
    hasToken: !!currentToken,
    valid: true,
    testResults: testResults,
    timestamp: startTime
  }
}

// 导出测试函数
if (typeof window !== 'undefined') {
  (window as any).tokenLifecycleAnalysis = tokenLifecycleAnalysis
}