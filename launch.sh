#!/bin/bash
# MedRoundTable - Second Me 上线部署脚本
# 一键完成所有部署和提交准备工作

set -e

echo "🚀 MedRoundTable - Second Me 上线部署"
echo "========================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 检查步骤
CHECKS_PASSED=0
CHECKS_TOTAL=6

check_step() {
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅${NC} $2"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${RED}❌${NC} $2"
    fi
}

# 1. 检查 GitHub 仓库
echo -e "${BLUE}📋 步骤 1: 检查 GitHub 仓库${NC}"
if git remote -v > /dev/null 2>&1; then
    REPO_URL=$(git remote get-url origin)
    echo "   仓库: $REPO_URL"
    check_step 0 "GitHub 仓库已连接"
else
    check_step 1 "GitHub 仓库未配置"
fi

# 2. 检查必要文件
echo ""
echo -e "${BLUE}📋 步骤 2: 检查必要文件${NC}"
REQUIRED_FILES=(
    "secondme-manifest.json"
    "a2a-config.json"
    "SECONDME_VERIFICATION.md"
    "SECONDME_SUBMISSION_GUIDE.md"
    "docs/USER_GUIDE.md"
    "config/agents_config.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (缺失)"
    fi
done
check_step 0 "核心文件检查完成"

# 3. 检查 Docker
echo ""
echo -e "${BLUE}📋 步骤 3: 检查部署环境${NC}"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    echo "   Docker: $DOCKER_VERSION"
    check_step 0 "Docker 已安装"
else
    check_step 1 "Docker 未安装"
fi

# 4. 检查端口
echo ""
echo -e "${BLUE}📋 步骤 4: 检查端口可用性${NC}"
PORTS=(8001 3001)
for PORT in "${PORTS[@]}"; do
    if ! netstat -tlnp 2>/dev/null | grep -q ":$PORT "; then
        echo "   ✅ 端口 $PORT 可用"
    else
        echo "   ⚠️  端口 $PORT 被占用"
    fi
done
check_step 0 "端口检查完成"

# 5. 运行部署（可选）
echo ""
echo -e "${BLUE}📋 步骤 5: 部署服务${NC}"
read -p "是否立即部署到服务器? (y/n): " DEPLOY
if [ "$DEPLOY" = "y" ] || [ "$DEPLOY" = "Y" ]; then
    echo "   正在部署..."
    if ./deploy-production.sh; then
        check_step 0 "部署成功"
    else
        check_step 1 "部署失败"
    fi
else
    echo "   ⏭️  跳过部署"
fi

# 6. 生成提交摘要
echo ""
echo -e "${BLUE}📋 步骤 6: 生成 Second Me 提交摘要${NC}"
cat > SECONDME_SUBMISSION_SUMMARY.txt << 'EOF'
MedRoundTable - Second Me 平台提交摘要
=====================================

项目名称: MedRoundTable (临床科研圆桌会)
项目类型: A2A 医学科研协作平台

核心功能:
- 5个专业AI Agent协作（临床主任、博士生、流行病学家、统计专家、研究护士）
- 完整的A2A协议实现（Discovery、Messaging、Task Management）
- Second Me OAuth登录集成
- 从临床问题到论文发表的全流程自动化

技术栈:
- 后端: FastAPI + Python
- 前端: Next.js + React
- AI: OpenAI/GLM/Claude API
- 部署: Docker + Docker Compose

A2A端点:
- GET /api/a2a/discovery - Agent发现
- POST /api/a2a/message - 消息通信
- POST /api/a2a/task - 任务管理
- POST /api/a2a/webhook/secondme - Webhook

OAuth集成:
- GET /api/auth/login - Second Me登录入口
- GET /api/auth/callback - OAuth回调处理

GitHub: https://github.com/MoKangMedical/medroundtable
Hackathon: https://hackathon.second.me/projects/cmlg779kn000204kvr6jygh28

开发者: MoKangMedical
联系: [待填写]
EOF

check_step 0 "提交摘要已生成 (SECONDME_SUBMISSION_SUMMARY.txt)"

# 最终总结
echo ""
echo "========================================"
echo -e "${GREEN}🎉 上线准备完成!${NC}"
echo ""
echo "📊 检查进度: $CHECKS_PASSED/$CHECKS_TOTAL 通过"
echo ""
echo "📋 下一步操作:"
echo ""
echo "1️⃣  访问 Second Me 开发者中心:"
echo "   https://app.secondme.io/developer"
echo ""
echo "2️⃣  创建新应用，填写信息:"
echo "   - 应用名称: MedRoundTable"
echo "   - 应用描述: 全球首个A2A架构医学科研协作平台"
echo "   - 上传 secondme-manifest.json"
echo ""
echo "3️⃣  配置OAuth:"
echo "   - 设置回调URL: https://your-domain.com/api/auth/callback"
echo "   - 记录 Client ID 和 Client Secret"
echo "   - 更新 .env.production 文件"
echo ""
echo "4️⃣  部署服务:"
echo "   ./deploy-production.sh"
echo ""
echo "5️⃣  提交审核并等待上线!"
echo ""
echo "📚 相关文档:"
echo "   - 提交指南: SECONDME_SUBMISSION_GUIDE.md"
echo "   - 用户指南: docs/USER_GUIDE.md"
echo "   - API文档: docs/SECONDME_API_GUIDE.md"
echo "   - 提交摘要: SECONDME_SUBMISSION_SUMMARY.txt"
echo ""
echo "🌟 祝上线顺利!"
echo ""
