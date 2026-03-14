#!/bin/bash

# =============================================================================
# MedRoundTable Zeabur 一键部署检查脚本
# =============================================================================
# 功能：
#   - 部署前检查（代码、配置、环境变量）
#   - 执行部署
#   - 部署后健康检查
#   - 日志查看
#   - 回滚功能
#
# 使用方法：
#   chmod +x zeabur-deploy.sh
#   ./zeabur-deploy.sh [command] [options]
#
# 命令：
#   check      - 部署前检查
#   deploy     - 执行部署（默认）
#   health     - 健康检查
#   logs       - 查看日志
#   rollback   - 回滚到上一版本
#   full       - 完整流程（检查+部署+验证）
#
# 示例：
#   ./zeabur-deploy.sh check                    # 仅检查
#   ./zeabur-deploy.sh deploy                   # 仅部署
#   ./zeabur-deploy.sh full                     # 完整流程
#   ./zeabur-deploy.sh health medroundtable.zeabur.app
#   ./zeabur-deploy.sh logs                     # 查看日志
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置
PROJECT_NAME="medroundtable"
DEFAULT_DOMAIN=""
GITHUB_REPO="MoKangMedical/medroundtable"
REQUIRED_ENV_VARS=(
    "PORT"
    "HOST"
    "DEBUG"
    "SECRET_KEY"
    "DATABASE_URL"
    "ALLOWED_ORIGINS"
)

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_header() {
    echo -e "\n${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"
}

# 显示使用帮助
show_help() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════╗
║           MedRoundTable Zeabur 一键部署脚本                          ║
╚══════════════════════════════════════════════════════════════════════╝

使用方法: ./zeabur-deploy.sh [命令] [选项]

命令:
  check       部署前检查（代码、配置、环境变量）
  deploy      推送到 GitHub 触发部署（默认命令）
  health      健康检查 [域名]
  logs        查看最近日志
  rollback    回滚到上一版本
  full        完整流程：检查 → 部署 → 验证
  help        显示此帮助信息

选项:
  -d, --domain <域名>    指定域名（默认从 .zeabur_domain 文件读取）
  -t, --timeout <秒>     设置超时时间（默认 300 秒）
  -v, --verbose          显示详细输出

示例:
  ./zeabur-deploy.sh check
  ./zeabur-deploy.sh deploy
  ./zeabur-deploy.sh full
  ./zeabur-deploy.sh health medroundtable.zeabur.app
  ./zeabur-deploy.sh rollback

EOF
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "未找到命令: $1"
        print_info "请安装 $1 后重试"
        return 1
    fi
    return 0
}

