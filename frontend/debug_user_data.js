// 用户数据分析调试工具 - 可直接在Chrome控制台中运行

async function debugUserData() {
  console.log('=== 开始用户数据分析 ===');
  
  // 1. 检查localStorage中的数据
  console.log('\n1. 检查localStorage中的数据:');
  const token = localStorage.getItem('token');
  const userInfo = localStorage.getItem('currentUser');
  
  console.log('Token存在:', !!token);
  console.log('用户信息存在:', !!userInfo);
  
  if (userInfo) {
    try {
      const parsedUserInfo = JSON.parse(userInfo);
      console.log('localStorage中的用户信息:', parsedUserInfo);
    } catch (e) {
      console.log('解析用户信息失败:', e);
    }
  }
  
  // 2. 调用后端API获取真实用户信息
  console.log('\n2. 调用后端API获取真实用户信息:');
  
  try {
    const userResponse = await fetch('/api/v1/auth/users/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    console.log('用户信息API状态:', userResponse.status);
    
    if (userResponse.ok) {
      const userData = await userResponse.json();
      console.log('后端返回的用户信息:', userData);
      
      const backendUserInfo = userData.data;
      console.log('后端用户信息详情:', {
        id: backendUserInfo.id,
        username: backendUserInfo.username,
        role_id: backendUserInfo.role_id
      });
      
      // 3. 检查JWT token内容
      console.log('\n3. 检查JWT token内容:');
      if (token) {
        try {
          const parts = token.split('.');
          if (parts.length === 3) {
            const payload = JSON.parse(atob(parts[1]));
            console.log('JWT payload:', payload);
            console.log('JWT sub字段:', payload.sub);
          }
        } catch (e) {
          console.log('JWT解码失败:', e);
        }
      }
      
      // 4. 检查日报数据
      console.log('\n4. 检查日报数据:');
      try {
        const reportsResponse = await fetch('/api/v1/daily-report/legacy/my-reports', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        console.log('日报列表API状态:', reportsResponse.status);
        
        if (reportsResponse.ok) {
          const reportsData = await reportsResponse.json();
          const reports = reportsData.items || [];
          console.log('日报数据数量:', reports.length);
          
          if (reports.length > 0) {
            const firstReport = reports[0];
            console.log('第一个日报的员工ID:', firstReport.employee_id);
            console.log('当前用户的工号:', backendUserInfo.username);
            console.log('权限匹配结果:', 
              backendUserInfo.username === firstReport.employee_id ? '✅ 匹配' : '❌ 不匹配');
              
            // 5. 详细权限分析
            console.log('\n5. 详细权限分析:');
            console.log('日报数据示例:', {
              id: firstReport.id,
              employee_id: firstReport.employee_id,
              employee_name: firstReport.employee_name,
              status: firstReport.status
            });
            
            console.log('用户信息示例:', {
              id: backendUserInfo.id,
              username: backendUserInfo.username,
              role_id: backendUserInfo.role_id
            });
          }
        } else {
          console.log('❌ 日报列表获取失败:', reportsResponse.status);
          const errorText = await reportsResponse.text();
          console.log('错误信息:', errorText);
        }
      } catch (e) {
        console.log('❌ 日报数据检查异常:', e);
      }
      
      // 6. 问题诊断结论
      console.log('\n6. 问题诊断结论:');
      const username = backendUserInfo.username;
      const reports = reportsData?.items || [];
      
      if (reports.length > 0) {
        const firstReport = reports[0];
        if (username !== firstReport.employee_id) {
          console.log('❌ 发现权限验证问题:');
          console.log(`  - 当前登录用户工号: ${username}`);
          console.log(`  - 日报数据员工ID: ${firstReport.employee_id}`);
          console.log(`  - 原因: 用户 ${username} 没有日报数据，或者权限验证逻辑有误`);
          console.log('\n🔧 建议解决方案:');
          console.log('A. 检查当前用户是否有日报数据');
          console.log('B. 检查日报数据是否属于正确的用户');
          console.log('C. 检查权限验证逻辑');
        } else {
          console.log('✅ 权限验证正常');
        }
      } else {
        console.log('❌ 没有找到日报数据');
        console.log('可能原因: 当前用户没有日报记录');
      }
      
    } else {
      console.log('❌ 获取用户信息失败:', userResponse.status);
      const errorText = await userResponse.text();
      console.log('错误信息:', errorText);
    }
    
  } catch (e) {
    console.log('❌ 用户信息API调用异常:', e);
  }
  
  console.log('\n=== 用户数据分析完成 ===');
}

// 将函数暴露到全局作用域
if (typeof window !== 'undefined') {
  window.debugUserData = debugUserData;
}

// 自动运行
debugUserData();