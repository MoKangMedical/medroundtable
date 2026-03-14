#!/bin/bash
# 部署后域名更新脚本
# 使用方法: ./update-domain.sh <your-zeabur-domain>

set -e

DOMAIN=$1

if [ -z "$DOMAIN" ]; then
    echo "❌ 错误: 请提供 Zeabur 域名"
    echo "用法: ./update-domain.sh medroundtable-xxx.zeabur.app"
    exit 1
fi

echo "🔄 更新 MedRoundTable 域名配置"
echo "================================"
echo ""
echo "新域名: $DOMAIN"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 更新 zeabur.toml
echo "📄 更新 zeabur.toml..."
sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" zeabur.toml 2>/dev/null || true

cat > zeabur.toml << EOF
name = "medroundtable"

[build]
builder = "DOCKERFILE"
dockerfile = "Dockerfile"

[deploy]
startCommand = ""
healthCheckPath = "/health"
healthCheckPort = 8000
autoDeploy = true

[env]
DATABASE_URL = { default = "sqlite:///data/medroundtable.db" }
SECRET_KEY = { default = "$(openssl rand -hex 32)" }
ALLOWED_ORIGINS = { default = "https://medroundtable-v2.vercel.app,https://${DOMAIN}" }
CORS_ORIGINS = { default = "https://medroundtable-v2.vercel.app,https://${DOMAIN}" }
SECONDME_REDIRECT_URI = { default = "https://${DOMAIN}/api/auth/callback" }
EOF

echo -e "${GREEN}✅ zeabur.toml 已更新${NC}"

# 更新 secondme-manifest.json
echo "📄 更新 secondme-manifest.json..."

if [ -f "secondme-manifest.json" ]; then
    cat > secondme-manifest.json << EOF
{
  "manifest_version": "1.0",
  "app_name": "MedRoundTable",
  "app_description": "全球首个基于A2A架构的医学科研协作平台",
  "version": "1.0.0",
  "author": "MoKangMedical",
  "website": "https://medroundtable-v2.vercel.app",
  "icon_url": "https://medroundtable-v2.vercel.app/logo.png",
  
  "a2a_protocol": {
    "version": "1.0",
    "discovery_endpoint": "https://${DOMAIN}/a2a/discovery",
    "messaging_endpoint": "https://${DOMAIN}/a2a/message",
    "task_endpoint": "https://${DOMAIN}/a2a/tasks"
  },
  
  "agents": [
    {
      "id": "clinical-director",
      "name": "临床主任",
      "description": "临床研究方向规划专家",
      "skills": ["研究设计", "方向规划", "文献指导"],
      "endpoint": "https://${DOMAIN}/agents/clinical-director"
    },
    {
      "id": "phd-student",
      "name": "博士生",
      "description": "实验设计与数据分析专家",
      "skills": ["实验设计", "统计分析", "论文写作"],
      "endpoint": "https://${DOMAIN}/agents/phd-student"
    },
    {
      "id": "epidemiologist",
      "name": "流行病学家",
      "description": "流行病学研究专家",
      "skills": ["队列研究", "病例对照", "生存分析"],
      "endpoint": "https://${DOMAIN}/agents/epidemiologist"
    },
    {
      "id": "statistician",
      "name": "统计专家",
      "description": "医学统计专家",
      "skills": ["统计方法", "R语言", "样本量计算"],
      "endpoint": "https://${DOMAIN}/agents/statistician"
    },
    {
      "id": "research-nurse",
      "name": "研究护士",
      "description": "临床研究执行专家",
      "skills": ["CRF设计", "数据管理", "伦理规范"],
      "endpoint": "https://${DOMAIN}/agents/research-nurse"
    }
  ],
  
  "oauth2": {
    "authorization_endpoint": "https://go.second.me/oauth/authorize",
    "token_endpoint": "https://${DOMAIN}/api/auth/token",
    "scopes": ["profile", "email", "shades:read", "softmemory:read"],
    "redirect_uris": [
      "https://${DOMAIN}/api/auth/callback",
      "https://medroundtable-v2.vercel.app/auth/callback"
    ]
  },
  
  "webhooks": {
    "events": ["task.completed", "message.received", "agent.assigned"],
    "endpoint": "https://${DOMAIN}/webhooks/secondme"
  },
  
  "pricing": {
    "currency": "CNY",
    "plans": [
      {
        "id": "free",
        "name": "免费版",
        "price": 0,
        "description": "基础科研协作功能"
      },
      {
        "id": "pro",
        "name": "专业版",
        "price": 299,
        "period": "month",
        "description": "AI专家无限对话"
      },
      {
        "id": "team",
        "name": "团队版",
        "price": 999,
        "period": "month",
        "description": "5人团队协作"
      }
    ]
  }
}
EOF
    echo -e "${GREEN}✅ secondme-manifest.json 已更新${NC}"
