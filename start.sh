#!/bin/bash
# MedRoundTable - 一键启动脚本

echo "🚀 启动 MedRoundTable - 临床科研圆桌会"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查依赖
echo -e "${YELLOW}检查依赖...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 需要安装 Python3${NC}"
    exit 1
fi

# 设置路径
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo -e "${BLUE}📁 项目目录: $PROJECT_DIR${NC}"

# 安装依赖
echo -e "${YELLOW}安装Python依赖...${NC}"
cd "$PROJECT_DIR"

pip3 install fastapi uvicorn pydantic websockets sse-starlette -q 2>/dev/null || pip3 install fastapi uvicorn pydantic websockets sse-starlette --break-system-packages -q

# 停止旧进程
echo -e "${YELLOW}清理旧进程...${NC}"
pkill -f "python.*backend/main" 2>/dev/null
pkill -f "http.server 3000" 2>/dev/null
sleep 2

# 启动后端
echo -e "${YELLOW}启动后端服务...${NC}"
cd "$PROJECT_DIR"
PYTHONPATH="$PROJECT_DIR" python3 backend/main.py > /tmp/medroundtable_api.log 2>&1 &
BACKEND_PID=$!
echo "后端PID: $BACKEND_PID"

# 等待后端启动
echo "等待后端启动..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端启动成功 (http://localhost:8000)${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ 后端启动失败${NC}"
        echo "查看日志: tail -f /tmp/medroundtable_api.log"
        exit 1
    fi
done

# 启动前端
echo -e "${YELLOW}启动前端服务...${NC}"
cd "$FRONTEND_DIR"
python3 -m http.server 3000 > /tmp/medroundtable_web.log 2>&1 &
FRONTEND_PID=$!
echo "前端PID: $FRONTEND_PID"

sleep 3
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 前端启动成功 (http://localhost:3000)${NC}"
else
    echo -e "${RED}❌ 前端启动失败${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 MedRoundTable 启动完成！${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📱 访问地址:${NC}"
echo "   前端界面: http://localhost:3000"
echo "   API文档:  http://localhost:8000/docs"
echo ""
echo -e "${BLUE}🤖 AI专家团队:${NC}"
echo "   👨‍⚕️ 临床主任 - 识别科研价值"
echo "   📚 博士生 - 文献调研协调"
echo "   📊 流行病学家 - 研究设计"
echo "   📈 统计专家 - 数据分析"
echo "   👩‍⚕️ 研究护士 - 执行管理"
echo ""
echo -e "${YELLOW}🔧 常用命令:${NC}"
echo "   查看后端日志: tail -f /tmp/medroundtable_api.log"
echo "   查看前端日志: tail -f /tmp/medroundtable_web.log"
echo "   停止服务: pkill -f 'python.*backend/main|http.server 3000'"
echo ""
echo -e "${YELLOW}💡 使用流程:${NC}"
echo "   1. 打开浏览器访问 http://localhost:3000"
echo "   2. 点击'新建圆桌会'"
echo "   3. 输入临床问题，创建圆桌会"
echo "   4. 观看5位AI专家自动讨论"
echo "   5. 实时提问参与讨论"
echo "   6. 导出完整研究方案"
echo ""
echo "按 Ctrl+C 停止日志查看，服务将继续在后台运行"
echo ""

# 显示后端日志
tail -f /tmp/medroundtable_api.log
