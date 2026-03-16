#!/bin/bash
# 快速部署到 GitHub Pages
# 用法: ./deploy-to-gh-pages.sh

echo "🚀 准备部署到 GitHub Pages"
echo "=========================="
echo ""

# 创建临时分支
git checkout -b gh-pages-temp

# 将 frontend 文件复制到根目录
echo "📁 复制前端文件到根目录..."
cp -r frontend/* .

# 添加所有文件
git add -A

# 提交
git commit -m "Deploy to GitHub Pages"

# 推送到 main
git push origin gh-pages-temp:main --force

# 切回 main
git checkout main

# 删除临时分支
git branch -D gh-pages-temp

echo ""
echo "✅ 部署完成！"
echo ""
echo "请访问 GitHub 设置启用 Pages:"
echo "https://github.com/MoKangMedical/medroundtable/settings/pages"
echo ""
echo "启用后访问地址:"
echo "https://mokangmedical.github.io/medroundtable/"
