#!/bin/bash
# MedRoundTable - 永久部署脚本
# 使用 PM2 进程管理器确保 24/7 运行

echo "🚀 MedRoundTable 永久部署脚本"
echo "==============================="

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 安装 PM2
if ! command -v pm2 &> /dev/null; then
    echo -e "${YELLOW}安装 PM2 进程管理器...${NC}"
    npm install -g pm2
fi

# 项目目录
PROJECT_DIR="/root/.openclaw/workspace/medroundtable"
cd "$PROJECT_DIR"

# 停止旧进程
echo -e "${YELLOW}清理旧进程...${NC}"
pm2 delete medroundtable-api 2>/dev/null || true
pm2 delete medroundtable-web 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "http.server 3000" 2>/dev/null || true
sleep 2

# 安装依赖
echo -e "${YELLOW}安装依赖...${NC}"
pip3 install fastapi uvicorn pydantic sse-starlette -q 2>/dev/null || pip3 install fastapi uvicorn pydantic sse-starlette --break-system-packages -q

# 启动后端
echo -e "${YELLOW}启动后端 API...${NC}"
PYTHONPATH="$PROJECT_DIR" pm2 start backend/main.py \
    --name medroundtable-api \
    --interpreter python3 \
    --watch \
    --ignore-watch "frontend/*" \
    --log /var/log/medroundtable-api.log

# 等待后端启动
sleep 5

# 启动前端
echo -e "${YELLOW}启动前端...${NC}"
cd "$PROJECT_DIR/frontend"
pm2 start "python3 -m http.server 3000" \
    --name medroundtable-web \
    --log /var/log/medroundtable-web.log

# 保存 PM2 配置
echo -e "${YELLOW}保存配置...${NC}"
pm2 save
pm2 startup systemd -u root --hp /root

echo ""
echo -e "${GREEN}✅ 部署完成！${NC}"
echo ""
echo "服务状态:"
pm2 status
echo ""
echo "日志查看:"
echo "  后端: pm2 logs medroundtable-api"
echo "  前端: pm2 logs medroundtable-web"
echo ""
echo "管理命令:"
echo "  停止: pm2 stop medroundtable-api medroundtable-web"
echo "  重启: pm2 restart medroundtable-api medroundtable-web"
echo "  查看: pm2 status"
