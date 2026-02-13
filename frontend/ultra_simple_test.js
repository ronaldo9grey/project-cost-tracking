// 超简单测试 - 避免所有语法问题
async function testAPI() {
  console.log('开始测试API...');
  
  const token = localStorage.getItem('token');
  console.log('Token存在:', !!token);
  
  if (!token) {
    console.log('没有token，测试结束');
    return;
  }
  
  try {
    const response = await fetch('/api/v1/daily-report/legacy/my-reports/12/', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('API状态码:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('API调用成功! 日报ID:', data.id);
    } else {
      const errorText = await response.text();
      console.log('API调用失败! 状态码:', response.status, '错误:', errorText);
    }
  } catch (error) {
    console.log('API调用异常:', error.message);
  }
}

testAPI();