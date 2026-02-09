// 分析用户数据不一致问题，找出EMP001用户的真实情况
export const userDataAnalysis = async () => {
  console.log('=== 分析用户数据不一致问题 ===')
  
  // 1. 检查当前登录状态
  console.log('1. 检查当前登录状态:')
  const token = localStorage.getItem('token')
  const userInfo = localStorage.getItem('currentUser')
  
  console.log('Token存在:', !!token)
  console.log('用户信息存在:', !!userInfo)
  
  if (userInfo) {
    const parsedUserInfo = JSON.parse(userInfo)
    console.log('localStorage中的用户信息:', parsedUserInfo)
  }
  
  // 2. 调用后端API获取真实用户信息
  console.log('\n2. 调用后端API获取真实用户信息:')
  
  try {
    const userResponse = await fetch('/api/v1/auth/users/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    console.log('用户信息API状态:', userResponse.status)
    
    if (userResponse.ok) {
      const userData = await userResponse.json()
      console.log('后端返回的用户信息:', userData)
      
      const backendUserInfo = userData.data
      console.log('后端用户信息详情:', {
        id: backendUserInfo.id,
        username: backendUserInfo.username,
        role_id: backendUserInfo.role_id
      })
      
      // 3. 检查JWT token内容
      console.log('\n3. 检查JWT token内容:')
      if (token) {
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
      
      // 4. 检查日报数据
      console.log('\n4. 检查日报数据:')
      try {
        const reportsResponse = await fetch('/api/v1/daily-report/legacy/my-reports', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        console.log('日报列表API状态:', reportsResponse.status)
        
        if (reportsResponse.ok) {
          const reportsData = await reportsResponse.json()
          const reports = reportsData.items || []
          console.log('日报数据数量:', reports.length)
          
          if (reports.length > 0) {
            const firstReport = reports[0]
            console.log('第一个日报的员工ID:', firstReport.employee_id)
            console.log('当前用户的工号:', backendUserInfo.username)
            console.log('权限匹配结果:', 
              backendUserInfo.username === firstReport.employee_id ? '✅ 匹配' : '❌ 不匹配')
          }
        } else {
          console.log('❌ 日报列表获取失败:', reportsResponse.status)
        }
      } catch (e) {
        console.log('❌ 日报数据检查异常:', e)
      }
      
      // 5. 问题诊断结论
      console.log('\n5. 问题诊断结论:')
      console.log('可能的问题:')
      console.log('A. EMP001用户不存在于personnel表中')
      console.log('B. EMP001用户存在但没有日报数据')
      console.log('C. 权限验证逻辑错误')
      console.log('D. 数据库数据不一致')
      
    } else {
      console.log('❌ 获取用户信息失败:', userResponse.status)
    }
    
  } catch (e) {
    console.log('❌ 用户信息API调用异常:', e)
  }
  
  console.log('\n=== 用户数据分析完成 ===')
}

// 导出分析工具
if (typeof window !== 'undefined') {
  (window as any).userDataAnalysis = userDataAnalysis
}