// 测试token有效性
export const testTokenValidity = async () => {
  console.log('=== 测试token有效性 ===')
  
  try {
    // 1. 检查localStorage中的token
    const token = localStorage.getItem('token')
    console.log('localStorage中的token:', token ? token.substring(0, 30) + '...' : 'null')
    
    if (!token) {
      console.log('❌ 没有找到token')
      return { valid: false, reason: 'no_token' }
    }
    
    // 2. 解码JWT token来检查内容（不验证签名）
    try {
      const parts = token.split('.')
      if (parts.length !== 3) {
        console.log('❌ Token格式不正确')
        return { valid: false, reason: 'invalid_format' }
      }
      
      const payload = JSON.parse(atob(parts[1]))
      console.log('Token payload:', payload)
      
      // 检查是否过期
      const now = Math.floor(Date.now() / 1000)
      if (payload.exp && payload.exp < now) {
        console.log('❌ Token已过期:', new Date(payload.exp * 1000).toISOString())
        return { valid: false, reason: 'expired', exp: payload.exp }
      }
      
      // 检查用户名
      if (payload.sub) {
        console.log('Token用户名:', payload.sub)
      }
      
    } catch (e) {
      console.log('❌ Token解析失败:', e)
      return { valid: false, reason: 'parse_error' }
    }
    
    console.log('✅ Token格式看起来有效')
    return { valid: true, token: token }
    
  } catch (error) {
    console.error('Token测试失败:', error)
    return { valid: false, reason: 'error', error }
  }
}

// 导出测试函数
if (typeof window !== 'undefined') {
  (window as any).testTokenValidity = testTokenValidity
}