// 深度分析token认证问题
export const authTokenDeepAnalysis = async () => {
  console.log('=== 深度分析token认证问题 ===')
  
  // 1. 分析当前token
  const token = localStorage.getItem('token')
  console.log('1. 当前token分析:')
  console.log('  Token存在:', !!token)
  console.log('  Token长度:', token ? token.length : 0)
  console.log('  Token前30字符:', token ? token.substring(0, 30) + '...' : 'null')
  
  if (token) {
    try {
      // 解码JWT payload
      const parts = token.split('.')
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]))
        console.log('2. Token payload分析:')
        console.log('  用户名:', payload.sub || payload.username)
        console.log('  过期时间:', payload.exp ? new Date(payload.exp * 1000).toISOString() : '无过期时间')
        console.log('  当前时间:', new Date().toISOString())
        console.log('  颁发者:', payload.iss)
        console.log('  受众:', payload.aud)
        
        const now = Math.floor(Date.now() / 1000)
        console.log('  是否过期:', payload.exp && payload.exp < now)
        
      } else {
        console.log('2. Token格式错误: 不是有效的JWT格式')
      }
    } catch (e) {
      console.log('2. Token解码失败:', e)
    }
  }
  
  // 3. 测试不同的API调用方式
  console.log('3. 测试不同API调用方式:')
  
  try {
    // 测试列表API
    console.log('  测试列表API...')
    const listResponse = await fetch('/project/api/v1/daily-report/legacy/my-reports', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    console.log('    列表API状态:', listResponse.status)
    
    // 测试详情API
    console.log('  测试详情API...')
    const detailResponse = await fetch('/project/api/v1/daily-report/legacy/my-reports/12/', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    console.log('    详情API状态:', detailResponse.status)
    
    if (detailResponse.ok) {
      const detailData = await detailResponse.json()
      console.log('    详情API成功:', detailData.id)
    } else {
      const errorText = await detailResponse.text()
      console.log('    详情API失败:', errorText)
    }
    
  } catch (e) {
    console.log('  API调用异常:', e)
  }
  
  // 4. 对比正常的登录流程
  console.log('4. 验证登录流程...')
  
  try {
    // 重新登录验证
    const formData = new URLSearchParams()
    formData.append('username', 'admin')
    formData.append('password', '123456')
    
    const loginResponse = await fetch('/project/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData
    })
    
    console.log('  重新登录状态:', loginResponse.status)
    
    if (loginResponse.ok) {
      const loginData = await loginResponse.json()
      console.log('  重新登录成功')
      console.log('  新token:', loginData.data?.access_token?.substring(0, 30) + '...')
      
      // 更新token
      if (loginData.data?.access_token) {
        console.log('  更新localStorage中的token...')
        localStorage.setItem('token', loginData.data.access_token)
        
        // 再次测试详情API
        console.log('  使用新token测试详情API...')
        const newDetailResponse = await fetch('/project/api/v1/daily-report/legacy/my-reports/12/', {
          headers: {
            'Authorization': `Bearer ${loginData.data.access_token}`,
            'Content-Type': 'application/json'
          }
        })
        console.log('    新token详情API状态:', newDetailResponse.status)
        
        if (newDetailResponse.ok) {
          console.log('✅ 问题解决！新的token可以正常工作')
        } else {
          const newErrorText = await newDetailResponse.text()
          console.log('❌ 新token仍然失败:', newErrorText)
        }
      }
    }
    
  } catch (e) {
    console.log('  重新登录异常:', e)
  }
  
  console.log('=== 深度分析完成 ===')
}

// 导出测试函数
if (typeof window !== 'undefined') {
  (window as any).authTokenDeepAnalysis = authTokenDeepAnalysis
}