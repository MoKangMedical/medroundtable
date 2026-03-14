#!/bin/bash
# MedRoundTable 一键上线脚本

echo "🚀 MedRoundTable 一键上线"
echo "=========================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. 检查部署状态
echo -e "${BLUE}1️⃣  检查部署状态${NC}"
if docker ps | grep -q "medroundtable-api"; then
    echo -e "${GREEN}✅ 后端服务运行中${NC}"
else
    echo -e "${YELLOW}⚠️  后端服务未运行，正在启动...${NC}"
    docker compose -f docker-compose.prod.yml up -d
fi

if docker ps | grep -q "medroundtable-web"; then
    echo -e "${GREEN}✅ 前端服务运行中${NC}"
else
    echo -e "${YELLOW}⚠️  前端服务未运行${NC}"
fi

echo ""
echo -e "${BLUE}2️⃣  服务地址${NC}"
echo "   后端 API: http://localhost:8001"
echo "   前端页面: http://localhost:3001"

echo ""
echo -e "${BLUE}3️⃣  Second Me 提交信息${NC}"
echo "   应用名称: MedRoundTable"
echo "   应用描述: 全球首个A2A架构医学科研协作平台"
echo "   Manifest: secondme-manifest.json"
echo "   提交地址: https://app.secondme.io/developer"

echo ""
echo "=========================="
echo -e "${GREEN}🎉 MedRoundTable 已就绪！${NC}"
echo ""
echo "下一步: 访问 https://app.secondme.io/developer 提交应用"
