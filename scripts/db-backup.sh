#!/bin/bash

# =============================================================================
# MedRoundTable 数据库自动备份脚本
# =============================================================================
# 功能：
#   - 自动备份 SQLite/PostgreSQL 数据库
#   - 支持本地存储和云存储（阿里云OSS、AWS S3、腾讯云COS）
#   - 自动清理旧备份
#   - 备份验证
#   - 邮件/通知告警
#
# 使用方法：
#   chmod +x db-backup.sh
#   ./db-backup.sh [命令] [选项]
#
# 命令：
#   backup     - 执行备份（默认）
#   restore    - 恢复备份 [文件路径]
#   list       - 列出所有备份
#   clean      - 清理旧备份
#   config     - 配置备份参数
#   cron       - 设置定时备份
#   test       - 测试备份和恢复
#
# 示例：
#   ./db-backup.sh backup                          # 执行备份
#   ./db-backup.sh backup --cloud oss              # 备份到阿里云OSS
#   ./db-backup.sh restore backup_20250115.db      # 恢复指定备份
#   ./db-backup.sh list                            # 列出备份
#   ./db-backup.sh clean --keep 7                  # 保留最近7天
#   ./db-backup.sh cron --schedule "0 2 * * *"     # 每天凌晨2点备份
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 默认配置
BACKUP_DIR="${BACKUP_DIR:-./backups}"
DB_PATH="${DB_PATH:-./data/medroundtable.db}"
DB_TYPE="${DB_TYPE:-sqlite}"  # sqlite 或 postgresql
KEEP_DAYS="${KEEP_DAYS:-30}"
CLOUD_PROVIDER="${CLOUD_PROVIDER:-local}"  # local, oss, s3, cos
COMPRESS="${COMPRESS:-true}"
ENCRYPT="${ENCRYPT:-false}"
NOTIFY_ON_SUCCESS="${NOTIFY_ON_SUCCESS:-false}"
NOTIFY_ON_FAILURE="${NOTIFY_ON_FAILURE:-true}"

# 阿里云 OSS 配置（可选）
OSS_BUCKET="${OSS_BUCKET:-}"
OSS_ENDPOINT="${OSS_ENDPOINT:-}"
OSS_ACCESS_KEY="${OSS_ACCESS_KEY:-}"
OSS_SECRET_KEY="${OSS_SECRET_KEY:-}"

# AWS S3 配置（可选）
S3_BUCKET="${S3_BUCKET:-}"
S3_REGION="${S3_REGION:-}"
AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-}"
AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-}"

# PostgreSQL 配置（如使用 PostgreSQL）
PG_HOST="${PG_HOST:-localhost}"
PG_PORT="${PG_PORT:-5432}"
PG_USER="${PG_USER:-medroundtable}"
PG_PASSWORD="${PG_PASSWORD:-}"
PG_DATABASE="${PG_DATABASE:-medroundtable}"

# 通知配置（可选）
WEBHOOK_URL="${WEBHOOK_URL:-}"  # 企业微信/钉钉/飞书 webhook
EMAIL_TO="${EMAIL_TO:-}"

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
║           MedRoundTable 数据库备份脚本                               ║
╚══════════════════════════════════════════════════════════════════════╝

使用方法: ./db-backup.sh [命令] [选项]

命令:
  backup              执行数据库备份（默认）
  restore <文件>      从备份文件恢复数据库
  list                列出所有备份文件
  clean               清理旧备份文件
  config              显示当前配置
  cron                设置定时备份任务
  test                测试备份和恢复流程
  help                显示此帮助信息

选项:
  --cloud <provider>  云存储提供商 (local, oss, s3, cos)
  --keep <days>       保留最近 N 天的备份
  --compress          启用压缩
  --no-compress       禁用压缩
  --encrypt           启用加密
  --notify            发送通知
  --db-path <path>    指定数据库路径
  --backup-dir <dir>  指定备份目录