else
    echo -e "${YELLOW}⚠️  secondme-manifest.json 不存在，跳过${NC}"
fi

# 更新 .env.production 模板
echo "📄 更新环境变量配置..."

cat > .env.production << EOF
# MedRoundTable 生产环境配置
# 部署到 Zeabur 时设置这些环境变量

# ==========================================
# 服务配置
# ==========================================
PORT=8000
HOST=0.0.0.0
DEBUG=false

# ==========================================
# 数据库
# ==========================================
DATABASE_URL=sqlite:///data/medroundtable.db
# 或使用 PostgreSQL:
# DATABASE_URL=postgresql://user:pass@host:5432/medroundtable

# ==========================================
# 安全配置
# ==========================================
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# ==========================================
# CORS 配置
# ==========================================
ALLOWED_ORIGINS=https://medroundtable-v2.vercel.app,https://${DOMAIN}
CORS_ORIGINS=https://medroundtable-v2.vercel.app,https://${DOMAIN}

# ==========================================
# Second Me OAuth
# ==========================================
SECONDME_API_BASE=https://api.mindverse.com/gate/lab
SECONDME_CLIENT_ID=your_client_id_here
SECONDME_CLIENT_SECRET=your_client_secret_here
SECONDME_REDIRECT_URI=https://${DOMAIN}/api/auth/callback

# ==========================================
# AI API Keys
# ==========================================
# OpenAI
OPENAI_API_KEY=your_openai_key

# Anthropic (Claude)
ANTHROPIC_API_KEY=your_anthropic_key

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_key

# Moonshot (Kimi)
MOONSHOT_API_KEY=your_moonshot_key

# Zhipu AI (GLM)
ZHIPU_API_KEY=your_zhipu_key

# ==========================================
# 支付配置 (Stripe)
# ==========================================
STRIPE_PUBLISHABLE_KEY=pk_live_xxx
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# ==========================================
# 存储配置
# ==========================================
# 阿里云OSS 或 AWS S3
STORAGE_PROVIDER=local
# STORAGE_ENDPOINT=
# STORAGE_BUCKET=
# STORAGE_ACCESS_KEY=
# STORAGE_SECRET_KEY=

# ==========================================
# 邮件配置
# ==========================================
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@medroundtable.com
SMTP_PASSWORD=your_smtp_password
FROM_EMAIL=noreply@medroundtable.com

# ==========================================
# 监控配置
# ==========================================
SENTRY_DSN=
LOG_LEVEL=INFO
EOF

echo -e "${GREEN}✅ .env.production 已更新${NC}"

# 创建 CORS 配置
cat > cors_config.py << EOF
"""CORS 配置"""
ALLOWED_ORIGINS = [
    "https://medroundtable-v2.vercel.app",
    "https://${DOMAIN}",
    "https://*.zeabur.app",
]

ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]

ALLOWED_HEADERS = [
    "*",
    "Authorization",
    "Content-Type",
    "X-Request-ID",
    "X-Correlation-ID",
]
EOF

echo -e "${GREEN}✅ CORS 配置已更新${NC}"
echo ""

# 保存域名
echo "$DOMAIN" > .zeabur_domain

# 提交更改
echo "📝 提交更改到 Git..."
git add zeabur.toml secondme-manifest.json .env.production cors_config.py 2>/dev/null || true
git commit -m "chore: update domain to ${DOMAIN}" 2>/dev/null || echo "无需提交"

echo ""
echo -e "${GREEN}🎉 域名配置更新完成！${NC}"
echo ""
echo "📋 下一步:"
echo "---------"
echo "1. 推送代码到 GitHub:"
echo "   git push origin main"
echo ""
echo "2. 在 Zeabur Dashboard 设置环境变量:"
echo "   - SECONDME_CLIENT_ID"
echo "   - SECONDME_CLIENT_SECRET"
echo "   - AI API Keys"
echo ""
echo "3. 重新部署应用"
echo ""
echo "🔗 访问地址:"
echo "   前端: https://medroundtable-v2.vercel.app"
echo "   后端: https://${DOMAIN}"
echo "   A2A Discovery: https://${DOMAIN}/a2a/discovery"
echo ""
