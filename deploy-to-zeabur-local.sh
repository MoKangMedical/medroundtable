#!/bin/bash
# 本地部署脚本 - 复制到你的电脑运行

echo "🚀 MedRoundTable V2.0 Zeabur部署"
echo "=================================="
echo ""

echo "📋 步骤:"
echo "1. 确保已安装Node.js"
echo "2. 克隆代码到本地"
echo "3. 安装Zeabur CLI并登录"
echo "4. 一键部署"
echo ""

read -p "按回车开始部署..."

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 请先安装Node.js: https://nodejs.org"
    exit 1
fi

# 安装Zeabur CLI
echo "📦 安装Zeabur CLI..."
npm install -g zeabur

# 登录
echo "🔑 登录Zeabur (会打开浏览器)..."
zeabur auth login

# 检查是否在项目目录
if [ ! -f "backend/main.py" ]; then
    echo "❌ 请在medroundtable项目目录运行此脚本"
    exit 1
fi

# 部署
echo "🚀 开始部署..."
zeabur deploy

echo ""
echo "✅ 部署完成!"
echo ""
echo "接下来:"
echo "1. 访问Zeabur控制台配置环境变量"
echo "2. 绑定域名"
echo "3. 开始使用!"
