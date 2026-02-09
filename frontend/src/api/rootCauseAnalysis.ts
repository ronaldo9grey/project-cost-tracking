// 根本原因分析：为什么列表能工作但详情API失效
export const rootCauseAnalysis = async () => {
  console.log('=== 开始根本原因分析 ===')
  
  const token = localStorage.getItem('token')
  if (!token) {
    console.log('❌ 没有token，分析结束')
    return
  }
  
  console.log('✅ 找到token，开始分析')
  
  // 1. 测试列表API
  console.log('1. 测试列表API...')
  try {
    const listResponse = await fetch('/api/v1/daily-report/legacy/my-reports', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    console.log('列表API状态:', listResponse.status)
    
    if (listResponse.ok) {
      const listData = await listResponse.json()
      console.log('✅ 列表API成功，获取到', listData.items?.length || 0, '条记录')
      if (listData.items && listData.items.length > 0) {
        console.log('第一个日报ID:', listData.items[0].id)
        console.log('日报状态:', listData.items[0].status)
        console.log('日报员工ID:', listData.items[0].employee_id)
      }
    } else {
      console.log('❌ 列表API失败:', listResponse.status)
    }
  } catch (e) {
    console.log('❌ 列表API异常:', e)
  }
  
  // 2. 测试详情API - 使用相同的日报ID
  console.log('\n2. 测试详情API (使用列表中的日报ID)...')
  try {
    // 先获取第一个可用的日报ID
    const listResponse = await fetch('/api/v1/daily-report/legacy/my-reports', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    
    if (listResponse.ok) {
      const listData = await listResponse.json()
      if (listData.items && listData.items.length > 0) {
        const firstReport = listData.items[0]
        console.log('使用日报ID:', firstReport.id)
        
        // 使用相同的token测试详情API
        const detailResponse = await fetch(`/api/v1/daily-report/legacy/my-reports/${firstReport.id}/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        console.log('详情API状态:', detailResponse.status)
        
        if (detailResponse.ok) {
          const detailData = await detailResponse.json()
          console.log('✅ 详情API成功:', detailData.id, detailData.report_date)
        } else {
          console.log('❌ 详情API失败:', detailResponse.status)
          const errorText = await detailResponse.text()
          console.log('详情API错误内容:', errorText)
        }
      }
    }
  } catch (e) {
    console.log('❌ 详情API异常:', e)
  }
  
  // 3. 对比请求头差异
  console.log('\n3. 分析请求头差异...')
  console.log('当前页面URL:', window.location.href)
  console.log('当前路径:', window.location.pathname)
  
  // 4. 测试不同日报ID的详情API
  console.log('\n4. 测试不同日报ID的详情API...')
  const testIds = [10, 11, 12]
  
  for (const testId of testIds) {
    try {
      console.log(`测试日报ID ${testId}...`)
      const detailResponse = await fetch(`/api/v1/daily-report/legacy/my-reports/${testId}/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      console.log(`  ID ${testId}:`, detailResponse.status)
      
      if (detailResponse.ok) {
        const detailData = await detailResponse.json()
        console.log(`  ID ${testId}: 成功，状态=${detailData.status}`)
      } else {
        console.log(`  ID ${testId}: 失败`)
      }
    } catch (e) {
      console.log(`  ID ${testId}: 异常`)
    }
  }
  
  // 5. 分析可能的根本原因
  console.log('\n5. 根本原因分析:')
  console.log('基于以上测试，可能的原因:')
  console.log('A. 某些日报ID不存在，返回401而不是404')
  console.log('B. 权限验证逻辑不同：列表 vs 详情')
  console.log('C. API端点配置差异')
  console.log('D. token在特定条件下失效')
  
  console.log('\n=== 根本原因分析完成 ===')
}

// 导出测试函数
if (typeof window !== 'undefined') {
  (window as any).rootCauseAnalysis = rootCauseAnalysis
}