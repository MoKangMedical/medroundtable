// MedRoundTable 用户系统集成模块
// 提供用户认证、历史记录保存、反馈收集等功能

class MedRoundTableUser {
    constructor() {
        this.API_BASE = window.location.hostname === 'localhost' 
            ? 'http://localhost:8000' 
            : 'https://mia-rating-ownership-downloads.trycloudflare.com';
        this.token = localStorage.getItem('mrt_token');
        this.user = JSON.parse(localStorage.getItem('mrt_user') || 'null');
        this.currentSessionId = null;
    }

    // ============ 认证相关 ============
    
    isLoggedIn() {
        return !!this.token;
    }

    getAuthHeaders() {
        return this.token ? { 'Authorization': `Bearer ${this.token}` } : {};
    }

    async register(name, email, password, institution = '') {
        try {
            const response = await fetch(`${this.API_BASE}/api/v1/user/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password, institution })
            });

            if (response.ok) {
                const data = await response.json();
                this.token = data.access_token;
                this.user = data.user;
                this._saveSession();
                return { success: true, user: data.user };
            } else {
                const error = await response.json();
                return { success: false, error: error.detail };
            }
        } catch (err) {
            return { success: false, error: '网络错误' };
        }
    }

    async login(email, password) {
        try {
            const response = await fetch(`${this.API_BASE}/api/v1/user/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (response.ok) {
                const data = await response.json();
                this.token = data.access_token;
                this.user = data.user;
                this._saveSession();
                return { success: true, user: data.user };
            } else {
                const error = await response.json();
                return { success: false, error: error.detail };
            }
        } catch (err) {
            return { success: false, error: '网络错误' };
        }
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('mrt_token');
        localStorage.removeItem('mrt_user');
    }

    _saveSession() {
        localStorage.setItem('mrt_token', this.token);
        localStorage.setItem('mrt_user', JSON.stringify(this.user));
    }

    // ============ 历史记录相关 ============

    async saveSession(sessionData) {
        if (!this.isLoggedIn()) {
            console.log('用户未登录，跳过保存历史记录');
            return { success: false, error: '未登录' };
        }

        try {
            const response = await fetch(`${this.API_BASE}/api/v1/user/history`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify(sessionData)
            });

            if (response.ok) {
                return { success: true };
            } else {
                const error = await response.json();
                return { success: false, error: error.detail };
            }
        } catch (err) {
            return { success: false, error: '网络错误' };
        }
    }

