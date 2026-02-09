// 分析API端点差异问题
async function apiEndpointAnalysis() {
  console.log('=== 分析API端点差异问题 ===');
  
  const token = localStorage.getItem('token');
  console.log('当前token存在:', !!token);
  
  // 1. 测试不同的API端点格式
  console.log('\n1. 测试不同API端点格式:');
  
  const endpoints = [
    { url: '/api/v1/daily-report/legacy/my-tasks', description: '任务API（成功）' },
    { url: '/api/v1/daily-report/legacy/my-reports', description: '日报列表API' },
    { url: '/api/v1/daily-report/legacy/my-reports/12/', description: '详情API（有斜杠）' },
    { url: '/api/v1/daily-report/legacy/my-reports/12', description: '详情API（无斜杠）' },
    { url: '/api/v1/daily-report/legacy/my-reports/10/', description: '详情API（日报ID=10）' },
    { url: '/api/v1/daily-report/legacy/my-reports/10', description: '详情API（日报ID=10，无斜杠）' }
  ];
  
  for (const endpoint of endpoints) {
    console.log(`\n测试: ${endpoint.description}`);
    console.log(`URL: ${endpoint.url}`);
    
    try {
      const response = await fetch(endpoint.url, {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer ' + token,
          'Content-Type': 'application/json'
        }
      });
      
      console.log(`状态码: ${response.status}`);
      
      if (response.ok) {
        const data = await response.json();
        console.log(`✅ 成功: ${endpoint.description}`);
        if (endpoint.url.includes('/my-reports')) {
          console.log(`  数据: ${Array.isArray(data.items) ? data.items.length : '非数组'} 条记录`);
        }
      } else {
        const errorText = await response.text();
        console.log(`❌ 失败: ${response.status} - ${errorText.substring(0, 100)}...`);
      }
    } catch (e) {
      console.log(`❌ 异常: ${e.message}`);
    }
  }
  
  // 2. 分析URL格式问题
  console.log('\n2. URL格式分析:');
  console.log('注意：详情API使用了不同的URL格式');
  console.log('成功: /api/v1/daily-report/legacy/my-tasks');
  console.log('失败: /api/v1/daily-report/legacy/my-reports/10/');
  console.log('差异：');
  console.log('A. 路径结构不同：tasks vs my-reports');
  console.log('B. 详情API有参数：/10/');
  console.log('C. 可能是后端路由配置问题');
  
  // 3. 建议解决方案
  console.log('\n3. 建议解决方案:');
  console.log('A. 检查后端路由配置是否一致');
  console.log('B. 统一API端点格式');
  console.log('C. 检查权限验证逻辑差异');
  console.log('D. 修复URL末尾斜杠问题');
  
  console.log('\n=== API端点分析完成 ===');
}

// 运行分析
apiEndpointAnalysis();