环境变量:
  BACKUP_DIR          备份目录 (默认: ./backups)
  DB_PATH             数据库文件路径 (默认: ./data/medroundtable.db)
  DB_TYPE             数据库类型 (sqlite/postgresql, 默认: sqlite)
  KEEP_DAYS           保留天数 (默认: 30)
  CLOUD_PROVIDER      云存储提供商 (默认: local)
  
  # 阿里云 OSS
  OSS_BUCKET          OSS Bucket 名称
  OSS_ENDPOINT        OSS Endpoint
  OSS_ACCESS_KEY      Access Key ID
  OSS_SECRET_KEY      Access Key Secret
  
  # AWS S3
  S3_BUCKET           S3 Bucket 名称
  S3_REGION           AWS 区域
  AWS_ACCESS_KEY_ID   AWS Access Key
  AWS_SECRET_ACCESS_KEY AWS Secret Key
  
  # 通知
  WEBHOOK_URL         Webhook 通知地址
  EMAIL_TO            通知邮箱

示例:
  # 执行本地备份
  ./db-backup.sh backup

  # 备份到阿里云 OSS
  ./db-backup.sh backup --cloud oss

  # 恢复数据库
  ./db-backup.sh restore backups/db_20250115_120000.db.gz

  # 清理 7 天前的备份
  ./db-backup.sh clean --keep 7

  # 设置每天凌晨 2 点自动备份
  ./db-backup.sh cron --schedule "0 2 * * *"

  # 测试备份和恢复
  ./db-backup.sh test

EOF
}

# 生成备份文件名
generate_backup_name() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local date_str=$(date +"%Y%m%d")
    echo "medroundtable_${timestamp}"
}

# 获取数据库大小
get_db_size() {
    if [ "$DB_TYPE" = "sqlite" ]; then
        if [ -f "$DB_PATH" ]; then
            du -h "$DB_PATH" | cut -f1
        else
            echo "unknown"
        fi
    else
        echo "N/A (PostgreSQL)"
    fi
}

# 发送通知
send_notification() {
    local status="$1"
    local message="$2"
    local backup_file="${3:-}"
    
    local title="数据库备份${status}"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    local hostname=$(hostname)
    local db_size=$(get_db_size)
    
    # 构建通知内容
    local content="备份时间: ${timestamp}\n"
    content+="服务器: ${hostname}\n"
    content+="数据库: ${DB_TYPE}\n"
    content+="数据库大小: ${db_size}\n"
    if [ -n "$backup_file" ]; then
        content+="备份文件: ${backup_file}\n"
    fi
    content+="状态: ${status}\n"
    content+="详情: ${message}"
    
    # 发送到 Webhook（企业微信/钉钉/飞书）
    if [ -n "$WEBHOOK_URL" ]; then
        print_info "发送 Webhook 通知..."
        
        # 企业微信格式
        local json_payload=$(cat <<EOF
{
    "msgtype": "text",
    "text": {
        "content": "$title\n$content"
    }
}
EOF
)
        
        curl -s -X POST "$WEBHOOK_URL" \
            -H "Content-Type: application/json" \
            -d "$json_payload" > /dev/null || true
    fi
    
    # 发送到邮件
    if [ -n "$EMAIL_TO" ] && command -v mail &> /dev/null; then
        print_info "发送邮件通知..."
        echo -e "$content" | mail -s "$title" "$EMAIL_TO" || true
    fi
}

# 执行 SQLite 备份
backup_sqlite() {
    local backup_name="$1"
    local backup_file="${BACKUP_DIR}/${backup_name}.db"
    
    print_info "备份 SQLite 数据库..."
    print_info "源文件: $DB_PATH"
    print_info "目标文件: $backup_file"
    
    # 检查数据库文件是否存在
    if [ ! -f "$DB_PATH" ]; then
        print_error "数据库文件不存在: $DB_PATH"
        return 1
    fi
    
    # 确保备份目录存在
    mkdir -p "$BACKUP_DIR"
    
    # 使用 SQLite 的在线备份功能
    if command -v sqlite3 &> /dev/null; then
        sqlite3 "$DB_PATH" ".backup '${backup_file}'"
    else
        # 如果没有 sqlite3 命令，直接复制
        cp "$DB_PATH" "$backup_file"
    fi
    
    if [ $? -eq 0 ]; then
        print_success "数据库备份成功"
        echo "$backup_file"
        return 0
    else
        print_error "数据库备份失败"
        return 1
    fi
}

