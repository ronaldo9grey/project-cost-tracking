// 测试HTTP拦截器对日报API的401错误处理
import { getDailyReport } from './dailyReport'
import { ElMessage } from 'element-plus'

export const test401Handling = async () => {
  console.log('=== 测试HTTP拦截器对401错误的处理 ===')
  
  try {
    // 1. 先验证当前token状态
    const token = localStorage.getItem('token')
    console.log('当前token状态:', token ? '存在' : '不存在')
    
    // 2. 测试getDailyReport调用
    console.log('2. 测试getDailyReport调用...')
    
    // 使用已知的日报ID进行测试
    const testId = 12
    console.log(`调用getDailyReport(${testId})...`)
    
    const report = await getDailyReport(testId)
    
    console.log('✅ getDailyReport调用成功:', {
      id: report.id,
      status: report.status,
      report_date: report.report_date
    })
    
    ElMessage.success('HTTP拦截器处理正常')
    
    return { success: true, report }
    
  } catch (error: any) {
    console.error('❌ HTTP拦截器处理异常:', error)
    console.error('错误详情:', {
      message: error.message,
      status: error.response?.status,
      url: error.config?.url,
      method: error.config?.method,
      headers: error.config?.headers,
      hasToken: !!localStorage.getItem('token'),
      isDailyReport: error.config?.url?.includes('/daily-report')
    })
    
    // 判断错误是否被正确处理
    if (error.response?.status === 401 && error.config?.url?.includes('/daily-report')) {
      console.warn('⚠️  日报API的401错误未被正确静默处理，错误传播到了组件')
    }
    
    ElMessage.error(`HTTP拦截器处理异常: ${error.message}`)
    
    return { success: false, error }
  }
}

// 导出测试函数，可以在控制台直接调用
if (typeof window !== 'undefined') {
  (window as any).test401Handling = test401Handling
}