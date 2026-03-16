#!/bin/bash
# MedRoundTable - Railway 非交互式部署
# 用于自动化部署

set -e

echo "🚀 MedRoundTable Railway 自动部署"
echo "=================================="
echo ""

# 检查 Railway Token
if [ -z "$RAILWAY_TOKEN" ]; then
    echo "❌ 错误: 请设置 RAILWAY_TOKEN 环境变量"
    echo "获取方式: https://railway.app/account/tokens"
    exit 1
fi

# 登录 Railway
echo "🔐 使用 Token 登录 Railway..."
railway login --token "$RAILWAY_TOKEN"

echo "✅ 登录成功"
echo ""

# 初始化或连接项目
echo "📁 初始化项目..."
if [ -f ".railway/config.json" ]; then
    echo "连接到现有项目..."
else
    echo "创建新项目..."
    railway init --name "medroundtable-api" || true
fi

echo ""
echo "⚙️  配置环境变量..."

# 配置环境变量
railway variables set PORT="8000"
railway variables set HOST="0.0.0.0"
railway variables set DEBUG="false"
railway variables set SECRET_KEY="0a1267066319f509476a44ea41c17798df616b97f93882b7d5e6ed88c065b475"
railway variables set DATABASE_URL="sqlite:///app/data/medroundtable.db"
railway variables set CORS_ORIGINS="https://medroundtable-v2.vercel.app,https://app.secondme.io"
railway variables set SECONDME_CLIENT_ID="19b5f08b-2256-41aa-b196-2f98491099f7"
railway variables set SECONDME_CLIENT_SECRET="f9f406e3d8dc4fe8e8363853865e1afea2957e7b0a33d75e96cbc5a22c4c20f3"
railway variables set SECONDME_REDIRECT_URI="https://medroundtable-api.up.railway.app/api/auth/callback"
railway variables set SECONDME_API_BASE="https://api.mindverse.com/gate/lab"

echo "✅ 环境变量配置完成"
echo ""

# 部署
echo "🚀 开始部署..."
railway up

echo ""
echo "🎉 部署完成！"
echo ""

# 获取域名
echo "📋 服务信息:"
railway status
railway domain

echo ""
echo "=================================="
echo "✅ 部署完成！"
echo "=================================="
