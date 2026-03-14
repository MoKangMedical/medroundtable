# MedRoundTable 环境变量设置指南

## ⚠️ 必须设置的环境变量（部署后立即配置）

登录 [Zeabur Dashboard](https://zeabur.com) → 你的项目 → Environment Variables

### 核心配置（必需）

```env
# 数据库
DATABASE_URL=sqlite:///data/medroundtable.db

# 安全密钥（自动生成随机字符串）
SECRET_KEY=your_random_32_char_string_here

# CORS 配置
ALLOWED_ORIGINS=https://medroundtable-v2.vercel.app,https://medroundtable.zeabur.app
CORS_ORIGINS=https://medroundtable-v2.vercel.app,https://medroundtable.zeabur.app
```

### Second Me OAuth（必需 - 用于登录）

```env
SECONDME_API_BASE=https://api.mindverse.com/gate/lab
SECONDME_CLIENT_ID=从Second Me开发者平台获取
SECONDME_CLIENT_SECRET=从Second Me开发者平台获取
SECONDME_REDIRECT_URI=https://medroundtable.zeabur.app/api/auth/callback
```

**获取方式：**
1. 访问 https://go.second.me/developers
2. 创建新应用
3. 设置回调URL: `https://medroundtable.zeabur.app/api/auth/callback`
4. 复制 Client ID 和 Client Secret

### AI API Keys（推荐设置）

```env
# OpenAI (GPT-4)
OPENAI_API_KEY=sk-xxx

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-xxx

# DeepSeek
DEEPSEEK_API_KEY=sk-xxx

# Moonshot (Kimi)
MOONSHOT_API_KEY=xxx

# Zhipu AI (GLM)
ZHIPU_API_KEY=xxx
```

### 可选配置

```env
# Stripe支付（如需订阅功能）
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# 邮件服务
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# 监控
SENTRY_DSN=your_sentry_dsn
```

---

## 🚀 快速设置步骤

### 1. 生成 SECRET_KEY
```bash
openssl rand -hex 32
# 复制输出到 SECRET_KEY
```

### 2. 设置数据库（SQLite默认）
```env
DATABASE_URL=sqlite:///data/medroundtable.db
```

如需PostgreSQL：
```env
DATABASE_URL=postgresql://user:password@host:5432/medroundtable
```

### 3. 测试配置
部署后访问：
- 健康检查: `https://medroundtable.zeabur.app/health`
- API文档: `https://medroundtable.zeabur.app/docs`

---

## ❓ 常见问题

**Q: 环境变量设置后没有生效？**
A: Zeabur会自动重启服务，等待1-2分钟后刷新。

**Q: Second Me OAuth报错？**
A: 确保回调URL完全匹配，包括 https:// 和路径。

**Q: 数据库连接失败？**
A: 检查 DATABASE_URL 格式，SQLite路径应为相对路径。

---

## 📞 支持

- Zeabur文档: https://docs.zeabur.com
- Second Me API: https://api.mindverse.com/gate/lab
- 项目仓库: https://github.com/MoKangMedical/medroundtable
