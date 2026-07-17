#!/bin/bash

# MedRoundTable Startup Script for Second Me

echo "🩺 启动 MedRoundTable..."
echo ""

# 设置环境变量
if [ -z "${MOONSHOT_API_KEY:-}" ]; then
    echo "❌ 请先在 Windows 环境变量中设置 MOONSHOT_API_KEY"
    exit 1
fi
export MOONSHOT_API_KEY
export MOONSHOT_BASE_URL="https://api.moonshot.cn/v1"
export MOONSHOT_MODEL="moonshot-v1-32k"

# 启动后端
echo "📡 启动后端服务 (端口 8000)..."
cd /root/.openclaw/workspace/medroundtable-secondme/backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > /tmp/medroundtable_backend.log 2>&1 &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 检查后端是否启动成功
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 后端服务启动成功"
else
    echo "❌ 后端服务启动失败，查看日志: /tmp/medroundtable_backend.log"
    cat /tmp/medroundtable_backend.log
    exit 1
fi

# 启动前端
echo "🌐 启动前端服务 (端口 3000)..."
cd /root/.openclaw/workspace/medroundtable-secondme/frontend
python3 -m http.server 3000 > /tmp/medroundtable_frontend.log 2>&1 &
FRONTEND_PID=$!

# 等待前端启动
sleep 2

# 检查前端是否启动成功
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
    echo "✅ 前端服务启动成功"
else
    echo "❌ 前端服务启动失败，查看日志: /tmp/medroundtable_frontend.log"
fi

echo ""
echo "🎉 MedRoundTable 已启动！"
echo ""
echo "📍 访问地址:"
echo "  - 本地前端: http://localhost:3000"
echo "  - 本地后端: http://localhost:8000"
echo "  - 健康检查: http://localhost:8000/health"
echo ""
echo "🔧 功能特性:"
echo "  - 5位AI专家协作讨论"
echo "  - 真实Kimi API集成"
echo "  - 临床研究方案生成"
echo "  - 思维导图可视化"
echo ""
echo "💡 使用说明:"
echo "  1. 打开浏览器访问前端地址"
echo "  2. 点击'开始新的圆桌会'"
echo "  3. 填写研究标题和临床问题"
echo "  4. 观看AI专家自动讨论"
echo ""
echo "⚠️  按 Ctrl+C 停止服务"

# 保持脚本运行
tail -f /tmp/medroundtable_backend.log
