#!/bin/bash
# 配置 Cloudflare 持久隧道 - 自动 HTTPS

set -e

echo "🔒 MedRoundTable HTTPS 配置"
echo "============================"
echo ""

# 检查 cloudflared
if ! command -v cloudflared &> /dev/null; then
    echo "📦 安装 cloudflared..."
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    dpkg -i cloudflared-linux-amd64.deb
    rm cloudflared-linux-amd64.deb
fi

# 检查登录状态
if [ ! -f ~/.cloudflared/cert.pem ]; then
    echo "⚠️  需要登录 Cloudflare"
    echo "请运行: cloudflared tunnel login"
    echo "然后在浏览器中授权"
    exit 1
fi

echo "✅ 已登录 Cloudflare"

# 创建隧道
TUNNEL_NAME="medroundtable-api"
if cloudflared tunnel list 2>/dev/null | grep -q "$TUNNEL_NAME"; then
    echo "隧道已存在"
    TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
else
    echo "创建隧道: $TUNNEL_NAME"
    cloudflared tunnel create "$TUNNEL_NAME"
    TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
fi

echo "隧道 ID: $TUNNEL_ID"

# 创建配置文件
mkdir -p ~/.cloudflared

cat > ~/.cloudflared/config.yml << EOF
tunnel: $TUNNEL_ID
credentials-file: /root/.cloudflared/$TUNNEL_ID.json

ingress:
  - hostname: api.medroundtable.io
    service: http://localhost:80
  - service: http_status:404
EOF

echo "✅ 配置文件已创建"

# 创建 DNS 记录
echo ""
echo "🌐 创建 DNS 记录..."
cloudflared tunnel route dns "$TUNNEL_NAME" "api.medroundtable.io"
echo "✅ DNS 记录已创建: api.medroundtable.io"

# 创建 systemd 服务
cat > /etc/systemd/system/cloudflared-medroundtable.service << EOF
[Unit]
Description=Cloudflare Tunnel for MedRoundTable
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/cloudflared tunnel run $TUNNEL_NAME
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cloudflared-medroundtable.service

echo ""
echo "🎉 配置完成！"
echo ""
echo "🌐 HTTPS 地址: https://api.medroundtable.io"
echo ""
echo "启动命令:"
echo "  systemctl start cloudflared-medroundtable"
echo ""
echo "查看状态:"
echo "  systemctl status cloudflared-medroundtable"
echo "  cloudflared tunnel info $TUNNEL_NAME"
