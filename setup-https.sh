#!/bin/bash
# 快速 HTTPS 配置脚本（使用 mkcert 自签名或 Let's Encrypt）

set -e

echo "🔒 MedRoundTable HTTPS 快速配置"
echo "================================"
echo ""

# 检查是否有域名
read -p "你有域名吗？(y/n): " HAS_DOMAIN

if [ "$HAS_DOMAIN" = "y" ] || [ "$HAS_DOMAIN" = "Y" ]; then
    read -p "请输入域名 (例如: api.yourdomain.com): " DOMAIN
    
    echo ""
    echo "📦 安装 Certbot..."
    apt-get update -qq
    apt-get install -y -qq certbot
    
    echo ""
    echo "🔒 申请 SSL 证书..."
    echo "请确保域名已指向本服务器 IP: $(curl -s ip.sb)"
    read -p "确认继续? (y/n): " CONFIRM
    
    if [ "$CONFIRM" = "y" ]; then
        certbot certonly --standalone -d "$DOMAIN" --agree-tos --non-interactive --email admin@$DOMAIN
        
        CERT_PATH="/etc/letsencrypt/live/$DOMAIN"
        echo "✅ 证书已安装到: $CERT_PATH"
        
        # 配置 Nginx
        setup_nginx "$DOMAIN" "$CERT_PATH/fullchain.pem" "$CERT_PATH/privkey.pem"
    fi
else
    echo ""
    echo "⚠️  没有域名，使用自签名证书（仅测试用）..."
    
    # 安装 mkcert
    if ! command -v mkcert &> /dev/null; then
        apt-get update -qq
        apt-get install -y -qq libnss3-tools
        
        curl -s https://api.github.com/repos/FiloSottile/mkcert/releases/latest | grep browser_download_url | grep linux-amd64 | cut -d '"' -f 4 | wget -qi -
        mv mkcert-v*-linux-amd64 mkcert
        chmod +x mkcert
        mv mkcert /usr/local/bin/
    fi
    
    # 生成自签名证书
    mkdir -p /etc/medroundtable/ssl
    cd /etc/medroundtable/ssl
    
    mkcert -install
    mkcert localhost 127.0.0.1 ::1 $(curl -s ip.sb)
    
    mv localhost+3.pem cert.pem
    mv localhost+3-key.pem key.pem
    
    echo "✅ 自签名证书已生成"
    echo "⚠️  浏览器会显示安全警告，点击高级->继续访问即可"
    
    # 配置 Nginx
    setup_nginx "localhost" "/etc/medroundtable/ssl/cert.pem" "/etc/medroundtable/ssl/key.pem"
fi

# 安装和配置 Nginx 的函数
setup_nginx() {
    local DOMAIN=$1
    local CERT=$2
    local KEY=$3
    
    echo ""
    echo "📦 安装 Nginx..."
    apt-get install -y -qq nginx
    
    echo ""
    echo "⚙️  配置 Nginx..."
    
    cat > /etc/nginx/sites-available/medroundtable << EOF
server {
    listen 443 ssl http2;
    server_name $DOMAIN;
    
    ssl_certificate $CERT;
    ssl_certificate_key $KEY;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # CORS 头
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
    }
}

server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}
EOF
    
    ln -sf /etc/nginx/sites-available/medroundtable /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    nginx -t
    systemctl restart nginx
    systemctl enable nginx
    
    echo ""
    echo "✅ Nginx 配置完成！"
    echo ""
    echo "🌐 HTTPS 地址: https://$DOMAIN"
    echo ""
    echo "📋 测试命令:"
    echo "curl https://$DOMAIN/health"
}

# 开放防火墙端口
echo ""
echo "🔓 开放防火墙端口..."
ufw allow 80/tcp 2>/dev/null || true
ufw allow 443/tcp 2>/dev/null || true

echo ""
echo "🎉 HTTPS 配置完成！"
