#!/bin/bash
# 自动部署到 Vercel 和 Railway

echo "🚀 自动部署脚本"
echo "==============="
echo ""

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/root/.openclaw/workspace/medroundtable"
cd "$PROJECT_DIR"

echo -e "${YELLOW}检查依赖...${NC}"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "安装 Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi

# 安装 Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "安装 Vercel CLI..."
    npm install -g vercel
fi

# 安装 Railway CLI
if ! command -v railway &> /dev/null; then
    echo "安装 Railway CLI..."
    npm install -g @railway/cli
fi

echo ""
echo -e "${YELLOW}步骤 1: 登录 Vercel${NC}"
echo "------------------------------"
echo "请在浏览器中完成登录..."
vercel login

echo ""
echo -e "${YELLOW}步骤 2: 部署前端到 Vercel${NC}"
echo "------------------------------"

# 创建 vercel.json
cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/index.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/frontend/index.html"
    }
  ]
}
EOF

# 部署
vercel --prod --yes

echo ""
echo -e "${YELLOW}步骤 3: 登录 Railway${NC}"
echo "------------------------------"
echo "请在浏览器中完成登录..."
railway login

echo ""
echo -e "${YELLOW}步骤 4: 部署后端到 Railway${NC}"
echo "------------------------------"

# 初始化 Railway 项目
railway init --name medroundtable-api

# 添加环境变量
railway variables set SECRET_KEY="medroundtable-secret-key-2024"
if [ -z "${MOONSHOT_API_KEY:-}" ]; then
    echo "MOONSHOT_API_KEY 未设置；请通过 Railway/VPS Secret 管理器注入。"
    exit 1
fi
railway variables set MOONSHOT_API_KEY="$MOONSHOT_API_KEY"

# 部署
railway up

# 获取域名
RAILWAY_DOMAIN=$(railway domain)
echo "Railway 域名: $RAILWAY_DOMAIN"

echo ""
echo -e "${YELLOW}步骤 5: 更新前端 API 地址${NC}"
echo "------------------------------"

# 更新前端配置
sed -i "s|https://mia-rating-ownership-downloads.trycloudflare.com|$RAILWAY_DOMAIN|g" frontend/index.html

# 提交更改
git add .
git commit -m "Update API endpoint to Railway"
git push

# 重新部署前端
vercel --prod --yes

echo ""
echo -e "${GREEN}🎉 部署完成！${NC}"
echo "=============================="
echo ""
echo "访问你的应用:"
echo "  前端: https://medroundtable.vercel.app"
echo "  后端: $RAILWAY_DOMAIN"
echo ""
