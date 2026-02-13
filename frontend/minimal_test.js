// 最小化测试代码 - 避免语法错误
async function testEditPage() {
  console.log('开始测试编辑页面...');
  
  const token = localStorage.getItem('token');
  console.log('Token存在:', !!token);
  
  try {
    const response = await fetch('/api/v1/daily-report/legacy/my-reports/12/', {
      headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('API状态:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('成功:', data.id);
    } else {
      const error = await response.text();
      console.log('失败:', response.status, error);
    }
  } catch (e) {
    console.log('异常:', e.message);
  }
}

testEditPage();