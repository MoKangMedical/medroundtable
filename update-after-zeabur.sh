#!/bin/bash
# Zeabur 部署后自动更新脚本
# 用法: ./update-after-zeabur.sh <你的zeabur域名>
# 示例: ./update-after-zeabur.sh https://medroundtable.zeabur.app

if [ -z "$1" ]; then
    echo "❌ 请提供 Zeabur 域名"
    echo "用法: ./update-after-zeabur.sh <你的zeabur域名>"
    echo "示例: ./update-after-zeabur.sh https://medroundtable.zeabur.app"
    exit 1
fi

ZEABUR_URL=$1
# 移除末尾的斜杠
ZEABUR_URL=${ZEABUR_URL%/}

echo "🔄 使用域名: $ZEABUR_URL"

# 更新 secondme-manifest.json
echo "📄 更新 secondme-manifest.json..."
python3 << EOF
import json
import sys

with open('secondme-manifest.json', 'r', encoding='utf-8') as f:
    manifest = json.load(f)

# 更新 API base_url
manifest['interfaces']['api']['base_url'] = "$ZEABUR_URL"

with open('secondme-manifest.json', 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print("✅ secondme-manifest.json 已更新")
EOF

# 创建 Vercel 环境变量更新脚本
echo "📄 创建 Vercel 环境变量配置..."
cat > .env.zeabur << EOF
# Zeabur 部署后的环境变量
# 请复制这些到 Vercel: https://vercel.com/dashboard → 你的项目 → Settings → Environment Variables

NEXT_PUBLIC_API_URL=$ZEABUR_URL
EOF

echo ""
echo "✅ 所有配置已更新！"
echo ""
echo "📋 接下来你需要做的："
echo ""
echo "1. 提交更改到 GitHub:"
echo "   git add secondme-manifest.json .env.zeabur"
echo "   git commit -m 'chore: Update API URL to Zeabur'"
echo "   git push"
echo ""
echo "2. 更新 Vercel 环境变量:"
echo "   访问 https://vercel.com/dashboard"
echo "   选择 medroundtable-v2 项目"
echo "   Settings → Environment Variables"
echo "   添加: NEXT_PUBLIC_API_URL=$ZEABUR_URL"
echo ""
echo "3. 测试 API:"
echo "   curl $ZEABUR_URL/health"
echo "   curl $ZEABUR_URL/api/a2a/discovery"
echo ""
echo "🎉 完成后你的 Second Me 应用就可以提交了！"
