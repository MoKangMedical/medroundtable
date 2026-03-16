#!/bin/bash
# MedRoundTable V2.0 - 访问解决方案

echo "======================================"
echo "🔧 MedRoundTable V2.0 访问修复"
echo "======================================"
echo ""

echo "❌ 问题: 服务器安全组/防火墙限制了8000端口"
echo ""

echo "======================================"
echo "✅ 解决方案 1: SSH隧道 (推荐，立即可用)"
echo "======================================"
echo ""
echo "在你的本地电脑终端运行:"
echo ""
echo "  ssh -L 8000:localhost:8000 root@43.134.3.158"
echo ""
echo "然后访问:"
echo "  http://localhost:8000"
echo "  http://localhost:8000/docs"
echo ""

echo "======================================"
echo "✅ 解决方案 2: 使用80端口 (可能已开放)"
echo "======================================"
echo ""

# 尝试使用80端口
echo "🔄 尝试在80端口启动服务..."
pkill -f "uvicorn.*main:app" 2>/dev/null
sleep 2

export SECRET_KEY="medroundtable-v2-$(date +%s)"
nohup python3 -m uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port 80 \
    > /tmp/medroundtable-80.log 2>&1 &

sleep 3

if curl -s http://localhost:80/health > /dev/null 2>&1; then
    echo "✅ 80端口启动成功!"
    echo ""
    echo "🌐 访问地址:"
    echo "  http://43.134.3.158/"
    echo "  http://43.134.3.158/docs"
else
    echo "❌ 80端口也需要权限，尝试方案3..."
    
    # 回到8000端口
    nohup python3 -m uvicorn backend.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        > /tmp/medroundtable.log 2>&1 &
fi

echo ""
echo "======================================"
echo "✅ 解决方案 3: Cloudflare Tunnel (最稳定)"
echo "======================================"
echo ""
echo "运行以下命令创建安全隧道:"
echo ""
echo "  cloudflared tunnel --url http://localhost:8000"
echo ""
echo "会得到类似 https://xxx.trycloudflare.com 的链接"
echo ""

echo "======================================"
echo "✅ 解决方案 4: 部署到 Vercel/Zeabur"
echo "======================================"
echo ""
echo "1. 访问 https://vercel.com 或 https://zeabur.com"
echo "2. 导入 GitHub 仓库"
echo "3. 自动部署完成"
echo ""

echo "======================================"
echo "📊 当前服务状态"
echo "======================================"
echo ""

PID=$(ps aux | grep "uvicorn.*main:app" | grep -v grep | awk '{print $2}')
if [ -n "$PID" ]; then
    echo "✅ 服务运行中 (PID: $PID)"
    echo "✅ 本地访问: http://localhost:8000 (服务器上)"
    echo "⚠️  外部访问: 被防火墙限制"
else
    echo "❌ 服务未运行"
fi

echo ""
echo "======================================"
echo "💡 推荐"
echo "======================================"
echo ""
echo "立即可用: SSH隧道"
echo "长期方案: 部署到 Zeabur (5分钟搞定)"
echo ""