    async getHistory(page = 1, perPage = 10, options = {}) {
        if (!this.isLoggedIn()) {
            return { success: false, error: '未登录', data: [] };
        }

        try {
            const params = new URLSearchParams({
                page: page.toString(),
                per_page: perPage.toString(),
                ...(options.favoritesOnly ? { favorites_only: 'true' } : {}),
                ...(options.search ? { search: options.search } : {})
            });

            const response = await fetch(`${this.API_BASE}/api/v1/user/history?${params}`, {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                return { success: true, data };
            } else {
                return { success: false, error: '获取失败', data: [] };
            }
        } catch (err) {
            return { success: false, error: '网络错误', data: [] };
        }
    }

    async toggleFavorite(sessionId) {
        if (!this.isLoggedIn()) return { success: false };

        try {
            const response = await fetch(`${this.API_BASE}/api/v1/user/history/${sessionId}/favorite`, {
                method: 'PUT',
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                return { success: true, isFavorite: data.is_favorite };
            }
        } catch (err) {
            console.error('Toggle favorite failed:', err);
        }
        return { success: false };
    }

    // ============ 反馈相关 ============

    async submitFeedback(feedbackData) {
        try {
            const headers = { 'Content-Type': 'application/json' };
            if (this.isLoggedIn()) {
                headers['Authorization'] = `Bearer ${this.token}`;
            }

            const response = await fetch(`${this.API_BASE}/api/v1/user/feedback`, {
                method: 'POST',
                headers,
                body: JSON.stringify(feedbackData)
            });

            if (response.ok) {
                return { success: true };
            } else {
                const error = await response.json();
                return { success: false, error: error.detail };
            }
        } catch (err) {
            return { success: false, error: '网络错误' };
        }
    }

    // ============ 统计相关 ============

    async getUserStats() {
        if (!this.isLoggedIn()) {
            return { success: false, error: '未登录' };
        }

        try {
            const response = await fetch(`${this.API_BASE}/api/v1/user/stats`, {
                headers: this.getAuthHeaders()
            });

            if (response.ok) {
                const data = await response.json();
                return { success: true, data };
            }
        } catch (err) {
            console.error('Get stats failed:', err);
        }
        return { success: false };
    }

    // ============ UI 辅助方法 ============

    createLoginModal() {
        const modal = document.createElement('div');
        modal.id = 'user-auth-modal';
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center';
        modal.innerHTML = `
            <div class="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 p-6">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-xl font-bold text-gray-800">用户登录</h3>
                    <button onclick="document.getElementById('user-auth-modal').remove()" class="text-gray-400 hover:text-gray-600">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div id="auth-tabs" class="flex border-b mb-4">
                    <button class="flex-1 py-2 text-blue-600 border-b-2 border-blue-600 font-medium" data-tab="login">登录</button>
                    <button class="flex-1 py-2 text-gray-500 hover:text-gray-700" data-tab="register">注册</button>
                </div>
                <div id="login-form">
                    <input type="email" id="auth-email" placeholder="邮箱" class="w-full px-4 py-2 border rounded-lg mb-3">
                    <input type="password" id="auth-password" placeholder="密码" class="w-full px-4 py-2 border rounded-lg mb-4">
                    <button id="auth-submit-btn" class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
                        登录
                    </button>
                </div>
                <div id="register-form" class="hidden">
                    <input type="text" id="reg-name" placeholder="姓名" class="w-full px-4 py-2 border rounded-lg mb-3">
                    <input type="email" id="reg-email" placeholder="邮箱" class="w-full px-4 py-2 border rounded-lg mb-3">
                    <input type="password" id="reg-password" placeholder="密码（至少6位）" class="w-full px-4 py-2 border rounded-lg mb-3">
                    <input type="text" id="reg-institution" placeholder="机构（可选）" class="w-full px-4 py-2 border rounded-lg mb-4">
                    <button id="reg-submit-btn" class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
                        注册
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // 标签切换
        modal.querySelectorAll('#auth-tabs button').forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.dataset.tab;
                modal.querySelectorAll('#auth-tabs button').forEach(b => {
                    b.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600', 'font-medium');
                    b.classList.add('text-gray-500');
                });
                btn.classList.add('text-blue-600', 'border-b-2', 'border-blue-600', 'font-medium');
                btn.classList.remove('text-gray-500');
                
                modal.querySelector('#login-form').classList.toggle('hidden', tab !== 'login');
                modal.querySelector('#register-form').classList.toggle('hidden', tab !== 'register');
            });
        });

        // 登录提交
        modal.querySelector('#auth-submit-btn').addEventListener('click', async () => {
            const email = modal.querySelector('#auth-email').value;
            const password = modal.querySelector('#auth-password').value;
            
            const result = await this.login(email, password);
            if (result.success) {
                modal.remove();
                this.showToast('登录成功', 'success');
                this.updateHeaderUI();
            } else {
                this.showToast(result.error || '登录失败', 'error');
            }
        });

        // 注册提交
        modal.querySelector('#reg-submit-btn').addEventListener('click', async () => {
            const name = modal.querySelector('#reg-name').value;
            const email = modal.querySelector('#reg-email').value;
            const password = modal.querySelector('#reg-password').value;
            const institution = modal.querySelector('#reg-institution').value;
            
            if (!name || !email || !password) {
                this.showToast('请填写完整信息', 'error');
                return;
            }
            
            const result = await this.register(name, email, password, institution);
            if (result.success) {
                modal.remove();
                this.showToast('注册成功', 'success');
                this.updateHeaderUI();
            } else {
                this.showToast(result.error || '注册失败', 'error');
            }
        });
    }

    updateHeaderUI() {
        const header = document.querySelector('header .max-w-7xl');
        if (!header) return;

        // 查找或创建用户区域
        let userArea = header.querySelector('#user-area');
        if (!userArea) {
            userArea = document.createElement('div');
            userArea.id = 'user-area';
            header.appendChild(userArea);
        }

        if (this.isLoggedIn()) {
            userArea.innerHTML = `
                <div class="flex items-center gap-3">
                    <span class="text-white text-sm">${this.user.name}</span>
                    <button id="user-menu-btn" class="text-white hover:text-gray-200">
                        <i class="fas fa-user-circle text-2xl"></i>
                    </button>
                </div>
            `;
            
            userArea.querySelector('#user-menu-btn').addEventListener('click', () => {
                this.showUserMenu();
            });
        } else {
            userArea.innerHTML = `
                <button onclick="window.mrtUser.createLoginModal()" class="px-4 py-2 bg-white/20 rounded-lg hover:bg-white/30 transition text-sm text-white">
                    <i class="fas fa-user mr-2"></i>登录
                </button>
            `;
        }
    }

    showUserMenu() {
        // 移除现有菜单
        const existing = document.getElementById('user-dropdown');
        if (existing) existing.remove();

        const menu = document.createElement('div');
        menu.id = 'user-dropdown';
        menu.className = 'absolute right-4 top-16 bg-white rounded-lg shadow-xl py-2 z-50 min-w-[150px]';
        menu.innerHTML = `
            <div class="px-4 py-2 border-b">
                <p class="font-medium text-gray-800">${this.user.name}</p>
                <p class="text-xs text-gray-500">${this.user.email}</p>
            </div>
            <a href="/feedback-v2.html" class="block px-4 py-2 hover:bg-gray-100 text-gray-700">
                <i class="fas fa-comment-dots mr-2"></i>反馈
            </a>
            <button onclick="window.mrtUser.logout(); window.mrtUser.updateHeaderUI(); document.getElementById('user-dropdown').remove();" 
                class="w-full text-left px-4 py-2 hover:bg-gray-100 text-red-600">
                <i class="fas fa-sign-out-alt mr-2"></i>退出
            </button>
        `;

        document.body.appendChild(menu);

        // 点击外部关闭
        setTimeout(() => {
            document.addEventListener('click', function close(e) {
                if (!menu.contains(e.target)) {
                    menu.remove();
                    document.removeEventListener('click', close);
                }
            });
        }, 100);
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg text-white ${
            type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500'
        }`;
        toast.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check' : type === 'error' ? 'fa-exclamation' : 'fa-info'} mr-2"></i>${message}`;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // ============ 自动保存功能 ============

    async autoSaveCurrentSession(sessionId, sessionData) {
        if (!this.isLoggedIn() || !sessionId) return;
        
        this.currentSessionId = sessionId;
        
        // 准备保存数据
        const data = {
            session_id: sessionId,
            title: sessionData.title || '未命名会话',
            clinical_question: sessionData.clinical_question || '',
            study_type: sessionData.study_type || null,
            messages: sessionData.messages || [],
            study_design: sessionData.study_design || null,
            crf_template: sessionData.crf_template || null,
            analysis_plan: sessionData.analysis_plan || null
        };

        await this.saveSession(data);
    }
}

// 初始化全局实例
window.mrtUser = new MedRoundTableUser();

// 页面加载完成后更新UI
document.addEventListener('DOMContentLoaded', () => {
    window.mrtUser.updateHeaderUI();
});