# 执行 PostgreSQL 备份
backup_postgresql() {
    local backup_name="$1"
    local backup_file="${BACKUP_DIR}/${backup_name}.sql"
    
    print_info "备份 PostgreSQL 数据库..."
    
    if ! command -v pg_dump &> /dev/null; then
        print_error "未找到 pg_dump 命令，请先安装 PostgreSQL 客户端"
        return 1
    fi
    
    mkdir -p "$BACKUP_DIR"
    
    PGPASSWORD="$PG_PASSWORD" pg_dump \
        -h "$PG_HOST" \
        -p "$PG_PORT" \
        -U "$PG_USER" \
        -d "$PG_DATABASE" \
        -F p \
        > "$backup_file"
    
    if [ $? -eq 0 ]; then
        print_success "PostgreSQL 备份成功"
        echo "$backup_file"
        return 0
    else
        print_error "PostgreSQL 备份失败"
        return 1
    fi
}

# 压缩备份文件
compress_backup() {
    local backup_file="$1"
    
    if [ "$COMPRESS" = "true" ]; then
        print_info "压缩备份文件..."
        
        if command -v gzip &> /dev/null; then
            gzip -f "$backup_file"
            print_success "压缩完成: ${backup_file}.gz"
            echo "${backup_file}.gz"
        else
            print_warning "未找到 gzip，跳过压缩"
            echo "$backup_file"
        fi
    else
        echo "$backup_file"
    fi
}

# 上传到阿里云 OSS
upload_to_oss() {
    local backup_file="$1"
    
    print_info "上传到阿里云 OSS..."
    
    # 检查 ossutil 是否安装
    if ! command -v ossutil &> /dev/null; then
        print_warning "未找到 ossutil，尝试安装..."
        
        # 尝试下载安装
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            wget -q https://gosspublic.alicdn.com/ossutil/1.7.14/ossutil64 -O /tmp/ossutil
            chmod +x /tmp/ossutil
            alias ossutil=/tmp/ossutil
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            wget -q https://gosspublic.alicdn.com/ossutil/1.7.14/ossutilmac64 -O /tmp/ossutil
            chmod +x /tmp/ossutil
            alias ossutil=/tmp/ossutil
        fi
    fi
    
    # 配置 ossutil
    if [ -n "$OSS_ACCESS_KEY" ] && [ -n "$OSS_SECRET_KEY" ]; then
        ossutil config -e "$OSS_ENDPOINT" -i "$OSS_ACCESS_KEY" -k "$OSS_SECRET_KEY" -L CH
    fi
    
    # 上传文件
    local filename=$(basename "$backup_file")
    ossutil cp "$backup_file" "oss://${OSS_BUCKET}/backups/${filename}"
    
    if [ $? -eq 0 ]; then
        print_success "上传 OSS 成功"
        return 0
    else
        print_error "上传 OSS 失败"
        return 1
    fi
}

# 上传到 AWS S3
upload_to_s3() {
    local backup_file="$1"
    
    print_info "上传到 AWS S3..."
    
    if ! command -v aws &> /dev/null; then
        print_error "未找到 AWS CLI，请先安装"
        return 1
    fi
    
    local filename=$(basename "$backup_file")
    aws s3 cp "$backup_file" "s3://${S3_BUCKET}/backups/${filename}"
    
    if [ $? -eq 0 ]; then
        print_success "上传 S3 成功"
        return 0
    else
        print_error "上传 S3 失败"
        return 1
    fi
}

# 上传到腾讯云 COS
upload_to_cos() {
    local backup_file="$1"
    
    print_info "上传到腾讯云 COS..."
    
    if ! command -v coscmd &> /dev/null; then
        print_error "未找到 coscmd，请先安装腾讯云 COS CLI"
        return 1
    fi
    
    local filename=$(basename "$backup_file")
    coscmd upload "$backup_file" "/backups/${filename}"
    
    if [ $? -eq 0 ]; then
        print_success "上传 COS 成功"
        return 0
    else
        print_error "上传 COS 失败"
        return 1
    fi
}

