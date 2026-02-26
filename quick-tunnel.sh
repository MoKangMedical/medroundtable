#!/bin/bash
# Cloudflare Quick Tunnel - 无需域名，立即获得 HTTPS

echo "🚀 Cloudflare Quick Tunnel - 临时 HTTPS"
echo "========================================"
echo ""

# 检查 cloudflared
if ! command -v cloudflared &> /dev/null; then
    echo "📦 安装 cloudflared..."
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    dpkg -i cloudflared-linux-amd64.deb
    rm cloudflared-linux-amd64.deb
    echo "✅ 安装完成"
fi

echo ""
echo "🌐 启动 Quick Tunnel..."
echo "这将为你的后端生成一个临时的 HTTPS URL"
echo ""
echo "按 Ctrl+C 停止隧道"
echo ""

# 启动 quick tunnel
cloudflared tunnel --url http://localhost:8001
