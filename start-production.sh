#!/bin/bash
# MedRoundTable - 一键启动脚本（服务器重启后使用）

echo "🚀 MedRoundTable - 启动服务"
echo "=============================="

PROJECT_DIR="/root/.openclaw/workspace/medroundtable"
cd "$PROJECT_DIR"

# 停止旧进程
echo "清理旧进程..."
pkill -f "python.*backend/main.py" 2>/dev/null
pkill -f "http.server 3000" 2>/dev/null
pkill -f "cloudflared tunnel" 2>/dev/null
sleep 2

# 启动后端
echo "启动后端 API..."
PYTHONPATH="$PROJECT_DIR" nohup python3 backend/main.py > /tmp/api_server.log 2>&1 &
sleep 3

# 启动前端
echo "启动前端..."
cd "$PROJECT_DIR/frontend"
nohup python3 -m http.server 3000 > /tmp/web_server.log 2>&1 &
sleep 2

# 启动 Cloudflare 隧道
echo "启动 Cloudflare 隧道..."
cd "$PROJECT_DIR"
nohup cloudflared tunnel --url http://localhost:3000 > /tmp/cf_web.log 2>&1 &
sleep 8
nohup cloudflared tunnel --url http://localhost:8000 > /tmp/cf_api.log 2>&1 &
sleep 8

# 获取链接
WEB_URL=$(grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf_web.log | head -1)
API_URL=$(grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" /tmp/cf_api.log | head -1)

echo ""
echo "✅ 启动完成！"
echo "=============================="
echo ""
echo "📱 访问链接:"
echo "   前端: $WEB_URL"
echo "   API:  $API_URL"
echo ""
echo "🔧 管理命令:"
echo "   查看状态: bash $PROJECT_DIR/status.sh"
echo "   停止服务: pkill -f 'python.*main|http.server|cloudflared'"
echo ""
echo "⏰ 监控状态:"
echo "   每2分钟自动检查，确保24/7运行"
echo ""
