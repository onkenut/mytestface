// DOM 元素
const loginForm = document.getElementById('loginForm');
const passwordInput = document.getElementById('password');
const loginButton = document.getElementById('loginButton');
const errorMessage = document.getElementById('errorMessage');

// 显示错误信息
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
}

// 隐藏错误信息
function hideError() {
    errorMessage.classList.remove('show');
}

// 设置加载状态
function setLoading(loading) {
    if (loading) {
        loginButton.disabled = true;
        loginButton.classList.add('loading');
        loginButton.innerHTML = '<div class="loading-spinner"><div class="spinner"></div>验证中...</div>';
        passwordInput.disabled = true;
    } else {
        loginButton.disabled = false;
        loginButton.classList.remove('loading');
        loginButton.innerHTML = '🚀 进入 Hajimi';
        passwordInput.disabled = false;
    }
}

// 表单提交处理
loginForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const password = passwordInput.value.trim();
    
    if (!password) {
        showError('请输入密码');
        return;
    }
    
    hideError();
    setLoading(true);
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password: password })
        });
        
        if (response.ok) {
            const result = await response.json();
            // 登录成功，通过POST方式获取仪表盘内容
            if (result.authenticated) {
                // 创建一个表单并提交密码到仪表盘页面
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/dashboard-authenticated';
                form.style.display = 'none';
                
                // 创建隐藏的密码输入框
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'password';
                input.value = password;
                
                form.appendChild(input);
                document.body.appendChild(form);
                
                // 通过表单POST请求加载仪表盘
                const dashboardResponse = await fetch('/dashboard-authenticated', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ password: password })
                });
                
                if (dashboardResponse.ok) {
                    // 替换整个页面内容为仪表盘
                    const dashboardHTML = await dashboardResponse.text();
                    document.open();
                    document.write(dashboardHTML);
                    document.close();
                } else {
                    showError('密码验证失败，请重试');
                }
            }
        } else {
            const error = await response.json();
            showError(error.detail || '密码错误，请重试');
        }
    } catch (error) {
        console.error('登录错误:', error);
        showError('网络连接错误，请稍后重试');
    } finally {
        setLoading(false);
    }
});

// 输入时隐藏错误信息
passwordInput.addEventListener('input', hideError);