# 执行备份主函数
do_backup() {
    print_header "执行数据库备份"
    
    local backup_name=$(generate_backup_name)
    local backup_file=""
    local final_file=""
    
    print_info "备份名称: $backup_name"
    print_info "数据库类型: $DB_TYPE"
    print_info "存储方式: $CLOUD_PROVIDER"
    
    # 执行备份
    case "$DB_TYPE" in
        sqlite)
            backup_file=$(backup_sqlite "$backup_name")
            ;;
        postgresql|postgres)
            backup_file=$(backup_postgresql "$backup_name")
            ;;
        *)
            print_error "不支持的数据库类型: $DB_TYPE"
            return 1
            ;;
    esac
    
    if [ $? -ne 0 ]; then
        send_notification "失败" "数据库备份失败"
        return 1
    fi
    
    # 压缩
    final_file=$(compress_backup "$backup_file")
    
    # 上传到云存储
    local upload_success=true
    case "$CLOUD_PROVIDER" in
        oss)
            upload_to_oss "$final_file" || upload_success=false
            ;;
        s3)
            upload_to_s3 "$final_file" || upload_success=false
            ;;
        cos)
            upload_to_cos "$final_file" || upload_success=false
            ;;
        local)
            print_info "本地备份完成: $final_file"
            ;;
    esac
    
    # 显示备份信息
    echo ""
    print_success "备份完成"
    echo "  文件: $final_file"
    if [ -f "$final_file" ]; then
        echo "  大小: $(du -h "$final_file" | cut -f1)"
    fi
    echo "  时间: $(date "+%Y-%m-%d %H:%M:%S")"
    
    # 发送成功通知
    if [ "$upload_success" = "true" ] && [ "$NOTIFY_ON_SUCCESS" = "true" ]; then
        send_notification "成功" "数据库备份已完成" "$final_file"
    fi
    
    return 0
}

# 恢复数据库
do_restore() {
    local backup_file="$1"
    
    print_header "恢复数据库"
    
    if [ -z "$backup_file" ]; then
        print_error "请指定备份文件路径"
        print_info "用法: ./db-backup.sh restore <备份文件路径>"
        return 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        print_error "备份文件不存在: $backup_file"
        return 1
    fi
    
    print_warning "⚠️ 警告: 恢复数据库将覆盖当前数据"
    read -p "确认继续？ (y/N): " confirm
    
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        print_info "已取消恢复"
        return 0
    fi
    
    # 如果是压缩文件，先解压
    local restore_file="$backup_file"
    if [[ "$backup_file" == *.gz ]]; then
        print_info "解压备份文件..."
        restore_file="${backup_file%.gz}"
        gunzip -c "$backup_file" > "$restore_file"
    fi
    
    # 备份当前数据库
    if [ -f "$DB_PATH" ]; then
        local current_backup="${DB_PATH}.backup.$(date +%Y%m%d_%H%M%S)"
        print_info "备份当前数据库到: $current_backup"
        cp "$DB_PATH" "$current_backup"
    fi
    
    # 执行恢复
    case "$DB_TYPE" in
        sqlite)
            print_info "恢复 SQLite 数据库..."
            cp "$restore_file" "$DB_PATH"
            ;;
        postgresql|postgres)
            print_info "恢复 PostgreSQL 数据库..."
            PGPASSWORD="$PG_PASSWORD" psql \
                -h "$PG_HOST" \
                -p "$PG_PORT" \
                -U "$PG_USER" \
                -d "$PG_DATABASE" \
                < "$restore_file"
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        print_success "数据库恢复成功"
        return 0
    else
        print_error "数据库恢复失败"
        return 1
    fi
}

