#!/bin/bash
# GitHub Pages 自动启用脚本
# 使用方法: ./enable-github-pages.sh

echo "🚀 MedRoundTable GitHub Pages 自动配置"
echo "========================================"
echo ""

# 检查是否在 Git 仓库中
if [ ! -d ".git" ]; then
    echo "❌ 错误: 当前目录不是 Git 仓库"
    echo "请确保在 medroundtable 仓库根目录运行此脚本"
    exit 1
fi

# 检查 GitHub CLI 是否安装
if ! command -v gh &> /dev/null; then
    echo "⚠️  未检测到 GitHub CLI (gh)"
    echo ""
    echo "请手动启用 GitHub Pages:"
    echo "1. 访问 https://github.com/MoKangMedical/medroundtable/settings/pages"
    echo "2. Source: Deploy from a branch"
    echo "3. Branch: main / docs"
    echo "4. 点击 Save"
    echo ""
    echo "或者安装 GitHub CLI:"
    echo "  - macOS: brew install gh"
    echo "  - Ubuntu: sudo apt install gh"
    echo "  - 其他: https://cli.github.com/"
    exit 1
fi

# 检查是否已登录
echo "🔍 检查 GitHub 登录状态..."
if ! gh auth status &> /dev/null; then
    echo "⚠️  未登录 GitHub CLI"
    echo "请运行: gh auth login"
    exit 1
fi

echo "✅ 已登录 GitHub CLI"
echo ""

# 检查仓库是否存在
echo "🔍 检查仓库..."
REPO="MoKangMedical/medroundtable"
if ! gh repo view "$REPO" &> /dev/null; then
    echo "❌ 错误: 无法访问仓库 $REPO"
    exit 1
fi

echo "✅ 仓库访问正常"
echo ""

# 检查 GitHub Pages 状态
echo "🔍 检查 GitHub Pages 状态..."
if gh api "repos/$REPO/pages" &> /dev/null; then
    echo "✅ GitHub Pages 已启用"
    URL=$(gh api "repos/$REPO/pages" --jq '.html_url' 2>/dev/null || echo "")
    if [ -n "$URL" ]; then
        echo "🌐 访问地址: $URL"
    fi
else
    echo "ℹ️  GitHub Pages 尚未启用"
    echo ""
    echo "正在创建 GitHub Actions 工作流..."
    
    # 确保工作流目录存在
    mkdir -p .github/workflows
    
    # 工作流文件已存在（由 setup.sh 创建）
    if [ -f ".github/workflows/pages.yml" ]; then
        echo "✅ 工作流文件已存在"
    else
        echo "❌ 工作流文件不存在，请检查"
        exit 1
    fi
    
    echo ""
    echo "========================================"
    echo "📋 下一步操作（请手动执行）:"
    echo "========================================"
    echo ""
    echo "由于 GitHub API 限制，Pages 需要通过网页启用:"
    echo ""
    echo "1️⃣  访问仓库设置页:"
    echo "   https://github.com/MoKangMedical/medroundtable/settings/pages"
    echo ""
    echo "2️⃣  选择部署源:"
    echo "   Source: GitHub Actions"
    echo ""
    echo "3️⃣  点击 Save 按钮"
    echo ""
    echo "4️⃣  等待 1-2 分钟后访问:"
    echo "   https://mokangmedical.github.io/medroundtable/"
    echo ""
    echo "========================================"
    echo "📝 或者使用 GitHub CLI 尝试自动启用:"
    echo "========================================"
    echo ""
    echo "gh api \"repos/MoKangMedical/medroundtable/pages\" \\"
    echo "  --method POST \\"
    echo "  --input - <<EOF"
    echo '{"source":{"branch":"main","path":"/docs"}}'
    echo "EOF"
    echo ""
fi

echo ""
echo "🔧 其他有用的命令:"
echo "  - 查看部署状态: gh workflow view pages"
echo "  - 手动触发部署: gh workflow run pages"
echo "  - 查看构建日志: gh run list --workflow=pages.yml"
echo ""

# 检查是否有未推送的更改
echo "🔍 检查未推送的更改..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  检测到未提交的更改"
    echo ""
    echo "请执行以下命令提交更改:"
    echo "  git add ."
    echo "  git commit -m 'feat: Add GitHub Pages workflow'"
    echo "  git push origin main"
    echo ""
    echo "推送后，GitHub Actions 将自动部署网站"
else
    echo "✅ 所有更改已提交"
fi

echo ""
echo "🎉 配置完成！"