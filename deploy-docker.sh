#!/bin/bash
# MedRoundTable Docker 一键部署脚本
# 用法: ./deploy-docker.sh

set -e

echo "🐳 MedRoundTable Docker 一键部署"
echo "=================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装${NC}"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose 未安装${NC}"
    echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker 和 Docker Compose 已安装${NC}"
echo ""

# 检查是否在项目目录
if [ ! -f "backend/main.py" ]; then
    echo -e "${RED}❌ 错误: 请在 medroundtable 项目根目录运行此脚本${NC}"
    exit 1
fi

echo -e "${BLUE}📁 项目目录检查通过${NC}"
echo ""

# 创建数据目录
mkdir -p data
echo -e "${BLUE}📁 创建数据目录${NC}"

# 构建镜像
echo -e "${BLUE}🔨 构建 Docker 镜像...${NC}"
docker-compose build --no-cache

echo -e "${GREEN}✅ 镜像构建完成${NC}"
echo ""

# 启动服务
echo -e "${BLUE}🚀 启动服务...${NC}"
docker-compose up -d

echo -e "${GREEN}✅ 服务已启动${NC}"
echo ""

# 等待服务启动
echo -e "${BLUE}⏳ 等待服务启动...${NC}"
sleep 5

# 检查健康状态
echo -e "${BLUE}🧪 检查服务健康状态...${NC}"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 服务健康检查通过！${NC}"
else
    echo -e "${YELLOW}⚠️  服务正在启动中，请稍后检查${NC}"
fi

echo ""
echo "=================================="
echo -e "${GREEN}🎉 Docker 部署完成！${NC}"
echo "=================================="
echo ""
echo -e "🌐 API 地址: ${YELLOW}http://localhost:8000${NC}"
echo -e "📖 A2A Discovery: ${YELLOW}http://localhost:8000/api/a2a/discovery${NC}"
echo -e "🔐 OAuth 回调: ${YELLOW}http://localhost:8000/api/auth/callback${NC}"
echo ""
echo "📊 查看日志:"
echo "  docker-compose logs -f"
echo ""
echo "🛑 停止服务:"
echo "  docker-compose down"
echo ""
echo "=================================="