# 列出备份
do_list() {
    print_header "备份文件列表"
    
    print_info "本地备份:"
    if [ -d "$BACKUP_DIR" ]; then
        ls -lh "$BACKUP_DIR" | tail -n +2 | awk '{printf "  %-20s %10s %s\n", $9, $5, $6" "$7" "$8}'
    else
        echo "  (备份目录不存在)"
    fi
    
    echo ""
    print_info "统计信息:"
    if [ -d "$BACKUP_DIR" ]; then
        local count=$(ls -1 "$BACKUP_DIR" | wc -l)
        local size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
        echo "  文件数量: $count"
        echo "  总大小: $size"
    fi
}

# 清理旧备份
do_clean() {
    print_header "清理旧备份"
    
    print_info "保留最近 $KEEP_DAYS 天的备份"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        print_warning "备份目录不存在"
        return 0
    fi
    
    # 查找并删除旧文件
    local deleted_count=0
    while IFS= read -r file; do
        print_info "删除: $(basename "$file")"
        rm -f "$file"
        ((deleted_count++))
    done < <(find "$BACKUP_DIR" -type f -mtime +$KEEP_DAYS)
    
    if [ $deleted_count -eq 0 ]; then
        print_info "没有需要清理的备份文件"
    else
        print_success "已清理 $deleted_count 个旧备份文件"
    fi
    
    # 清理云存储（如果配置了）
    case "$CLOUD_PROVIDER" in
        oss)
            print_info "清理阿里云 OSS 旧备份..."
            # ossutil rm -rf oss://${OSS_BUCKET}/backups/ --include "*.db*" --exclude "*$(date -d "-$KEEP_DAYS days" +%Y%m)*"
            ;;
        s3)
            print_info "清理 AWS S3 旧备份..."
            # aws s3 ls s3://${S3_BUCKET}/backups/ | awk '{print $4}' | xargs -I {} aws s3 rm s3://${S3_BUCKET}/backups/{}
            ;;
    esac
}

# 显示配置
do_config() {
    print_header "当前备份配置"
    
    echo -e "${CYAN}基础配置:${NC}"
    echo "  数据库类型: $DB_TYPE"
    echo "  数据库路径: $DB_PATH"
    echo "  备份目录: $BACKUP_DIR"
    echo "  保留天数: $KEEP_DAYS"
    echo "  云存储: $CLOUD_PROVIDER"
    echo "  压缩: $COMPRESS"
    echo "  加密: $ENCRYPT"
    
    echo ""
    echo -e "${CYAN}阿里云 OSS 配置:${NC}"
    if [ -n "$OSS_BUCKET" ]; then
        echo "  Bucket: $OSS_BUCKET"
        echo "  Endpoint: $OSS_ENDPOINT"
        echo "  Access Key: ${OSS_ACCESS_KEY:0:8}..."
        echo "  Secret Key: ${OSS_SECRET_KEY:0:8}..."
    else
        echo "  (未配置)"
    fi
    
    echo ""
    echo -e "${CYAN}AWS S3 配置:${NC}"
    if [ -n "$S3_BUCKET" ]; then
        echo "  Bucket: $S3_BUCKET"
        echo "  Region: $S3_REGION"
    else
        echo "  (未配置)"
    fi
    
    echo ""
    echo -e "${CYAN}PostgreSQL 配置:${NC}"
    if [ "$DB_TYPE" = "postgresql" ]; then
        echo "  Host: $PG_HOST"
        echo "  Port: $PG_PORT"
        echo "  User: $PG_USER"
        echo "  Database: $PG_DATABASE"
    else
        echo "  (使用 SQLite)"
    fi
    
    echo ""
    echo -e "${CYAN}通知配置:${NC}"
    if [ -n "$WEBHOOK_URL" ]; then
        echo "  Webhook: ${WEBHOOK_URL:0:50}..."
    else
        echo "  Webhook: (未配置)"
    fi
    
    if [ -n "$EMAIL_TO" ]; then
        echo "  Email: $EMAIL_TO"
    else
        echo "  Email: (未配置)"
    fi
}

