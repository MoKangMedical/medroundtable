#!/bin/bash
# 自动部署脚本 - 一键配置 GitHub + Vercel + Railway

echo "🚀 MedRoundTable - 自动部署脚本"
echo "=================================="
echo ""
echo "此脚本将帮助你："
echo "1. 推送代码到 GitHub"
echo "2. 部署前端到 Vercel"
echo "3. 部署后端到 Railway"
echo ""

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 项目目录
PROJECT_DIR="/root/.openclaw/workspace/medroundtable"
cd "$PROJECT_DIR"

echo -e "${YELLOW}步骤 1/4: 检查 GitHub Token${NC}"
echo "----------------------------------------"
echo "你需要一个 GitHub Personal Access Token"
echo ""
echo "生成步骤："
echo "1. 访问: https://github.com/settings/tokens/new"
echo "2. Note: MedRoundTable Deploy"
echo "3. 勾选 'repo' 权限"
echo "4. 点击 Generate token"
echo "5. 复制 token (以 ghp_ 开头)"
echo ""

# 读取 Token
read -p "请输入 GitHub Token: " GITHUB_TOKEN

if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}❌ Token 不能为空${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}步骤 2/4: 推送代码到 GitHub${NC}"
echo "----------------------------------------"

# 配置 git
git config user.name "MoKangMedical"
git config user.email "smartresearch2026@163.com"

# 移除旧的 remote
git remote remove origin 2>/dev/null || true

# 添加带 token 的 remote
git remote add origin https://MoKangMedical:${GITHUB_TOKEN}@github.com/MoKangMedical/medroundtable.git

# 添加所有文件
git add .

# 提交
git commit -m "Auto deploy: Add GitHub Actions workflow" || echo "No changes to commit"

# 推送
if git push -u origin main --force; then
    echo -e "${GREEN}✅ 代码已推送到 GitHub${NC}"
    echo "   访问: https://github.com/MoKangMedical/medroundtable"
else
    echo -e "${RED}❌ 推送失败，请检查 Token 是否正确${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}步骤 3/4: Vercel 部署配置${NC}"
echo "----------------------------------------"
echo "请按以下步骤配置 Vercel："
echo ""
echo "1. 访问: https://vercel.com/new"
echo "2. 导入 GitHub 仓库: MoKangMedical/medroundtable"
echo "3. Framework Preset: Other"
echo "4. Output Directory: frontend"
echo "5. 点击 Deploy"
echo ""
read -p "完成 Vercel 部署后按 Enter 继续..."

echo ""
echo -e "${YELLOW}步骤 4/4: Railway 部署配置${NC}"
echo "----------------------------------------"
echo "请按以下步骤配置 Railway："
echo ""
echo "1. 访问: https://railway.app/new"
echo "2. 选择 'Deploy from GitHub repo'"
echo "3. 选择: MoKangMedical/medroundtable"
echo "4. 添加环境变量:"
echo "   - SECRET_KEY: medroundtable-secret-key-2024"
echo "   - MOONSHOT_API_KEY: 使用 Railway/VPS 的环境变量，不要写入脚本"
echo "5. 点击 Deploy"
echo ""
read -p "完成 Railway 部署后按 Enter 继续..."

echo ""
echo -e "${GREEN}🎉 部署完成！${NC}"
echo "=================================="
echo ""
echo "你的永久链接："
echo "  前端: https://medroundtable.vercel.app (或分配的域名)"
echo "  后端: https://medroundtable-api.up.railway.app (或分配的域名)"
echo ""
echo "GitHub 仓库:"
echo "  https://github.com/MoKangMedical/medroundtable"
echo ""
echo "后续更新："
echo "  只需执行: git push"
echo "  即可自动部署到 Vercel + Railway"
echo ""
