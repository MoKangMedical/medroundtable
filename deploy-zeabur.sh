#!/bin/bash
# MedRoundTable Zeabur 部署脚本
# 使用方法: ./deploy-zeabur.sh

set -e

echo "🚀 MedRoundTable Zeabur 部署向导"
echo "================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查必要文件
echo "📋 检查项目文件..."

if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}❌ 错误: 未找到 Dockerfile${NC}"
    echo "请确保在项目根目录运行此脚本"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ 错误: 未找到 requirements.txt${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 项目文件检查通过${NC}"
echo ""

# 提示用户输入域名
echo "🔧 配置信息"
echo "-----------"
read -p "请输入 Zeabur 分配的域名 (例如: medroundtable.zeabur.app): " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}❌ 域名不能为空${NC}"
    exit 1
fi

echo ""
echo "📦 正在准备部署配置..."

# 创建/更新 zeabur.toml
cat > zeabur.toml << EOF
name = "medroundtable"

[build]
builder = "DOCKERFILE"
dockerfile = "Dockerfile"

[deploy]
startCommand = ""
healthCheckPath = "/health"
healthCheckPort = 8000

[env]
DATABASE_URL = { default = "sqlite:///data/medroundtable.db" }
SECRET_KEY = { default = "$(openssl rand -hex 32)" }
ALLOWED_ORIGINS = { default = "https://medroundtable-v2.vercel.app,https://${DOMAIN}" }
CORS_ORIGINS = { default = "https://medroundtable-v2.vercel.app,https://${DOMAIN}" }
SECONDME_API_BASE = { default = "https://api.mindverse.com/gate/lab" }
EOF

echo -e "${GREEN}✅ zeabur.toml 已创建${NC}"

# 创建/更新 Dockerfile（如果不存在）
if [ ! -f "Dockerfile" ]; then
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建数据目录
RUN mkdir -p data

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
    echo -e "${GREEN}✅ Dockerfile 已创建${NC}"
fi

# 创建启动脚本
cat > start.sh << 'EOF'
#!/bin/bash
# 启动脚本

echo "🚀 启动 MedRoundTable 服务..."

# 创建数据目录
mkdir -p data

# 运行数据库迁移（如果有）
# alembic upgrade head

# 启动服务
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4
EOF

chmod +x start.sh

echo -e "${GREEN}✅ 启动脚本已创建${NC}"

# 创建健康检查端点
cat > health.py << 'EOF'
"""健康检查端点"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "medroundtable",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
EOF

echo -e "${GREEN}✅ 健康检查端点已创建${NC}"
echo ""

# 生成部署摘要
echo "📊 部署配置摘要"
echo "---------------"
echo "域名: $DOMAIN"
echo "前端地址: https://medroundtable-v2.vercel.app"
echo "后端地址: https://$DOMAIN"
echo ""

# 保存域名到文件
echo "$DOMAIN" > .zeabur_domain

echo -e "${YELLOW}⚠️  重要提醒${NC}"
echo "--------------"
echo "1. 确保已将代码推送到 GitHub"
echo "2. 访问 https://zeabur.com 创建新项目"
echo "3. 导入 GitHub 仓库: MoKangMedical/medroundtable"
echo "4. 部署完成后，更新以下环境变量:"
echo ""
echo "   SECONDME_CLIENT_ID=<your_client_id>"
echo "   SECONDME_CLIENT_SECRET=<your_client_secret>"
echo "   SECONDME_REDIRECT_URI=https://${DOMAIN}/api/auth/callback"
echo ""

# 创建环境变量模板
cat > .env.zeabur << EOF
# Zeabur 环境变量配置
# 在 Zeabur Dashboard 中设置这些变量

# 数据库
DATABASE_URL=sqlite:///data/medroundtable.db

# 安全配置
SECRET_KEY=$(openssl rand -hex 32)

# CORS 配置
ALLOWED_ORIGINS=https://medroundtable-v2.vercel.app,https://${DOMAIN}
CORS_ORIGINS=https://medroundtable-v2.vercel.app,https://${DOMAIN}

# Second Me OAuth
SECONDME_API_BASE=https://api.mindverse.com/gate/lab
SECONDME_CLIENT_ID=your_client_id_here
SECONDME_CLIENT_SECRET=your_client_secret_here
SECONDME_REDIRECT_URI=https://${DOMAIN}/api/auth/callback

# AI API Keys (可选)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
DEEPSEEK_API_KEY=
EOF

echo -e "${GREEN}✅ 环境变量模板已保存到 .env.zeabur${NC}"
echo ""

# 更新 .gitignore
if ! grep -q ".zeabur_domain" .gitignore 2>/dev/null; then
    echo ".zeabur_domain" >> .gitignore
fi

if ! grep -q ".env.zeabur" .gitignore 2>/dev/null; then
    echo ".env.zeabur" >> .gitignore
fi

echo "📝 后续步骤"
echo "----------"
echo ""
echo "1. 提交更改到 GitHub:"
echo "   git add zeabur.toml Dockerfile start.sh health.py"
echo "   git commit -m \"chore: add Zeabur deployment config\""
echo "   git push origin main"
echo ""
echo "2. 访问 Zeabur 部署:"
echo "   https://zeabur.com"
echo ""
echo "3. 部署完成后运行:"
echo "   ./update-domain.sh $DOMAIN"
echo ""

echo -e "${GREEN}🎉 部署准备完成！${NC}"