# 部署前检查
do_check() {
    print_header "部署前检查"
    
    local has_error=0
    
    # 1. 检查 Git
    print_info "检查 Git 环境..."
    if ! check_command git; then
        has_error=1
    else
        print_success "Git 已安装"
    fi
    
    # 2. 检查 GitHub CLI（可选）
    print_info "检查 GitHub CLI..."
    if check_command gh; then
        print_success "GitHub CLI 已安装"
        if gh auth status &>/dev/null; then
            print_success "GitHub CLI 已登录"
        else
            print_warning "GitHub CLI 未登录，部分功能受限"
        fi
    else
        print_warning "GitHub CLI 未安装（可选）"
    fi
    
    # 3. 检查 curl
    print_info "检查 curl..."
    if ! check_command curl; then
        has_error=1
    else
        print_success "curl 已安装"
    fi
    
    # 4. 检查项目目录
    print_info "检查项目结构..."
    if [ ! -f "main.py" ]; then
        print_error "未找到 main.py，请在项目根目录运行此脚本"
        has_error=1
    else
        print_success "项目结构正常"
    fi
    
    # 5. 检查 Git 仓库
    print_info "检查 Git 仓库..."
    if [ ! -d ".git" ]; then
        print_error "当前目录不是 Git 仓库"
        has_error=1
    else
        print_success "Git 仓库正常"
    fi
    
    # 6. 检查远程仓库
    print_info "检查远程仓库..."
    if ! git remote -v &>/dev/null; then
        print_error "未配置远程仓库"
        has_error=1
    else
        print_success "远程仓库已配置"
        echo "    $(git remote -v | head -1)"
    fi
    
    # 7. 检查环境变量文件
    print_info "检查环境变量文件..."
    if [ ! -f ".env.production" ]; then
        print_warning "未找到 .env.production 文件"
        print_info "请根据 ENV_SETUP_GUIDE.md 创建此文件"
    else
        print_success "找到 .env.production"
    fi
    
    # 8. 检查必需的环境变量
    print_info "检查必需的环境变量..."
    if [ -f ".env.production" ]; then
        local missing_vars=()
        for var in "${REQUIRED_ENV_VARS[@]}"; do
            if ! grep -q "^${var}=" .env.production; then
                missing_vars+=("$var")
            fi
        done
        
        if [ ${#missing_vars[@]} -eq 0 ]; then
            print_success "所有必需变量已配置"
        else
            print_error "缺少以下环境变量："
            for var in "${missing_vars[@]}"; do
                echo "    - $var"
            done
            has_error=1
        fi
    fi
    
    # 9. 检查关键文件
    print_info "检查部署文件..."
    local required_files=("Dockerfile" "zeabur.toml" "start.sh")
    local missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        print_success "所有部署文件已就绪"
    else
        print_warning "缺少以下文件（将由部署脚本自动生成）："
        for file in "${missing_files[@]}"; do
            echo "    - $file"
        done
    fi
    
    # 10. 检查未提交的更改
    print_info "检查未提交的更改..."
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        print_warning "有未提交的更改"
        echo ""
        git status -s
        echo ""
        read -p "是否自动提交更改？ (y/N): " auto_commit
        if [[ $auto_commit =~ ^[Yy]$ ]]; then
            git add .
            git commit -m "chore: auto-commit before deployment ($(date +%Y-%m-%d_%H:%M))"
            print_success "更改已提交"
        else
            print_warning "请手动提交更改后重试"
            has_error=1
        fi
    else
        print_success "没有未提交的更改"
    fi
    
    # 11. 检查域名配置
    print_info "检查域名配置..."
    if [ -f ".zeabur_domain" ]; then
        local domain=$(cat .zeabur_domain)
        print_success "域名配置: $domain"
    else
        print_warning "未找到 .zeabur_domain 文件"
        print_info "运行 ./update-domain.sh <域名> 进行配置"
    fi
    
    # 总结
    echo ""
    if [ $has_error -eq 0 ]; then
        print_success "✅ 所有检查通过，可以进行部署"
        return 0
    else
        print_error "❌ 检查未通过，请修复上述问题后重试"
        return 1
    fi
}

# 执行部署
do_deploy() {
    print_header "开始部署"
    
    # 1. 确保所有更改已提交
    print_info "检查 Git 状态..."
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        print_warning "有未提交的更改，正在自动提交..."
        git add .
        git commit -m "chore: auto-commit for deployment ($(date +%Y-%m-%d_%H:%M))"
    fi
    
    # 2. 推送代码
    print_info "推送到 GitHub..."
    if git push origin main; then
        print_success "代码已推送到 GitHub"
    else
        print_error "推送失败"
        return 1
    fi
    
    # 3. 等待部署
    print_info "等待 Zeabur 部署..."
    print_info "你可以在 https://zeabur.com/dashboard 查看部署进度"
    
    echo ""
    echo -e "${CYAN}部署已触发，请等待 2-5 分钟...${NC}"
    echo ""
    
    # 显示进度条
    local total=30
    for i in $(seq 1 $total); do
        local percent=$((i * 100 / total))
        local filled=$((i * 50 / total))
        local empty=$((50 - filled))
        
        printf "\r${BLUE}[${NC}"
        printf "%${filled}s" | tr ' ' '█'
        printf "%${empty}s" | tr ' ' '░'
        printf "${BLUE}]${NC} %3d%%" "$percent"
        
        sleep 2
    done
    echo ""
    echo ""
    
    print_success "部署流程已提交到 Zeabur"
    print_info "请访问 Zeabur Dashboard 确认部署状态"
    
    return 0
}

# 健康检查
do_health() {
    local domain="${1:-}"
    
    # 尝试从文件读取域名
    if [ -z "$domain" ] && [ -f ".zeabur_domain" ]; then
        domain=$(cat .zeabur_domain)
    fi
    
    if [ -z "$domain" ]; then
        print_error "未指定域名，请提供域名参数或配置 .zeabur_domain 文件"
        echo "用法: ./zeabur-deploy.sh health <域名>"
        return 1
    fi
    
    print_header "健康检查: $domain"
    
    local has_error=0
    local base_url="https://$domain"
    
    # 1. 基础连接检查
    print_info "检查基础连接..."
    if curl -s -o /dev/null -w "%{http_code}" "$base_url" | grep -q "200\|307"; then
        print_success "基础连接正常"
    else
        print_error "基础连接失败"
        has_error=1
    fi
    
    # 2. 健康检查端点
    print_info "检查健康检查端点..."
    local health_response=$(curl -s "$base_url/health" 2>/dev/null)
    if echo "$health_response" | grep -q "healthy"; then
        print_success "健康检查通过"
        echo "    响应: $health_response"
    else
        print_error "健康检查失败"
        has_error=1
    fi
    
    # 3. API 端点检查
    print_info "检查 A2A Discovery..."
    local discovery_response=$(curl -s "$base_url/api/a2a/discovery" 2>/dev/null)
    if echo "$discovery_response" | grep -q "agent_id"; then
        print_success "A2A Discovery 正常"
    else
        print_warning "A2A Discovery 可能未正常工作"
    fi
    
    # 4. Agent 列表检查
    print_info "检查 Agent 列表..."
    local agents_response=$(curl -s "$base_url/api/v1/agents" 2>/dev/null)
    if echo "$agents_response" | grep -q "\["; then
        print_success "Agent 列表正常"
    else
        print_warning "Agent 列表可能未正常工作"
    fi
    
    # 5. CORS 检查
    print_info "检查 CORS 配置..."
    local cors_response=$(curl -s -X OPTIONS -H "Origin: https://example.com" \
        -H "Access-Control-Request-Method: GET" \
        "$base_url/api/v1/agents" -w "\n%{http_code}" 2>/dev/null | tail -1)
    if [ "$cors_response" = "200" ] || [ "$cors_response" = "204" ]; then
        print_success "CORS 配置正常"
    else
        print_warning "CORS 检查返回: $cors_response"
    fi
    
    # 总结
    echo ""
    if [ $has_error -eq 0 ]; then
        print_success "✅ 健康检查通过"
        return 0
    else
        print_error "❌ 健康检查未完全通过"
        return 1
    fi
}

# 查看日志
do_logs() {
    print_header "查看部署日志"
    
    print_info "最近的 Git 提交记录："
    echo ""
    git log --oneline -10 --graph
    echo ""
    
    print_info "提示："
    echo "  1. 访问 https://zeabur.com/dashboard 查看实时日志"
    echo "  2. 或使用 GitHub CLI: gh run list"
    echo ""
}

# 回滚
do_rollback() {
    print_header "回滚部署"
    
    print_warning "⚠️ 即将回滚到上一版本"
    read -p "确认继续？ (y/N): " confirm
    
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        print_info "已取消回滚"
        return 0
    fi
    
    # 获取上一个提交
    local previous_commit=$(git rev-parse HEAD~1)
    local previous_message=$(git log -1 --pretty=%B HEAD~1)
    
    print_info "上一个版本: ${previous_commit:0:8}"
    print_info "提交信息: $previous_message"
    
    # 执行回滚
    print_info "执行回滚..."
    if git revert --no-commit HEAD; then
        git commit -m "revert: rollback to previous version"
        git push origin main
        print_success "回滚完成，正在重新部署..."
        print_info "请访问 Zeabur Dashboard 查看部署状态"
    else
        print_error "回滚失败"
        return 1
    fi
}

# 完整流程
do_full() {
    print_header "执行完整部署流程"
    
    # 1. 检查
    if ! do_check; then
        print_error "检查未通过，停止部署"
        return 1
    fi
    
    echo ""
    read -p "检查通过，是否继续部署？ (Y/n): " continue
    if [[ $continue =~ ^[Nn]$ ]]; then
        print_info "已取消"
        return 0
    fi
    
    # 2. 部署
    if ! do_deploy; then
        print_error "部署失败"
        return 1
    fi
    
    # 3. 等待
    print_info "等待 60 秒让部署生效..."
    sleep 60
    
    # 4. 健康检查
    local domain=""
    if [ -f ".zeabur_domain" ]; then
        domain=$(cat .zeabur_domain)
    fi
    
    if [ -n "$domain" ]; then
        do_health "$domain"
    else
        print_warning "未配置域名，跳过健康检查"
        print_info "请手动运行: ./zeabur-deploy.sh health <你的域名>"
    fi
    
    print_success "完整流程执行完毕"
}

# 主函数
main() {
    local command="${1:-full}"
    local domain=""
    
    # 解析参数
    shift || true
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--domain)
                domain="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                # 如果位置参数未被识别为选项，可能是域名
                if [ -z "$domain" ] && [[ "$1" != -* ]]; then
                    domain="$1"
                fi
                shift
                ;;
        esac
    done
    
    # 切换到项目目录
    cd "$(dirname "$0")/.." || exit 1
    
    case "$command" in
        check)
            do_check
            ;;
        deploy)
            do_deploy
            ;;
        health)
            do_health "$domain"
            ;;
        logs)
            do_logs
            ;;
        rollback)
            do_rollback
            ;;
        full)
            do_full
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