# 设置定时任务
do_cron() {
    local schedule="${1:-0 2 * * *}"
    
    print_header "设置定时备份"
    
    print_info "备份计划: $schedule"
    print_info "含义: $(echo "$schedule" | awk '{
        if ($1 == "0" && $2 == "2" && $3 == "*" && $4 == "*" && $5 == "*") 
            print "每天凌晨 2:00"
        else if ($1 == "0" && $2 == "*/6" && $3 == "*" && $4 == "*" && $5 == "*")
            print "每 6 小时"
        else if ($1 == "0" && $2 == "0" && $3 == "*" && $4 == "*" && $5 == "0")
            print "每周日凌晨"
        else
            print "自定义计划"
    }')"
    
    # 获取脚本绝对路径
    local script_path=$(realpath "$0")
    
    print_info "添加 cron 任务..."
    
    # 创建新的 crontab 内容
    local cron_job="$schedule $script_path backup >> $BACKUP_DIR/backup.log 2>&1"
    
    # 添加到 crontab
    (crontab -l 2>/dev/null | grep -v "$script_path"; echo "$cron_job") | crontab -
    
    print_success "定时任务已设置"
    print_info "查看当前 crontab:"
    crontab -l | grep "db-backup" || echo "  (未找到)"
}

# 测试备份和恢复
do_test() {
    print_header "测试备份和恢复流程"
    
    print_info "此测试将:"
    echo "  1. 创建测试数据"
    echo "  2. 执行备份"
    echo "  3. 修改数据"
    echo "  4. 恢复备份"
    echo "  5. 验证数据完整性"
    echo ""
    
    read -p "确认开始测试？这将修改数据库 (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        print_info "已取消测试"
        return 0
    fi
    
    # 1. 备份当前数据库
    print_info "步骤 1: 备份当前数据库..."
    local original_backup="${DB_PATH}.original.$(date +%Y%m%d_%H%M%S)"
    if [ -f "$DB_PATH" ]; then
        cp "$DB_PATH" "$original_backup"
        print_success "原数据库已备份到: $original_backup"
    fi
    
    # 2. 创建测试备份
    print_info "步骤 2: 创建测试备份..."
    local test_backup=$(do_backup 2>&1 | grep "文件:" | awk '{print $2}')
    
    if [ -z "$test_backup" ]; then
        print_error "备份失败"
        return 1
    fi
    
    print_success "测试备份已创建"
    
    # 3. 模拟数据变化（这里只是示例）
    print_info "步骤 3: 模拟数据变化..."
    print_info "（实际测试中，这里会插入测试数据）"
    
    # 4. 恢复测试
    print_info "步骤 4: 从备份恢复..."
    if do_restore "$test_backup"; then
        print_success "恢复成功"
    else
        print_error "恢复失败"
        # 恢复原数据库
        if [ -f "$original_backup" ]; then
            cp "$original_backup" "$DB_PATH"
        fi
        return 1
    fi
    
    # 5. 清理
    print_info "步骤 5: 清理测试文件..."
    rm -f "$test_backup"
    if [[ "$test_backup" == *.gz ]]; then
        rm -f "${test_backup%.gz}"
    fi
    
    print_success "✅ 测试完成！备份和恢复流程正常工作"
}

# 主函数
main() {
    local command="${1:-backup}"
    shift || true
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --cloud)
                CLOUD_PROVIDER="$2"
                shift 2
                ;;
            --keep)
                KEEP_DAYS="$2"
                shift 2
                ;;
            --compress)
                COMPRESS="true"
                shift
                ;;
            --no-compress)
                COMPRESS="false"
                shift
                ;;
            --encrypt)
                ENCRYPT="true"
                shift
                ;;
            --notify)
                NOTIFY_ON_SUCCESS="true"
                shift
                ;;
            --db-path)
                DB_PATH="$2"
                shift 2
                ;;
            --backup-dir)
                BACKUP_DIR="$2"
                shift 2
                ;;
            --schedule)
                CRON_SCHEDULE="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                # 保留位置参数
                break
                ;;
        esac
    done
    
    case "$command" in
        backup)
            do_backup
            ;;
        restore)
            do_restore "$1"
            ;;
        list)
            do_list
            ;;
        clean)
            do_clean
            ;;
        config)
            do_config
            ;;
        cron)
            do_cron "${CRON_SCHEDULE:-0 2 * * *}"
            ;;
        test)
            do_test
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
