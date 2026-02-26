#!/bin/bash
# Zeabur 一键部署脚本
# 国内访问友好的 Serverless 平台

echo "🚀 MedRoundTable Zeabur 部署脚本"
echo "================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查 Zeabur CLI
if ! command -v zeabur &> /dev/null; then
    echo -e "${BLUE}📦 安装 Zeabur CLI...${NC}"
    curl -fsSL https://raw.githubusercontent.com/zeabur/cli/main/install.sh | bash
    
    # 添加到 PATH
    export PATH="$HOME/.zeabur/bin:$PATH"
    echo 'export PATH="$HOME/.zeabur/bin:$PATH"' >> ~/.bashrc
fi

# 检查登录
echo ""
echo -e "${BLUE}🔍 检查 Zeabur 登录状态...${NC}"
if ! zeabur auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️  需要登录 Zeabur${NC}"
    echo ""
    echo "请运行: zeabur auth login"
    echo "或访问 https://zeabur.com 获取 API Token"
    exit 1
fi

echo -e "${GREEN}✅ 已登录 Zeabur${NC}"

# 创建项目
echo ""
echo -e "${BLUE}📁 创建 Zeabur 项目...${NC}"
PROJECT_NAME="medroundtable-api"

if zeabur project list | grep -q "$PROJECT_NAME"; then
    echo "项目已存在"
else
    zeabur project create "$PROJECT_NAME"
fi

# 部署
echo ""
echo -e "${BLUE}🚀 开始部署...${NC}"
zeabur deploy --project "$PROJECT_NAME"

echo ""
echo -e "${GREEN}🎉 部署完成！${NC}"
echo ""
echo "📋 查看服务:"
zeabur service list --project "$PROJECT_NAME"

echo ""
echo "🌐 获取域名:"
zeabur domain list --project "$PROJECT_NAME"
