// 详细分析token问题
async function detailedTokenAnalysis() {
  console.log('=== 详细分析token问题 ===');
  
  // 1. 检查token基本信息
  const token = localStorage.getItem('token');
  console.log('1. Token基本信息:');
  console.log('  Token存在:', !!token);
  console.log('  Token长度:', token ? token.length : 0);
  console.log('  Token前缀:', token ? token.substring(0, 20) + '...' : 'null');
  
  // 2. 解码JWT内容
  if (token) {
    console.log('\n2. JWT内容分析:');
    try {
      const parts = token.split('.');
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]));
        console.log('  JWT payload:', payload);
        console.log('  sub字段:', payload.sub);
        console.log('  过期时间:', payload.exp ? new Date(payload.exp * 1000).toISOString() : '无过期时间');
        console.log('  当前时间:', new Date().toISOString());
        
        const now = Math.floor(Date.now() / 1000);
        const isExpired = payload.exp && payload.exp < now;
        console.log('  是否过期:', isExpired);
        
        if (isExpired) {
          console.log('  ⚠️  Token已过期!');
        }
      } else {
        console.log('  ❌ Token格式错误: 不是有效的JWT');
      }
    } catch (e) {
      console.log('  ❌ JWT解码失败:', e.message);
    }
  }
  
  // 3. 测试其他API调用
  console.log('\n3. 测试其他API调用:');
  
  // 3.1 测试用户信息API
  try {
    console.log('  测试用户信息API...');
    const userResponse = await fetch('/api/v1/auth/users/me', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('    用户信息API状态:', userResponse.status);
    
    if (userResponse.ok) {
      const userData = await userResponse.json();
      console.log('    ✅ 用户信息API成功:', userData.data.username);
    } else {
      const errorText = await userResponse.text();
      console.log('    ❌ 用户信息API失败:', userResponse.status, errorText);
    }
  } catch (e) {
    console.log('    ❌ 用户信息API异常:', e.message);
  }
  
  // 3.2 测试日报列表API
  try {
    console.log('  测试日报列表API...');
    const listResponse = await fetch('/api/v1/daily-report/legacy/my-reports', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('    日报列表API状态:', listResponse.status);
    
    if (listResponse.ok) {
      const listData = await listResponse.json();
      console.log('    ✅ 日报列表API成功，记录数:', listData.items ? listData.items.length : 0);
    } else {
      const errorText = await listResponse.text();
      console.log('    ❌ 日报列表API失败:', listResponse.status, errorText);
    }
  } catch (e) {
    console.log('    ❌ 日报列表API异常:', e.message);
  }
  
  // 4. 结论分析
  console.log('\n4. 问题分析:');
  console.log('基于以上测试结果:');
  
  if (token) {
    const parts = token.split('.');
    if (parts.length === 3) {
      try {
        const payload = JSON.parse(atob(parts[1]));
        const now = Math.floor(Date.now() / 1000);
        const isExpired = payload.exp && payload.exp < now;
        
        if (isExpired) {
          console.log('  🔍 问题诊断: Token已过期');
          console.log('  🔧 解决方案: 重新登录获取新token');
        } else {
          console.log('  🔍 问题诊断: Token未过期但详情API失败');
          console.log('  🔧 可能原因: 页面跳转时token状态不一致');
          console.log('  🔧 解决方案: 刷新页面或重新登录');
        }
      } catch (e) {
        console.log('  🔍 问题诊断: Token格式错误');
        console.log('  🔧 解决方案: 清理localStorage并重新登录');
      }
    }
  }
  
  console.log('\n=== 详细分析完成 ===');
}

// 运行分析
detailedTokenAnalysis();