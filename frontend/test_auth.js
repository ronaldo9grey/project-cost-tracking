// 完整的认证流程测试
// 在浏览器控制台中运行此代码

async function testAuthFlow() {
    console.log('=== 开始认证流程测试 ===');
    
    try {
        // 1. 清理所有存储
        localStorage.removeItem('token');
        localStorage.removeItem('currentUser');
        console.log('1. 清理本地存储完成');
        
        // 2. 执行登录
        console.log('2. 开始登录...');
        
        // 模拟登录请求
        const formData = new URLSearchParams();
        formData.append('username', 'admin');
        formData.append('password', '123456');
        
        const loginResponse = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });
        
        console.log('登录响应状态:', loginResponse.status);
        
        if (loginResponse.ok) {
            const loginData = await loginResponse.json();
            console.log('登录成功:', loginData);
            
            if (loginData.code === 200 && loginData.data?.access_token) {
                const token = loginData.data.access_token;
                
                // 3. 保存token
                localStorage.setItem('token', token);
                console.log('3. Token保存完成:', token.substring(0, 20) + '...');
                
                // 4. 测试获取日报列表
                console.log('4. 测试获取日报列表...');
                const listResponse = await fetch('/api/v1/daily-report/legacy/my-reports', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                console.log('列表请求状态:', listResponse.status);
                
                if (listResponse.ok) {
                    const listData = await listResponse.json();
                    console.log('列表获取成功:', listData);
                    
                    // 5. 如果有日报，测试获取详情
                    if (listData.items && listData.items.length > 0) {
                        const firstReport = listData.items[0];
                        console.log('5. 测试获取日报详情 (ID:', firstReport.id, ')...');
                        
                        const detailResponse = await fetch(`/api/v1/daily-report/legacy/my-reports/${firstReport.id}/`, {
                            headers: {
                                'Authorization': `Bearer ${token}`
                            }
                        });
                        
                        console.log('详情请求状态:', detailResponse.status);
                        
                        if (detailResponse.ok) {
                            const detailData = await detailResponse.json();
                            console.log('详情获取成功:', detailData);
                            console.log('✅ 完整认证流程测试成功！');
                        } else {
                            const errorText = await detailResponse.text();
                            console.error('❌ 详情获取失败:', detailResponse.status, errorText);
                        }
                    } else {
                        console.log('5. 没有找到日报数据，跳过详情测试');
                    }
                } else {
                    const errorText = await listResponse.text();
                    console.error('❌ 列表获取失败:', listResponse.status, errorText);
                }
            } else {
                console.error('❌ 登录响应格式错误:', loginData);
            }
        } else {
            const errorText = await loginResponse.text();
            console.error('❌ 登录失败:', loginResponse.status, errorText);
        }
        
    } catch (error) {
        console.error('❌ 测试过程出错:', error);
    }
}

// 运行测试
testAuthFlow();