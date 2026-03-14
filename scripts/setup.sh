#!/bin/bash
# =============================================================================
# MedRoundTable - 一键开发环境搭建脚本
# =============================================================================
# 用法: ./scripts/setup.sh [options]
# 
# 选项:
#   -h, --help          显示帮助信息
#   -f, --force         强制重新安装（清除现有环境）
#   --with-docker       同时安装Docker环境
#   --with-node         同时安装Node.js环境
#   --backend-only      仅搭建后端环境
#   --frontend-only     仅搭建前端环境
#
# 示例:
#   ./scripts/setup.sh                    # 基础安装
#   ./scripts/setup.sh --with-docker      # 包含Docker
#   ./scripts/setup.sh --force            # 强制重新安装
# =============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 全局变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FORCE_REINSTALL=false
WITH_DOCKER=false
WITH_NODE=false
BACKEND_ONLY=false
FRONTEND_ONLY=false
PYTHON_VERSION="3.11"
NODE_VERSION="20"

# =============================================================================
# 日志函数
# =============================================================================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# =============================================================================
# 错误处理
# =============================================================================
error_exit() {
    log_error "$1"
    exit 1
}

trap 'error_exit "脚本执行中断"' INT TERM

# =============================================================================
# 解析命令行参数
# =============================================================================
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -f|--force)
                FORCE_REINSTALL=true
                shift
                ;;
            --with-docker)
                WITH_DOCKER=true
                shift
                ;;
            --with-node)
                WITH_NODE=true
                shift
                ;;
            --backend-only)
                BACKEND_ONLY=true
                shift
                ;;
            --frontend-only)
                FRONTEND_ONLY=true
                shift
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

show_help() {
    head -n 20 "$0" | tail -n 18
}

# =============================================================================
# 系统检查
# =============================================================================
check_system() {
    log_info "检查系统环境..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            DISTRO=$NAME
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macOS"
    else
        error_exit "不支持的操作系统: $OSTYPE"
    fi
    
    log_success "检测到操作系统: $DISTRO"
    
    # 检查必要命令
    local required_commands=("curl" "git")
    for cmd in "${required_commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            error_exit "未找到必要命令: $cmd"
        fi
    done
}

# =============================================================================
# Python环境安装
# =============================================================================
setup_python() {
    log_info "设置Python环境..."
    
    # 检查Python版本
    if command -v python3 &> /dev/null; then
        local current_version=$(python3 --version 2>&1 | awk '{print $2}')
        log_info "当前Python版本: $current_version"
    fi
    
    # 创建虚拟环境
    local venv_path="$PROJECT_ROOT/.venv"
    
    if [ "$FORCE_REINSTALL" = true ] && [ -d "$venv_path" ]; then
        log_warning "强制重新安装: 删除现有虚拟环境"
        rm -rf "$venv_path"
    fi
    
    if [ ! -d "$venv_path" ]; then
        log_info "创建虚拟环境..."
        python3 -m venv "$venv_path"
    else
        log_info "虚拟环境已存在"
    fi
    
    # 激活虚拟环境
    source "$venv_path/bin/activate"
    
    # 升级pip
    log_info "升级pip..."
    pip install --upgrade pip setuptools wheel
    
    # 安装依赖
    log_info "安装Python依赖..."
    pip install -r "$PROJECT_ROOT/requirements.txt"
    
    # 安装开发依赖
    log_info "安装开发依赖..."
    pip install pytest pytest-asyncio black flake8 isort mypy bandit safety
    
    log_success "Python环境配置完成"
}

