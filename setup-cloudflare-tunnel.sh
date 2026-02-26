#!/bin/bash
# Cloudflare Tunnel 一键配置脚本
# 为 MedRoundTable 后端添加 HTTPS 域名

set -e

echo "🚀 MedRoundTable Cloudflare Tunnel 配置"
echo "========================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查 cloudflared
if ! command -v cloudflared &> /dev/null; then
    echo -e "${BLUE}📦 安装 cloudflared...${NC}"
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    dpkg -i cloudflared-linux-amd64.deb
    rm cloudflared-linux-amd64.deb
    echo -e "${GREEN}✅ cloudflared 安装完成${NC}"
fi

# 检查是否已登录
echo ""
echo -e "${BLUE}🔍 检查 Cloudflare 登录状态...${NC}"
if ! cloudflared tunnel list &> /dev/null; then
    echo -e "${YELLOW}⚠️  需要登录 Cloudflare${NC}"
    echo ""
    echo "请运行以下命令登录："
    echo -e "${GREEN}cloudflared tunnel login${NC}"
    echo ""
    echo "这会生成一个认证链接，请在浏览器中打开并授权。"
    echo "完成后重新运行此脚本。"
    exit 1
fi

echo -e "${GREEN}✅ 已登录 Cloudflare${NC}"

# 创建隧道
echo ""
echo -e "${BLUE}🚇 创建隧道...${NC}"
TUNNEL_NAME="medroundtable-api"

if cloudflared tunnel list | grep -q "$TUNNEL_NAME"; then
    echo "隧道已存在，使用现有隧道"
    TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
else
    echo "创建新隧道: $TUNNEL_NAME"
    cloudflared tunnel create "$TUNNEL_NAME"
    TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
fi

echo -e "${GREEN}✅ 隧道 ID: $TUNNEL_ID${NC}"

# 创建配置文件
echo ""
echo -e "${BLUE}⚙️  创建配置文件...${NC}"

mkdir -p ~/.cloudflared

cat > ~/.cloudflared/config.yml << EOF
tunnel: $TUNNEL_ID
credentials-file: /root/.cloudflared/$TUNNEL_ID.json

# 入口规则
ingress:
  # MedRoundTable API
  - hostname: api.medroundtable.com
    service: http://localhost:8001
  
  # 也可以自定义域名
  # - hostname: your-domain.com
  #   service: http://localhost:8001
  
  # 默认拒绝
  - service: http_status:404
EOF

echo -e "${GREEN}✅ 配置文件已创建: ~/.cloudflared/config.yml${NC}"

# 创建 DNS 记录
echo ""
echo -e "${BLUE}🌐 创建 DNS 记录...${NC}"
echo "请选择你的域名（从列表中选择）:"
cloudflared tunnel list | grep -E '^[0-9a-f]{8}' | head -5

echo ""
read -p "请输入你的域名 (例如: example.com): " DOMAIN

if [ -n "$DOMAIN" ]; then
    cloudflared tunnel route dns "$TUNNEL_NAME" "api.$DOMAIN"
    echo -e "${GREEN}✅ DNS 记录已创建: api.$DOMAIN${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  重要提示:${NC}"
    echo "请在你的域名 DNS 管理中添加 CNAME 记录:"
    echo "  名称: api"
    echo "  目标: $TUNNEL_ID.cfargotunnel.com"
fi

# 测试隧道
echo ""
echo -e "${BLUE}🧪 测试隧道...${NC}"
echo "启动隧道（按 Ctrl+C 停止）..."
echo ""
echo -e "${YELLOW}测试命令:${NC}"
echo "curl https://api.$DOMAIN/health"
echo ""

cloudflared tunnel run "$TUNNEL_NAME"
