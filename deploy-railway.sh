#!/bin/bash
# MedRoundTable Railway 一键部署脚本

echo "🚀 MedRoundTable Railway 部署脚本"
echo "=================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 初始化项目（如果不存在）
echo ""
echo -e "${BLUE}📁 初始化 Railway 项目...${NC}"
if [ ! -f ".railway/config.json" ]; then
    railway init --name medroundtable-api
else
    echo "项目已初始化"
fi

# 设置环境变量
echo ""
echo -e "${BLUE}⚙️  配置环境变量...${NC}"
railway variables set SECRET_KEY="$(openssl rand -hex 32)"
railway variables set DEBUG="false"
railway variables set DATABASE_URL="sqlite:///app/data/medroundtable.db"
railway variables set CORS_ORIGINS="https://medroundtable-v2.vercel.app,https://app.secondme.io"

echo ""
echo -e "${GREEN}✅ 环境变量设置完成${NC}"

# 部署
echo ""
echo -e "${BLUE}🚀 开始部署...${NC}"
railway up

echo ""
echo -e "${GREEN}🎉 部署完成！${NC}"
echo ""
echo "📋 查看服务状态:"
railway status

echo ""
echo "🔗 获取域名:"
railway domain

echo ""
echo "📊 查看日志:"
railway logs
