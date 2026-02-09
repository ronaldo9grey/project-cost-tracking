// 诊断权限验证问题
async function diagnosePermissionIssue() {
  console.log('=== 诊断权限验证问题 ===');
  
  const token = localStorage.getItem('token');
  console.log('当前token:', !!token ? '存在' : '不存在');
  
  // 1. 检查当前用户信息
  console.log('\n1. 检查当前用户信息:');
  try {
    const userResponse = await fetch('/api/v1/auth/users/me', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      }
    });
    
    if (userResponse.ok) {
      const userData = await userResponse.json();
      const userInfo = userData.data;
      console.log('当前用户:', {
        id: userInfo.id,
        username: userInfo.username,
        role_id: userInfo.role_id
      });
      
      // 检查JWT token内容
      if (token) {
        const parts = token.split('.');
        if (parts.length === 3) {
          const payload = JSON.parse(atob(parts[1]));
          console.log('JWT sub字段:', payload.sub);
          console.log('用户信息匹配:', payload.sub === userInfo.username ? '✅ 匹配' : '❌ 不匹配');
        }
      }
    } else {
      console.log('❌ 获取用户信息失败:', userResponse.status);
    }
  } catch (e) {
    console.log('❌ 用户信息检查异常:', e.message);
  }
  
  // 2. 获取用户的所有日报
  console.log('\n2. 获取用户的所有日报:');
  try {
    const listResponse = await fetch('/api/v1/daily-report/legacy/my-reports', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      }
    });
    
    if (listResponse.ok) {
      const listData = await listResponse.json();
      const reports = listData.items || [];
      console.log('用户日报数量:', reports.length);
      
      if (reports.length > 0) {
        console.log('日报列表:');
        reports.forEach((report, index) => {
          console.log(`  ${index + 1}. ID:${report.id} 日期:${report.report_date} 状态:${report.status} 员工ID:${report.employee_id}`);
        });
        
        // 3. 检查日报ID=10是否存在
        console.log('\n3. 检查日报ID=10:');
        const targetReport = reports.find(r => r.id === 10);
        
        if (targetReport) {
          console.log('找到日报ID=10:', targetReport);
          console.log('日报所属员工ID:', targetReport.employee_id);
          console.log('当前用户工号:', userData.data.username);
          console.log('权限匹配:', targetReport.employee_id === userData.data.username ? '✅ 匹配' : '❌ 不匹配');
        } else {
          console.log('❌ 日报ID=10不存在于当前用户的日报列表中');
          console.log('这解释了403错误的原因');
        }
      } else {
        console.log('❌ 用户没有任何日报数据');
      }
    } else {
      console.log('❌ 获取日报列表失败:', listResponse.status);
    }
  } catch (e) {
    console.log('❌ 日报列表检查异常:', e.message);
  }
  
  // 4. 尝试访问存在的日报
  console.log('\n4. 尝试访问存在的日报:');
  if (reports && reports.length > 0) {
    const validReport = reports[0];
    console.log(`尝试访问日报ID=${validReport.id}:`);
    
    try {
      const detailResponse = await fetch(`/api/v1/daily-report/legacy/my-reports/${validReport.id}`, {
        headers: {
          'Authorization': 'Bearer ' + token,
          'Content-Type': 'application/json'
        }
      });
      
      console.log(`日报ID=${validReport.id}访问状态:`, detailResponse.status);
      
      if (detailResponse.ok) {
        const detailData = await detailResponse.json();
        console.log('✅ 成功访问有效日报:', detailData.id);
      } else {
        const errorText = await detailResponse.text();
        console.log('❌ 访问有效日报失败:', detailResponse.status, errorText);
      }
    } catch (e) {
      console.log('❌ 访问有效日报异常:', e.message);
    }
  }
  
  // 5. 分析结果
  console.log('\n5. 问题诊断结论:');
  console.log('403 Forbidden错误的可能原因:');
  console.log('A. 日报ID=10不属于当前用户');
  console.log('B. 权限验证逻辑错误');
  console.log('C. 用户角色权限不足');
  
  console.log('\n建议解决方案:');
  console.log('1. 使用有效的日报ID进行测试');
  console.log('2. 检查日报和用户的对应关系');
  console.log('3. 验证权限验证逻辑');
  
  console.log('\n=== 权限诊断完成 ===');
}

// 运行诊断
diagnosePermissionIssue();