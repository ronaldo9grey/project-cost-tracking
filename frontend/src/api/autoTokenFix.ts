// 自动token修复工具
export const autoTokenFix = async () => {
  console.log('=== 开始自动Token修复 ===')
  
  try {
    // 1. 检查当前token状态
    console.log('1. 检查当前token状态...')
    const currentToken = localStorage.getItem('token')
    console.log('当前token存在:', !!currentToken)
    
    // 2. 清理可能损坏的token
    console.log('2. 清理可能损坏的token...')
    localStorage.removeItem('token')
    localStorage.removeItem('currentUser')
    console.log('已清理localStorage')
    
    // 3. 重新登录
    console.log('3. 重新登录...')
    const formData = new URLSearchParams()
    formData.append('username', 'admin')
    formData.append('password', '123456')
    
    const loginResponse = await fetch('/project/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    })
    
    console.log('登录响应状态:', loginResponse.status)
    
    if (loginResponse.ok) {
      const loginData = await loginResponse.json()
      console.log('登录成功:', loginData)
      
      if (loginData.code === 200 && loginData.data?.access_token) {
        const newToken = loginData.data.access_token
        console.log('新token:', newToken.substring(0, 30) + '...')
        
        // 4. 保存新token
        console.log('4. 保存新token...')
        localStorage.setItem('token', newToken)
        console.log('Token已保存到localStorage')
        
        // 5. 保存用户信息
        const userInfo = {
          id: '1',
          employee_id: '0001',
          employee_name: 'admin',
          name: 'admin',
          username: 'admin'
        }
        localStorage.setItem('currentUser', JSON.stringify(userInfo))
        console.log('用户信息已保存')
        
        // 6. 立即测试新token
        console.log('5. 立即测试新token...')
        const testResponse = await fetch('/project/api/v1/daily-report/legacy/my-reports/12/', {
          headers: {
            'Authorization': `Bearer ${newToken}`,
            'Content-Type': 'application/json'
          }
        })
        
        console.log('测试详情API状态:', testResponse.status)
        
        if (testResponse.ok) {
          const testData = await testResponse.json()
          console.log('✅ Token修复成功！')
          console.log('日报数据:', testData.id, testData.report_date)
          
          return { success: true, token: newToken, report: testData }
        } else {
          console.log('❌ 测试失败:', testResponse.status, await testResponse.text())
          return { success: false, error: 'test_failed', status: testResponse.status }
        }
      } else {
        console.log('❌ 登录响应格式错误:', loginData)
        return { success: false, error: 'login_format_error', data: loginData }
      }
    } else {
      const errorText = await loginResponse.text()
      console.log('❌ 登录失败:', errorText)
      return { success: false, error: 'login_failed', response: errorText }
    }
    
  } catch (error) {
    console.error('❌ 自动修复异常:', error)
    return { success: false, error: error.message }
  }
}

// 导出修复函数
if (typeof window !== 'undefined') {
  (window as any).autoTokenFix = autoTokenFix
}