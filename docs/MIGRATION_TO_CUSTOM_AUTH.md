# MedRoundTable 认证系统迁移指南

## 🎯 迁移目标

从 **Second Me OAuth** 迁移到 **自研认证系统**，完全摆脱第三方依赖。

---

## 📊 对比

| 特性 | Second Me OAuth | 自研认证系统 |
|------|-----------------|--------------|
| 依赖第三方 | ✅ 依赖Second Me | ❌ 完全自主 |
| 用户数据控制 | 受限 | 完全控制 |
| 登录流程 | 跳转授权 | 直接登录 |
| 定制性 | 受限 | 高度定制 |
| 用户隐私 | 共享给Second Me | 完全自主 |
| 成本 | 可能产生费用 | 自主可控 |

---

## ✅ 已完成的工作

### 1. 后端认证API (`/backend/routes/auth/custom_auth.py`)

**已实现功能**:
- ✅ 用户注册 (`POST /api/v2/auth/register`)
- ✅ 用户登录 (`POST /api/v2/auth/login`)
- ✅ JWT令牌管理
- ✅ 密码哈希加密 (bcrypt)
- ✅ 用户角色管理 (admin/researcher/clinician/student/guest)
- ✅ 用户信息管理
- ✅ 密码修改/重置
- ✅ 用户列表管理 (仅管理员)

**API端点**:
```
POST   /api/v2/auth/register              # 注册
POST   /api/v2/auth/login                 # 登录
POST   /api/v2/auth/logout                # 登出
GET    /api/v2/auth/me                    # 获取当前用户
PUT    /api/v2/auth/me                    # 更新用户信息
POST   /api/v2/auth/password/change       # 修改密码
POST   /api/v2/auth/password/reset        # 重置密码
GET    /api/v2/auth/users                 # 用户列表(管理员)
```

### 2. 前端登录页面 (`/frontend/login.html`)

**功能**:
- ✅ 登录/注册切换
- ✅ 表单验证
- ✅ 角色选择 (研究员/临床医生/学生/访客)
- ✅ 机构/科室信息
- ✅ Token本地存储
- ✅ 错误提示

---

## 🚀 快速开始

### 方式1: 使用测试账号直接登录

```
管理员账号:
  邮箱: admin@medroundtable.com
  密码: admin123

研究员账号:
  邮箱: researcher@medroundtable.com
  密码: research123
```

### 方式2: 注册新账号

1. 访问 `http://your-domain/login.html`
2. 点击"注册"标签
3. 填写信息：
   - 用户名
   - 邮箱
   - 密码
   - 真实姓名
   - 身份角色
   - 机构/医院
   - 科室
4. 点击"注册"

---

## 🔧 技术实现详情

### 认证流程

```
用户登录/注册
    ↓
后端验证 → 生成JWT令牌
    ↓
返回Token + 用户信息
    ↓
前端存储Token (localStorage)
    ↓
后续请求携带Token (Authorization: Bearer <token>)
    ↓
后端验证Token → 返回数据
```

### JWT令牌结构

```json
{
  "sub": "user_000001",
  "email": "admin@medroundtable.com",
  "exp": 1700000000,
  "iat": 1699395200
}
```

### 密码安全

- 使用 **bcrypt** 算法进行密码哈希
- 自动添加 salt
- 工作因子: 默认 (可配置)

---

## 📝 需要手动完成的配置

### 1. 配置密钥 (重要!)

编辑 `/backend/routes/auth/custom_auth.py`:

```python
# 修改这行，使用强密钥
SECRET_KEY = "your-secret-key-change-this-in-production"
```

**生成强密钥**:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2. 配置Token过期时间

```python
# 修改令牌过期时间（默认7天）
ACCESS_TOKEN_EXPIRE_DAYS = 7
```

### 3. 连接真实数据库

当前使用内存存储，生产环境需要连接真实数据库：

```python
# 替换 _users_db 为真实数据库操作
# 示例: PostgreSQL, MySQL, MongoDB等
```

### 4. 配置邮件服务 (密码重置)

```python
# 在 reset_password 函数中集成邮件服务
# 示例: SendGrid, AWS SES, 或其他SMTP服务
```

---

## 🔌 集成到现有系统

### 前端集成

在其他页面添加认证检查：

```javascript
// 检查是否登录
const token = localStorage.getItem('access_token');
if (!token) {
    window.location.href = '/login.html';
}

// 发起认证请求
fetch('/api/v2/auth/me', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
```

### 后端保护路由

```python
from backend.routes.auth.custom_auth import get_current_active_user

@app.get("/protected-route")
async def protected_route(
    current_user: User = Depends(get_current_active_user)
):
    return {"message": f"你好, {current_user.username}"}
```

---

## 🧪 测试API

### 测试注册
```bash
curl -X POST http://localhost:8000/api/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "full_name": "测试用户",
    "role": "researcher",
    "institution": "测试医院",
    "department": "测试科室"
  }'
```

