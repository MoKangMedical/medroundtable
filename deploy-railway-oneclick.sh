#!/bin/bash
# MedRoundTable - Railway 一键部署脚本
# 用法: ./deploy-railway-oneclick.sh

set -e  # 遇到错误立即退出

echo "🚀 MedRoundTable Railway 一键部署"
echo "=================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
CLIENT_ID="19b5f08b-2256-41aa-b196-2f98491099f7"
CLIENT_SECRET="f9f406e3d8dc4fe8e8363853865e1afea2957e7b0a33d75e96cbc5a22c4c20f3"
PROJECT_NAME="medroundtable-api"

# 检查 Railway CLI
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}⚠️  Railway CLI 未安装${NC}"
    echo "正在安装..."
    npm install -g @railway/cli
fi

# 检查登录状态
echo -e "${BLUE}🔍 检查 Railway 登录状态...${NC}"
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}请登录 Railway...${NC}"
    railway login
fi

echo -e "${GREEN}✅ Railway CLI 已安装并登录${NC}"
echo ""

# 检查是否在项目目录
if [ ! -f "backend/main.py" ]; then
    echo -e "${RED}❌ 错误: 请在 medroundtable 项目根目录运行此脚本${NC}"
    echo "当前目录: $(pwd)"
    exit 1
fi

echo -e "${BLUE}📁 项目目录检查通过${NC}"
echo ""

# 初始化项目
echo -e "${BLUE}🚀 初始化 Railway 项目...${NC}"
if [ ! -d ".railway" ]; then
    railway init --name "$PROJECT_NAME"
else
    echo "项目已初始化"
fi
echo ""

# 连接项目
echo -e "${BLUE}🔗 连接 Railway 项目...${NC}"
railway link

echo ""
echo -e "${BLUE}⚙️  配置环境变量...${NC}"

# 设置环境变量
railway variables set PORT="8000"
railway variables set HOST="0.0.0.0"
railway variables set DEBUG="false"
railway variables set SECRET_KEY="0a1267066319f509476a44ea41c17798df616b97f93882b7d5e6ed88c065b475"
railway variables set DATABASE_URL="sqlite:///app/data/medroundtable.db"
railway variables set CORS_ORIGINS="https://medroundtable-v2.vercel.app,https://app.secondme.io,https://go.second.me"

# Second Me OAuth 配置
railway variables set SECONDME_CLIENT_ID="$CLIENT_ID"
railway variables set SECONDME_CLIENT_SECRET="$CLIENT_SECRET"
railway variables set SECONDME_REDIRECT_URI="https://medroundtable-api.up.railway.app/api/auth/callback"
railway variables set SECONDME_API_BASE="https://api.mindverse.com/gate/lab"

# AI API Keys (可选，使用环境变量或留空)
railway variables set MOONSHOT_API_KEY="${MOONSHOT_API_KEY:-}"
railway variables set OPENAI_API_KEY="${OPENAI_API_KEY:-}"

echo -e "${GREEN}✅ 环境变量设置完成${NC}"
echo ""

# 部署
echo -e "${BLUE}🚀 开始部署...${NC}"
railway up --detach

echo ""
echo -e "${GREEN}🎉 部署完成！${NC}"
echo ""

# 获取域名
echo -e "${BLUE}📋 获取服务信息...${NC}"
DOMAIN=$(railway domain 2>/dev/null || echo "medroundtable-api.up.railway.app")

echo ""
echo "=================================="
echo -e "${GREEN}✅ MedRoundTable API 已部署！${NC}"
echo "=================================="
echo ""
echo -e "🌐 API 地址: ${YELLOW}https://$DOMAIN${NC}"
echo -e "📖 A2A Discovery: ${YELLOW}https://$DOMAIN/api/a2a/discovery${NC}"
echo -e "🔐 OAuth 回调: ${YELLOW}https://$DOMAIN/api/auth/callback${NC}"
echo ""
echo "📊 查看日志:"
echo "  railway logs"
echo ""
echo "🔧 管理项目:"
echo "  https://railway.app/dashboard"
echo ""
echo "=================================="
echo -e "${YELLOW}⚠️  重要提醒:${NC}"
echo "1. 请记录上面的 API 地址"
echo "2. 更新 Second Me 开发者平台的回调地址"
echo "3. 更新 Vercel 前端的环境变量"
echo "4. 测试 API 是否正常工作"
echo "=================================="
echo ""

# 测试部署
echo -e "${BLUE}🧪 测试 API 连接...${NC}"
sleep 3

if curl -s "https://$DOMAIN/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API 健康检查通过！${NC}"
else
    echo -e "${YELLOW}⏳ API 正在启动中，请稍后手动检查:${NC}"
    echo "  curl https://$DOMAIN/health"
fi

echo ""
echo -e "${GREEN}🎊 部署完成！${NC}"
