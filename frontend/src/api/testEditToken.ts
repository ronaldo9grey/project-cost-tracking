// 测试编辑页面token发送情况
import { getDailyReport } from './dailyReport'
import { ElMessage } from 'element-plus'

export const testEditPageToken = async () => {
  console.log('=== 测试编辑页面token发送 ===')
  
  try {
    // 1. 检查localStorage中的token
    const token = localStorage.getItem('token')
    console.log('localStorage中的token:', token ? token.substring(0, 20) + '...' : 'null')
    
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
    
    ElMessage.success('编辑页面token发送测试成功')
    
    return { success: true, report }
    
  } catch (error: any) {
    console.error('❌ 编辑页面token发送测试失败:', error)
    console.error('错误详情:', {
      message: error.message,
      status: error.response?.status,
      url: error.config?.url,
      headers: error.config?.headers,
      hasToken: !!localStorage.getItem('token')
    })
    
    ElMessage.error(`编辑页面token发送测试失败: ${error.message}`)
    
    return { success: false, error }
  }
}

// 导出测试函数，可以在控制台直接调用
if (typeof window !== 'undefined') {
  (window as any).testEditPageToken = testEditPageToken
}