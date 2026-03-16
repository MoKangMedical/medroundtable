#!/bin/bash
# Zeabur 自动部署脚本

echo "🚀 Zeabur 自动部署"
echo "=================="
echo ""

# 检查是否安装zeabur CLI
if ! command -v zeabur &> /dev/null; then
    echo "📦 安装 Zeabur CLI..."
    npm install -g zeabur
fi

# 登录
echo "🔑 请登录 Zeabur..."
zeabur login

# 进入项目目录
cd /root/.openclaw/workspace/medroundtable

# 创建项目
echo "📁 创建项目..."
zeabur project create medroundtable-v2

# 部署
echo "🚀 开始部署..."
zeabur deploy

echo ""
echo "✅ 部署完成!"
echo "访问: https://medroundtable-v2.zeabur.app"
