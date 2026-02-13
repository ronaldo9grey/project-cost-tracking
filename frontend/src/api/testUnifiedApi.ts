// 测试统一API模块的修复效果
import { getMyReports, getMyTasks } from './dailyReport'
import { ElMessage } from 'element-plus'

export const testUnifiedApi = async () => {
  console.log('=== 测试统一API修复效果 ===')
  
  try {
    // 1. 测试getMyTasks
    console.log('1. 测试getMyTasks...')
    const tasksResponse = await getMyTasks()
    console.log('getMyTasks响应:', tasksResponse)
    console.log('getMyTasks响应类型:', typeof tasksResponse)
    console.log('getMyTasks是否数组:', Array.isArray(tasksResponse))
    
    if (Array.isArray(tasksResponse)) {
      console.log('✅ getMyTasks返回数组格式正确')
    } else if (tasksResponse?.items) {
      console.log('✅ getMyTasks返回对象格式正确')
    } else {
      console.log('❌ getMyTasks返回格式异常:', tasksResponse)
    }
    
    // 2. 测试getMyReports
    console.log('\n2. 测试getMyReports...')
    const reportsResponse = await getMyReports()
    console.log('getMyReports响应:', reportsResponse)
    console.log('getMyReports响应类型:', typeof reportsResponse)
    console.log('getMyReports是否有items:', 'items' in reportsResponse)
    
    if (reportsResponse?.items) {
      console.log('✅ getMyReports返回格式正确')
      console.log('日报数量:', reportsResponse.items.length)
    } else {
      console.log('❌ getMyReports返回格式异常:', reportsResponse)
    }
    
    ElMessage.success('统一API测试完成，请查看控制台')
    
  } catch (error: any) {
    console.error('❌ 统一API测试失败:', error)
    console.error('错误详情:', {
      message: error.message,
      status: error.response?.status,
      url: error.config?.url
    })
    ElMessage.error(`统一API测试失败: ${error.message}`)
  }
}

// 导出测试函数，可以在控制台直接调用
if (typeof window !== 'undefined') {
  (window as any).testUnifiedApi = testUnifiedApi
}