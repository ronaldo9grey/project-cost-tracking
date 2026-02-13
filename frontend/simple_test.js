// 简洁版编辑页面token测试 - 避免语法错误
async function simpleTokenTest() {
  console.log('=== 开始简单token测试 ===');
  
  // 1. 检查token
  const token = localStorage.getItem('token');
  console.log('Token存在:', !!token);
  if (token) {
    console.log('Token前30字符:', token.substring(0, 30) + '...');
  }
  
  // 2. 测试详情API
  console.log('测试详情API...');
  try {
    const response = await fetch('/api/v1/daily-report/legacy/my-reports/12/', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('详情API状态:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ 详情API成功:', data.id, data.report_date);
    } else {
      const errorText = await response.text();
      console.log('❌ 详情API失败:', response.status, errorText);
    }
  } catch (e) {
    console.log('❌ API异常:', e.message);
  }
  
  console.log('=== 测试完成 ===');
}

// 运行测试
simpleTokenTest();