# =============================================================================
# Node.js环境安装
# =============================================================================
setup_node() {
    if [ "$WITH_NODE" = false ] && [ "$FRONTEND_ONLY" = false ]; then
        return
    fi
    
    log_info "设置Node.js环境..."
    
    # 检查Node.js
    if command -v node &> /dev/null; then
        local current_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$current_version" -ge "${NODE_VERSION%%.*}" ]; then
            log_info "Node.js版本满足要求: $(node --version)"
        else
            log_warning "Node.js版本过低，建议升级到 $NODE_VERSION"
        fi
    else
        log_info "安装Node.js..."
        if [ "$OS" = "macos" ]; then
            if command -v brew &> /dev/null; then
                brew install node@$NODE_VERSION
            else
                error_exit "请先安装Homebrew"
            fi
        else
            # 使用nvm安装
            if [ ! -d "$HOME/.nvm" ]; then
                curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
                export NVM_DIR="$HOME/.nvm"
                [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
            fi
            nvm install $NODE_VERSION
            nvm use $NODE_VERSION
        fi
    fi
    
    # 安装前端依赖
    if [ -d "$PROJECT_ROOT/frontend" ]; then
        log_info "安装前端依赖..."
        cd "$PROJECT_ROOT/frontend"
        
        if [ ! -d "node_modules" ] || [ "$FORCE_REINSTALL" = true ]; then
            if [ "$FORCE_REINSTALL" = true ] && [ -d "node_modules" ]; then
                rm -rf node_modules package-lock.json
            fi
            npm install
        fi
    fi
    
    log_success "Node.js环境配置完成"
}

# =============================================================================
# Docker环境安装
# =============================================================================
setup_docker() {
    if [ "$WITH_DOCKER" = false ]; then
        return
    fi
    
    log_info "检查Docker环境..."
    
    if command -v docker &> /dev/null; then
        log_success "Docker已安装: $(docker --version)"
        
        # 检查Docker Compose
        if docker compose version &> /dev/null || docker-compose --version &> /dev/null; then
            log_success "Docker Compose可用"
        else
            log_warning "Docker Compose未安装"
        fi
    else
        log_info "Docker未安装，请参考官方文档安装:"
        log_info "https://docs.docker.com/get-docker/"
    fi
}

# =============================================================================
# 数据库初始化
# =============================================================================
init_database() {
    log_info "初始化数据库..."
    
    # 创建数据目录
    mkdir -p "$PROJECT_ROOT/data"
    
    # 如果是SQLite，数据库会自动创建
    # 如果是PostgreSQL，需要额外配置
    
    log_info "数据目录: $PROJECT_ROOT/data"
    log_success "数据库初始化完成"
}

# =============================================================================
# 配置文件设置
# =============================================================================
setup_config() {
    log_info "设置配置文件..."
    
    # 创建.env文件（如果不存在）
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        if [ -f "$PROJECT_ROOT/.env.example" ]; then
            cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
            log_info "已创建.env文件，请编辑配置"
        else
            log_warning "未找到.env.example文件"
        fi
    fi
    
    # 创建必要的目录
    mkdir -p "$PROJECT_ROOT/data"
    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/tmp"
    
    log_success "配置文件设置完成"
}

# =============================================================================
# 预提交钩子设置
# =============================================================================
setup_hooks() {
    log_info "设置Git hooks..."
    
    local hooks_dir="$PROJECT_ROOT/.git/hooks"
    
    if [ ! -d "$hooks_dir" ]; then
        log_warning "未找到Git hooks目录，跳过"
        return
    fi
    
    # 创建pre-commit钩子
    cat > "$hooks_dir/pre-commit" << 'EOF'
#!/bin/bash
# Pre-commit hook for MedRoundTable

echo "Running pre-commit checks..."

# 运行代码格式化
echo "Running black..."
black backend/ agents/ --check || {
    echo "Code not formatted. Run: black backend/ agents/"
    exit 1
}

# 运行flake8
echo "Running flake8..."
flake8 backend/ agents/ --count --select=E9,F63,F7,F82 --show-source --statistics || exit 1

echo "Pre-commit checks passed!"
EOF
    
    chmod +x "$hooks_dir/pre-commit"
    log_success "Git hooks设置完成"
}

# =============================================================================
# 验证安装
# =============================================================================
verify_installation() {
    log_info "验证安装..."
    
    local has_error=false
    
    # 检查Python
    if command -v python3 &> /dev/null; then
        log_success "✓ Python可用"
    else
        log_error "✗ Python不可用"
        has_error=true
    fi
    
    # 检查虚拟环境
    if [ -d "$PROJECT_ROOT/.venv" ]; then
        log_success "✓ 虚拟环境已创建"
    else
        log_error "✗ 虚拟环境未创建"
        has_error=true
    fi
    
    # 检查依赖安装
    if [ -f "$PROJECT_ROOT/.venv/bin/uvicorn" ]; then
        log_success "✓ Python依赖已安装"
    else
        log_error "✗ Python依赖未正确安装"
        has_error=true
    fi
    
    # 检查Node.js（如果安装了）
    if [ "$WITH_NODE" = true ] || [ "$FRONTEND_ONLY" = true ]; then
        if command -v node &> /dev/null; then
            log_success "✓ Node.js可用"
        else
            log_error "✗ Node.js不可用"
            has_error=true
        fi
    fi
    
    # 检查Docker（如果安装了）
    if [ "$WITH_DOCKER" = true ]; then
        if command -v docker &> /dev/null; then
            log_success "✓ Docker可用"
        else
            log_warning "✗ Docker不可用"
        fi
    fi
    
    if [ "$has_error" = true ]; then
        error_exit "安装验证失败"
    fi
    
    log_success "安装验证通过"
}

# =============================================================================
# 显示使用说明
# =============================================================================
show_usage() {
    echo ""
    echo "=========================================="
    echo -e "${GREEN}✅ MedRoundTable 开发环境搭建完成!${NC}"
    echo "=========================================="
    echo ""
    echo "🚀 快速开始:"
    echo ""
    echo "1. 激活虚拟环境:"
    echo "   source .venv/bin/activate"
    echo ""
    echo "2. 编辑配置文件:"
    echo "   vim .env"
    echo ""
    echo "3. 启动开发服务器:"
    echo "   ./scripts/start-dev.sh"
    echo "   或: uvicorn backend.main:app --reload"
    echo ""
    echo "4. 运行测试:"
    echo "   pytest"
    echo ""
    echo "📚 更多信息:"
    echo "   - README.md"
    echo "   - DEPLOYMENT.md"
    echo ""
    echo "🐳 Docker方式启动:"
    echo "   docker-compose up -d"
    echo ""
}

# =============================================================================
# 主函数
# =============================================================================
main() {
    echo "=========================================="
    echo "  MedRoundTable 开发环境搭建"
    echo "=========================================="
    echo ""
    
    # 解析参数
    parse_args "$@"
    
    # 切换到项目根目录
    cd "$PROJECT_ROOT"
    
    # 执行安装步骤
    check_system
    
    if [ "$FRONTEND_ONLY" = false ]; then
        setup_python
        init_database
    fi
    
    if [ "$BACKEND_ONLY" = false ]; then
        setup_node
    fi
    
    setup_docker
    setup_config
    setup_hooks
    verify_installation
    
    # 显示使用说明
    show_usage
}

# 执行主函数
main "$@"
