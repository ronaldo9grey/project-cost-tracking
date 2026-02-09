// 测试保存功能的API调用
async function testSaveFunction() {
  console.log('=== 测试保存功能API调用 ===');
  
  const token = localStorage.getItem('token');
  console.log('Token存在:', !!token);
  
  // 1. 测试GET获取日报（应该成功）
  console.log('\n1. 测试GET获取日报:');
  try {
    const getResponse = await fetch('/api/v1/daily-report/legacy/my-reports/10', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('GET状态:', getResponse.status);
    if (getResponse.ok) {
      const reportData = await getResponse.json();
      console.log('✅ GET成功，日报ID:', reportData.id);
    } else {
      const errorText = await getResponse.text();
      console.log('❌ GET失败:', getResponse.status, errorText);
    }
  } catch (e) {
    console.log('❌ GET异常:', e.message);
  }
  
  // 2. 测试PUT更新日报（可能失败）
  console.log('\n2. 测试PUT更新日报:');
  try {
    const putData = {
      report_date: "2026-01-15",
      employee_id: "0001",
      employee_name: "admin",
      tomorrow_plan: "测试保存功能",
      planned_hours: 8.0
    };
    
    const putResponse = await fetch('/api/v1/daily-report/legacy/my-reports/10', {
      method: 'PUT',
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(putData)
    });
    
    console.log('PUT状态:', putResponse.status);
    
    if (putResponse.ok) {
      const putResult = await putResponse.json();
      console.log('✅ PUT成功:', putResult.id);
    } else {
      const errorText = await putResponse.text();
      console.log('❌ PUT失败:', putResponse.status, errorText);
      
      // 尝试解析错误
      try {
        const errorJson = JSON.parse(errorText);
        console.log('错误详情:', errorJson.detail || errorJson.message);
      } catch (e) {
        console.log('错误文本:', errorText);
      }
    }
  } catch (e) {
    console.log('❌ PUT异常:', e.message);
  }
  
  // 3. 分析可能的原因
  console.log('\n3. 分析PUT 401错误的原因:');
  console.log('A. URL格式: 已修复（移除末尾斜杠）');
  console.log('B. 权限验证: 可能问题');
  console.log('C. 用户信息: 可能不匹配');
  console.log('D. 数据格式: 可能格式错误');
  
  // 4. 检查用户信息
  console.log('\n4. 检查用户信息:');
  try {
    const userResponse = await fetch('/api/v1/auth/users/me', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      }
    });
    
    if (userResponse.ok) {
      const userData = await userResponse.json();
      console.log('用户信息:', userData.data);
      console.log('PUT数据中的employee_id:', '0001');
      console.log('用户信息中的username:', userData.data.username);
      console.log('匹配结果:', userData.data.username === '0001' ? '✅ 匹配' : '❌ 不匹配');
    }
  } catch (e) {
    console.log('❌ 用户信息检查异常:', e.message);
  }
  
  console.log('\n=== 保存功能测试完成 ===');
}

// 运行测试
testSaveFunction();