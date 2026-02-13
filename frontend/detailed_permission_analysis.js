// 深入分析权限验证问题
async function detailedPermissionAnalysis() {
  console.log('=== 深入分析权限验证问题 ===');
  
  const token = localStorage.getItem('token');
  console.log('当前token:', !!token ? '存在' : '不存在');
  
  // 1. 获取用户信息
  console.log('\n1. 获取用户信息:');
  let currentUser = null;
  try {
    const userResponse = await fetch('/api/v1/auth/users/me', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      }
    });
    
    if (userResponse.ok) {
      const userData = await userResponse.json();
      currentUser = userData.data;
      console.log('当前用户:', currentUser);
      
      // 检查JWT token内容
      if (token) {
        const parts = token.split('.');
        if (parts.length === 3) {
          const payload = JSON.parse(atob(parts[1]));
          console.log('JWT sub字段:', payload.sub);
          console.log('JWT exp:', new Date(payload.exp * 1000).toISOString());
          console.log('当前时间:', new Date().toISOString());
        }
      }
    } else {
      console.log('❌ 获取用户信息失败:', userResponse.status);
    }
  } catch (e) {
    console.log('❌ 用户信息检查异常:', e.message);
  }
  
  // 2. 获取日报列表
  console.log('\n2. 获取日报列表:');
  let reports = [];
  try {
    const listResponse = await fetch('/api/v1/daily-report/legacy/my-reports', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      }
    });
    
    if (listResponse.ok) {
      const listData = await listResponse.json();
      reports = listData.items || [];
      console.log('用户日报数量:', reports.length);
      
      reports.forEach((report, index) => {
        console.log(`  ${index + 1}. ID:${report.id} 日期:${report.report_date} 状态:${report.status} 员工ID:${report.employee_id}`);
      });
    } else {
      console.log('❌ 获取日报列表失败:', listResponse.status);
    }
  } catch (e) {
    console.log('❌ 日报列表检查异常:', e.message);
  }
  
  // 3. 测试不同的日报访问
  console.log('\n3. 测试不同的日报访问:');
  
  for (const report of reports.slice(0, 2)) { // 测试前2个日报
    console.log(`\n测试日报ID=${report.id}:`);
    console.log(`  日报信息: ID=${report.id}, employee_id=${report.employee_id}`);
    console.log(`  当前用户: employee_id=${currentUser?.username}`);
    console.log(`  权限检查: ${report.employee_id === currentUser?.username ? '✅ 应该通过' : '❌ 应该拒绝'}`);
    
    try {
      const detailResponse = await fetch(`/api/v1/daily-report/legacy/my-reports/${report.id}`, {
        headers: {
          'Authorization': 'Bearer ' + token,
          'Content-Type': 'application/json'
        }
      });
      
      console.log(`  API状态: ${detailResponse.status}`);
      
      if (detailResponse.ok) {
        const detailData = await detailResponse.json();
        console.log(`  ✅ 访问成功: ${detailData.id}`);
      } else {
        const errorText = await detailResponse.text();
        console.log(`  ❌ 访问失败: ${detailResponse.status}`);
        
        try {
          const errorJson = JSON.parse(errorText);
          console.log(`    错误详情: ${errorJson.detail || errorJson.message}`);
        } catch (e) {
          console.log(`    错误文本: ${errorText.substring(0, 100)}...`);
        }
      }
    } catch (e) {
      console.log(`  ❌ 访问异常: ${e.message}`);
    }
  }
  
  // 4. 检查后端日志分析
  console.log('\n4. 后端日志分析:');
  console.log('403 Forbidden错误可能的原因:');
  console.log('A. 后端权限验证逻辑bug');
  console.log('B. 数据库查询条件错误');
  console.log('C. 中间件或过滤器问题');
  console.log('D. 缓存或会话问题');
  
  // 5. 建议解决方案
  console.log('\n5. 建议解决方案:');
  console.log('由于权限逻辑看起来正确，建议:');
  console.log('A. 检查后端代码的权限验证逻辑');
  console.log('B. 查看后端日志获取更详细的错误信息');
  console.log('C. 测试其他HTTP方法（POST, DELETE）');
  console.log('D. 重新登录清除可能的缓存问题');
  
  console.log('\n=== 深入分析完成 ===');
}

// 运行分析
detailedPermissionAnalysis();