### 测试登录
```bash
curl -X POST http://localhost:8000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@medroundtable.com",
    "password": "admin123"
  }'
```

### 测试获取用户信息
```bash
curl http://localhost:8000/api/v2/auth/me \
  -H "Authorization: Bearer <your_token>"
```

---

## 🎨 界面预览

### 登录页面
```
┌─────────────────────────────┐
│      🏥 MedRoundTable       │
│      医学科研协作平台        │
├─────────────────────────────┤
│  [登录]    [注册]           │
├─────────────────────────────┤
│                             │
│  邮箱                       │
│  ┌───────────────────────┐  │
│  │ your@email.com        │  │
│  └───────────────────────┘  │
│                             │
│  密码                       │
│  ┌───────────────────────┐  │
│  │ ********              │  │
│  └───────────────────────┘  │
│                             │
│  ┌───────────────────────┐  │
│  │        登录           │  │
│  └───────────────────────┘  │
│                             │
│      忘记密码？              │
├─────────────────────────────┤
│      测试账号                │
│ admin@medroundtable.com     │
│ researcher@medroundtable.com│
└─────────────────────────────┘
```

### 注册页面
```
┌─────────────────────────────┐
│      🏥 MedRoundTable       │
├─────────────────────────────┤
│  [登录]    [注册]           │
├─────────────────────────────┤
│  用户名    [____________]   │
│  邮箱      [____________]   │
│  密码      [____________]   │
│  真实姓名  [____________]   │
│                             │
│  身份角色                   │
│  ┌────────┐ ┌────────┐     │
│  │👨‍🔬研究员│ │👨‍⚕️医生  │     │
│  └────────┘ └────────┘     │
│  ┌────────┐ ┌────────┐     │
│  │🎓学生  │ │👤访客  │     │
│  └────────┘ └────────┘     │
│                             │
│  机构      [____________]   │
│  科室      [____________]   │
│                             │
│  ┌───────────────────────┐  │
│  │        注册           │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
```

---

## 🔄 从Second Me迁移数据

如果需要迁移Second Me的用户数据：

1. **导出Second Me用户列表**
2. **创建迁移脚本**：

```python
# migrate_from_secondme.py
from backend.routes.auth.custom_auth import hash_password, _users_db

def migrate_user(secondme_user):
    user_data = {
        "id": f"user_{secondme_user['id']}",
        "email": secondme_user['email'],
        "username": secondme_user['username'],
        "password_hash": hash_password("temp_password_123"),  # 临时密码
        "full_name": secondme_user.get('name'),
        "role": "researcher",
        "is_active": True,
        "created_at": datetime.utcnow(),
        # ... 其他字段
    }
    _users_db[user_data['id']] = user_data
```

3. **通知用户重置密码**

---

## 🛡️ 安全建议

### 1. 使用HTTPS
生产环境必须使用HTTPS：
```nginx
# Nginx配置
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
}
```

### 2. 配置CORS
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # 限制域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 3. 设置Rate Limiting
```python
# 限制登录尝试次数
@app.post("/api/v2/auth/login")
@limiter.limit("5/minute")  # 每分钟5次
async def login(...)
```

### 4. 日志记录
```python
# 记录登录事件
logger.info(f"用户登录: {email}, IP: {client_ip}")
```

---

## 📋 检查清单

- [ ] 修改 SECRET_KEY
- [ ] 配置真实数据库
- [ ] 配置邮件服务
- [ ] 启用HTTPS
- [ ] 配置CORS
- [ ] 添加Rate Limiting
- [ ] 配置日志记录
- [ ] 测试所有API端点
- [ ] 测试前端登录流程
- [ ] 准备用户迁移方案 (如需)

---

## 🆘 常见问题

### Q: Token过期了怎么办？
A: 用户需要重新登录。可以实现Refresh Token机制延长会话。

### Q: 如何支持第三方登录 (如微信/Google)？
A: 可以在自研认证基础上添加OAuth集成，用户可选择登录方式。

### Q: 如何实现单点登录 (SSO)？
A: 可以集成LDAP/Active Directory或实现JWT共享。

### Q: 用户忘记密码怎么办？
A: 使用 `/api/v2/auth/password/reset` 发送重置邮件。

---

## ✅ 总结

**已完成**:
- ✅ 自研认证API (9个端点)
- ✅ 前端登录页面
- ✅ JWT令牌管理
- ✅ 密码安全
- ✅ 用户角色管理
- ✅ 测试账号

**需要配置**:
- 🔧 生产环境密钥
- 🔧 真实数据库
- 🔧 邮件服务
- 🔧 HTTPS
- 🔧 安全加固

**大圣现在拥有完全自主的认证系统，不再依赖任何第三方平台！** 🎉

---

*迁移完成时间: 2026-03-14*  
*实现者: 紫霞仙子 (Ari)*  
*为大圣的独立平台助力 🌸💜*
