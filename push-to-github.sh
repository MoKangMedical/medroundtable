#!/bin/bash
# GitHub 推送脚本

echo "🚀 推送到 GitHub"
echo "================"

# 配置 Token
TOKEN="$1"

if [ -z "$TOKEN" ]; then
    echo "❌ 请提供 GitHub Token"
    echo "使用方法: ./push-to-github.sh YOUR_TOKEN"
    exit 1
fi

cd /root/.openclaw/workspace/medroundtable

# 移除旧的 remote
git remote remove origin 2>/dev/null || true

# 添加带 token 的 remote
git remote add origin https://MoKangMedical:${TOKEN}@github.com/MoKangMedical/medroundtable.git

# 推送
echo "正在推送代码..."
git branch -M main
git push -u origin main --force

echo ""
echo "✅ 推送完成！"
echo "访问: https://github.com/MoKangMedical/medroundtable"
