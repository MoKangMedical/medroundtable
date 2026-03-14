# MedRoundTable 环境变量检查清单

## 🔴 必需环境变量

| 变量名 | 用途 | 获取/生成方法 |
|--------|------|--------------|
| `PORT` | 服务端口 | 固定值：`8000` |
| `HOST` | 监听地址 | 固定值：`0.0.0.0` |
| `DEBUG` | 调试模式 | 生产环境设为 `false` |
| `SECRET_KEY` | JWT加密密钥 | 生成命令：`openssl rand -hex 32` |
| `DATABASE_URL` | 数据库连接 | SQLite: `sqlite:///data/medroundtable.db` |
| `ALLOWED_ORIGINS` | CORS白名单 | 格式：`https://前端地址1,https://前端地址2` |
| `CORS_ORIGINS` | CORS来源 | 同 `ALLOWED_ORIGINS` |

## 🟡 Second Me OAuth（推荐配置）

| 变量名 | 用途 | 获取方法 |
|--------|------|---------|
| `SECONDME_API_BASE` | Second Me API基础URL | 固定值：`https://api.mindverse.com/gate/lab` |
| `SECONDME_CLIENT_ID` | OAuth客户端ID | Second Me开发者中心创建应用后获取 |
| `SECONDME_CLIENT_SECRET` | OAuth客户端密钥 | Second Me开发者中心创建应用后获取 |
| `SECONDME_REDIRECT_URI` | OAuth回调地址 | 格式：`https://你的域名/api/auth/callback` |

## 🟢 AI API Keys（至少配置一个）

| 变量名 | 用途 | 获取地址 |
|--------|------|---------|
| `OPENAI_API_KEY` | OpenAI GPT模型 | https://platform.openai.com/api-keys |
| `ANTHROPIC_API_KEY` | Claude模型 | https://console.anthropic.com/settings/keys |
| `DEEPSEEK_API_KEY` | DeepSeek模型 | https://platform.deepseek.com/api_keys |
| `MOONSHOT_API_KEY` | Kimi模型 | https://platform.moonshot.cn/console/api-keys |
| `ZHIPU_API_KEY` | GLM模型 | https://open.bigmodel.cn/usercenter/apikeys |

## 🔵 可选环境变量

### 支付配置 (Stripe)
| 变量名 | 用途 | 获取地址 |
|--------|------|---------|
| `STRIPE_PUBLISHABLE_KEY` | 前端支付密钥 | https://dashboard.stripe.com/apikeys |
| `STRIPE_SECRET_KEY` | 后端支付密钥 | 同上 |
| `STRIPE_WEBHOOK_SECRET` | Webhook密钥 | Stripe Dashboard → Webhooks |

### 存储配置
| 变量名 | 用途 | 示例值 |
|--------|------|-------|
| `STORAGE_PROVIDER` | 存储提供商 | `local` / `oss` / `s3` |
| `STORAGE_ENDPOINT` | 存储端点 | `oss-cn-beijing.aliyuncs.com` |
| `STORAGE_BUCKET` | 存储桶名 | `medroundtable` |
| `STORAGE_ACCESS_KEY` | 访问密钥 | 从云服务商获取 |
| `STORAGE_SECRET_KEY` | 访问密钥 | 从云服务商获取 |

### 邮件配置
| 变量名 | 用途 | 示例值 |
|--------|------|-------|
| `SMTP_HOST` | SMTP服务器 | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP端口 | `587` |
| `SMTP_USER` | 发件邮箱 | `noreply@medroundtable.com` |
| `SMTP_PASSWORD` | 邮箱密码 | 应用专用密码 |
| `FROM_EMAIL` | 显示发件人 | `noreply@medroundtable.com` |

### 监控配置
| 变量名 | 用途 | 获取地址 |
|--------|------|---------|
| `SENTRY_DSN` | 错误追踪 | https://sentry.io/settings/projects/ |
| `LOG_LEVEL` | 日志级别 | `DEBUG`/`INFO`/`WARNING`/`ERROR` |

### Token 配置
| 变量名 | 用途 | 默认值 |
|--------|------|-------|
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 访问Token有效期 | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 刷新Token有效期 | `7` |

## 📋 快速配置模板

### Zeabur 部署模板
```bash
# 基础配置
PORT=8000
HOST=0.0.0.0
DEBUG=false
SECRET_KEY=你的32位随机字符串

# 数据库（Zeabur自动挂载/data目录）
DATABASE_URL=sqlite:///data/medroundtable.db

# CORS
ALLOWED_ORIGINS=https://medroundtable-v2.vercel.app,https://medroundtable.zeabur.app
CORS_ORIGINS=https://medroundtable-v2.vercel.app,https://medroundtable.zeabur.app

# Second Me OAuth
SECONDME_API_BASE=https://api.mindverse.com/gate/lab
SECONDME_CLIENT_ID=从Second Me获取
SECONDME_CLIENT_SECRET=从Second Me获取
SECONDME_REDIRECT_URI=https://medroundtable.zeabur.app/api/auth/callback

# AI API（至少配一个）
OPENAI_API_KEY=sk-xxx
```

## ✅ 验证命令

```bash
# 生成 SECRET_KEY
openssl rand -hex 32

# 检查环境变量是否设置
echo $SECRET_KEY

# 检查所有必需变量是否已配置
grep -E "^(PORT|HOST|DEBUG|SECRET_KEY|DATABASE_URL|ALLOWED_ORIGINS)=" .env.production
```

## ⚠️ 安全注意事项

1. **SECRET_KEY**: 生产环境必须使用随机生成的密钥，不可使用默认值
2. **API Keys**: 不要提交到Git仓库，使用环境变量或密钥管理服务
3. **OAuth密钥**: Client Secret 绝对不要暴露在前端代码中
4. **数据库**: 生产环境建议使用PostgreSQL而非SQLite
