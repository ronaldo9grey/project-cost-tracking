// 对比列表页面和编辑页面的API调用差异
async function pageContextComparison() {
  console.log('=== 对比列表页面和编辑页面的API调用差异 ===');
  
  const token = localStorage.getItem('token');
  console.log('当前token:', token ? '有效' : '不存在');
  
  // 1. 测试列表页面API（应该成功）
  console.log('\n1. 测试列表页面API:');
  try {
    const listResponse = await fetch('/api/v1/daily-report/legacy/my-reports', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('  列表API状态:', listResponse.status);
    if (listResponse.ok) {
      const listData = await listResponse.json();
      console.log('  ✅ 列表API成功，记录数:', listData.items ? listData.items.length : 0);
    } else {
      console.log('  ❌ 列表API失败:', await listResponse.text());
    }
  } catch (e) {
    console.log('  ❌ 列表API异常:', e.message);
  }
  
  // 2. 测试编辑页面API（可能失败）
  console.log('\n2. 测试编辑页面API:');
  try {
    const detailResponse = await fetch('/api/v1/daily-report/legacy/my-reports/12/', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('  详情API状态:', detailResponse.status);
    if (detailResponse.ok) {
      const detailData = await detailResponse.json();
      console.log('  ✅ 详情API成功，日报ID:', detailData.id);
    } else {
      const errorText = await detailResponse.text();
      console.log('  ❌ 详情API失败:', detailResponse.status, errorText);
      
      // 尝试解析JSON错误
      try {
        const errorJson = JSON.parse(errorText);
        console.log('  错误详情:', errorJson.detail);
      } catch (e) {
        console.log('  错误文本:', errorText);
      }
    }
  } catch (e) {
    console.log('  ❌ 详情API异常:', e.message);
  }
  
  // 3. 对比请求头
  console.log('\n3. 请求头对比分析:');
  console.log('  使用的Authorization头: Bearer ' + (token ? token.substring(0, 20) + '...' : 'null'));
  console.log('  使用的Content-Type: application/json');
  console.log('  使用的URL:');
  console.log('    列表: /api/v1/daily-report/legacy/my-reports');
  console.log('    详情: /api/v1/daily-report/legacy/my-reports/12/');
  
  // 4. 分析可能的问题
  console.log('\n4. 问题分析:');
  console.log('  如果列表成功但详情失败，可能的原因:');
  console.log('  A. 后端路由配置问题');
  console.log('  B. 页面上下文在路由跳转时丢失');
  console.log('  C. HTTP拦截器在不同页面的行为差异');
  console.log('  D. Vite代理配置问题');
  
  console.log('\n=== 对比分析完成 ===');
}

// 运行对比
pageContextComparison();