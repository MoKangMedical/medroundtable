#!/bin/bash
# MedRoundTable 生产环境部署脚本

set -e

echo "🚀 MedRoundTable 生产环境部署"
echo "================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 配置
BACKEND_PORT=8001
FRONTEND_PORT=3001
PROJECT_NAME="medroundtable"

echo -e "${YELLOW}📋 部署配置:${NC}"
echo "  后端端口: $BACKEND_PORT"
echo "  前端端口: $FRONTEND_PORT"
echo ""

# 检查Docker
echo -e "${YELLOW}🔍 检查 Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker Compose 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker 检查通过${NC}"

# 检查端口
echo -e "${YELLOW}🔍 检查端口占用...${NC}"
if netstat -tlnp 2>/dev/null | grep -q ":$BACKEND_PORT "; then
    echo -e "${RED}❌ 端口 $BACKEND_PORT 已被占用${NC}"
    exit 1
fi

if netstat -tlnp 2>/dev/null | grep -q ":$FRONTEND_PORT "; then
    echo -e "${RED}❌ 端口 $FRONTEND_PORT 已被占用${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 端口检查通过${NC}"

# 构建和启动
echo -e "${YELLOW}🏗️  构建 Docker 镜像...${NC}"
docker compose -f docker-compose.prod.yml build

echo -e "${YELLOW}🚀 启动服务...${NC}"
docker compose -f docker-compose.prod.yml up -d

# 等待服务启动
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 5

# 健康检查
echo -e "${YELLOW}🏥 健康检查...${NC}"
if curl -s "http://localhost:$BACKEND_PORT/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 后端服务运行正常${NC}"
else
    echo -e "${YELLOW}⚠️ 后端服务可能还在启动中${NC}"
fi

echo ""
echo "================================"
echo -e "${GREEN}🎉 部署完成!${NC}"
echo ""
echo "📊 服务状态:"
echo "  后端 API: http://localhost:$BACKEND_PORT"
echo "  前端页面: http://localhost:$FRONTEND_PORT"
echo ""
echo "📋 常用命令:"
echo "  查看日志: docker compose -f docker-compose.prod.yml logs -f"
echo "  停止服务: docker compose -f docker-compose.prod.yml down"
echo "  重启服务: docker compose -f docker-compose.prod.yml restart"
echo ""
